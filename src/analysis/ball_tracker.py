"""
BallTracker - 卓球ボールトラッキングモジュール

卓球ボール（オレンジ/白）を追跡し、以下のデータを抽出:
- ボールの位置（各フレーム）
- ボールの速度
- ラリーの検出（ボールが往復する回数）
- 打球タイミングの検出

注意: 卓球ボールは小さく高速なため、一般的なカメラ（30fps）では
追跡精度に限界があります。本モジュールは補助的な情報として使用し、
主要な分析はLLMによる定性分析に依存します。
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass
class BallPosition:
    """ボールの位置データ"""
    frame_number: int
    timestamp_sec: float
    x: float  # 正規化座標 (0-1)
    y: float  # 正規化座標 (0-1)
    confidence: float  # 検出信頼度


@dataclass
class RallyEvent:
    """ラリーイベント"""
    start_time: float
    end_time: float
    duration: float
    ball_crosses: int  # ボールがネットを横切った回数


class BallTracker:
    """
    卓球ボールトラッキング
    
    HSV色空間でオレンジ/白のボールを検出し、
    輪郭検出で位置を特定します。
    """
    
    # オレンジボールのHSV範囲
    ORANGE_LOWER = np.array([5, 100, 100])
    ORANGE_UPPER = np.array([25, 255, 255])
    
    # 白ボールのHSV範囲
    WHITE_LOWER = np.array([0, 0, 200])
    WHITE_UPPER = np.array([180, 30, 255])
    
    def __init__(self, video_path: str, sample_rate: int = 2):
        """
        Args:
            video_path: 動画ファイルのパス
            sample_rate: 何フレームごとに分析するか（ボールは高速なので低い値推奨）
        """
        self.video_path = Path(video_path)
        self.sample_rate = sample_rate
        
        # 結果格納用
        self.ball_positions: List[BallPosition] = []
        self.rally_events: List[RallyEvent] = []
        
        # 動画情報
        self.fps: float = 0
        self.total_frames: int = 0
        self.frame_width: int = 0
        self.frame_height: int = 0
        
        # ボールの色（自動検出または指定）
        self.ball_color: str = "auto"  # "orange", "white", "auto"
        
    def run_tracking(self, verbose: bool = False) -> Dict:
        """
        ボールトラッキングを実行
        
        Returns:
            トラッキング結果の辞書
        """
        if verbose:
            print(f"[BallTracker] 動画を読み込み中: {self.video_path}")
        
        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            raise ValueError(f"動画を開けません: {self.video_path}")
        
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        if verbose:
            print(f"[BallTracker] FPS: {self.fps:.1f}, 解像度: {self.frame_width}x{self.frame_height}")
        
        # 最初の数フレームでボールの色を自動検出
        if self.ball_color == "auto":
            self.ball_color = self._detect_ball_color(cap)
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 先頭に戻す
            if verbose:
                print(f"[BallTracker] ボールの色を検出: {self.ball_color}")
        
        # フレームごとに処理
        frame_number = 0
        detected_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_number % self.sample_rate == 0:
                timestamp_sec = frame_number / self.fps if self.fps > 0 else 0
                
                # ボール検出
                ball_pos = self._detect_ball(frame, frame_number, timestamp_sec)
                if ball_pos:
                    self.ball_positions.append(ball_pos)
                    detected_count += 1
                
                if verbose and frame_number % 100 == 0:
                    progress = (frame_number / self.total_frames) * 100
                    print(f"[BallTracker] 進捗: {progress:.1f}%")
            
            frame_number += 1
        
        cap.release()
        
        if verbose:
            detection_rate = detected_count / (self.total_frames / self.sample_rate) * 100
            print(f"[BallTracker] 検出完了: {detected_count}フレーム ({detection_rate:.1f}%)")
        
        # ラリー検出
        self._detect_rallies()
        
        return self._compile_results()
    
    def _detect_ball_color(self, cap: cv2.VideoCapture, sample_frames: int = 30) -> str:
        """最初の数フレームからボールの色を自動検出"""
        orange_count = 0
        white_count = 0
        
        for _ in range(sample_frames):
            ret, frame = cap.read()
            if not ret:
                break
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # オレンジマスク
            orange_mask = cv2.inRange(hsv, self.ORANGE_LOWER, self.ORANGE_UPPER)
            orange_contours, _ = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 白マスク
            white_mask = cv2.inRange(hsv, self.WHITE_LOWER, self.WHITE_UPPER)
            white_contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # ボールサイズの輪郭をカウント
            for cnt in orange_contours:
                area = cv2.contourArea(cnt)
                if 50 < area < 5000:  # ボールらしいサイズ
                    orange_count += 1
            
            for cnt in white_contours:
                area = cv2.contourArea(cnt)
                if 50 < area < 5000:
                    white_count += 1
        
        return "orange" if orange_count >= white_count else "white"
    
    def _detect_ball(self, frame: np.ndarray, frame_number: int, timestamp_sec: float) -> Optional[BallPosition]:
        """1フレームでボールを検出"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 色に応じたマスクを作成
        if self.ball_color == "orange":
            mask = cv2.inRange(hsv, self.ORANGE_LOWER, self.ORANGE_UPPER)
        else:
            mask = cv2.inRange(hsv, self.WHITE_LOWER, self.WHITE_UPPER)
        
        # ノイズ除去
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # 輪郭検出
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # ボールらしい輪郭を探す
        best_candidate = None
        best_score = 0
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            
            # サイズフィルタ
            if area < 30 or area > 10000:
                continue
            
            # 円形度を計算
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * area / (perimeter ** 2)
            
            # 円形度が高いほどボールらしい
            if circularity > 0.5:
                score = circularity * area
                if score > best_score:
                    best_score = score
                    best_candidate = cnt
        
        if best_candidate is None:
            return None
        
        # 重心を計算
        M = cv2.moments(best_candidate)
        if M["m00"] == 0:
            return None
        
        cx = M["m10"] / M["m00"]
        cy = M["m01"] / M["m00"]
        
        # 正規化座標に変換
        x_norm = cx / self.frame_width
        y_norm = cy / self.frame_height
        
        # 信頼度（円形度）
        area = cv2.contourArea(best_candidate)
        perimeter = cv2.arcLength(best_candidate, True)
        confidence = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
        
        return BallPosition(
            frame_number=frame_number,
            timestamp_sec=timestamp_sec,
            x=x_norm,
            y=y_norm,
            confidence=confidence
        )
    
    def _detect_rallies(self):
        """ラリーを検出（ボールのX座標の変化から）"""
        if len(self.ball_positions) < 10:
            return
        
        # ボールがネット（画面中央）を横切るタイミングを検出
        center_x = 0.5
        crossings = []
        
        for i in range(1, len(self.ball_positions)):
            prev = self.ball_positions[i-1]
            curr = self.ball_positions[i]
            
            # 中央を横切ったか
            if (prev.x < center_x and curr.x >= center_x) or (prev.x >= center_x and curr.x < center_x):
                crossings.append(curr.timestamp_sec)
        
        # 連続した横切りをラリーとしてグループ化
        if len(crossings) < 2:
            return
        
        rally_start = crossings[0]
        rally_crosses = 1
        
        for i in range(1, len(crossings)):
            time_diff = crossings[i] - crossings[i-1]
            
            if time_diff < 3.0:  # 3秒以内なら同じラリー
                rally_crosses += 1
            else:
                # ラリー終了
                if rally_crosses >= 2:  # 2回以上の往復でラリーとみなす
                    self.rally_events.append(RallyEvent(
                        start_time=rally_start,
                        end_time=crossings[i-1],
                        duration=crossings[i-1] - rally_start,
                        ball_crosses=rally_crosses
                    ))
                rally_start = crossings[i]
                rally_crosses = 1
        
        # 最後のラリー
        if rally_crosses >= 2:
            self.rally_events.append(RallyEvent(
                start_time=rally_start,
                end_time=crossings[-1],
                duration=crossings[-1] - rally_start,
                ball_crosses=rally_crosses
            ))
    
    def _compile_results(self) -> Dict:
        """結果をまとめる"""
        # ボール速度の統計
        speeds = []
        for i in range(1, len(self.ball_positions)):
            prev = self.ball_positions[i-1]
            curr = self.ball_positions[i]
            
            dx = curr.x - prev.x
            dy = curr.y - prev.y
            dt = curr.timestamp_sec - prev.timestamp_sec
            
            if dt > 0:
                speed = np.sqrt(dx**2 + dy**2) / dt
                speeds.append(speed)
        
        return {
            "video_info": {
                "path": str(self.video_path),
                "fps": self.fps,
                "resolution": f"{self.frame_width}x{self.frame_height}",
                "total_frames": self.total_frames
            },
            "ball_detection": {
                "detected_frames": len(self.ball_positions),
                "detection_rate": len(self.ball_positions) / (self.total_frames / self.sample_rate) if self.total_frames > 0 else 0,
                "ball_color": self.ball_color,
                "avg_confidence": np.mean([bp.confidence for bp in self.ball_positions]) if self.ball_positions else 0
            },
            "ball_speed": {
                "avg_speed": np.mean(speeds) if speeds else 0,
                "max_speed": np.max(speeds) if speeds else 0,
                "min_speed": np.min(speeds) if speeds else 0
            },
            "rally_detection": {
                "rally_count": len(self.rally_events),
                "avg_rally_duration": np.mean([r.duration for r in self.rally_events]) if self.rally_events else 0,
                "avg_ball_crosses": np.mean([r.ball_crosses for r in self.rally_events]) if self.rally_events else 0,
                "rallies": [asdict(r) for r in self.rally_events]
            }
        }
    
    def save_results(self, output_path: str):
        """結果をJSONファイルに保存"""
        results = self._compile_results()
        
        # numpy型を変換
        def convert_numpy(obj):
            if isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(i) for i in obj]
            return obj
        
        results = convert_numpy(results)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return output_path


# テスト用
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ball_tracker.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    tracker = BallTracker(video_path, sample_rate=2)
    results = tracker.run_tracking(verbose=True)
    
    print("\n=== トラッキング結果 ===")
    print(json.dumps(results, ensure_ascii=False, indent=2))
