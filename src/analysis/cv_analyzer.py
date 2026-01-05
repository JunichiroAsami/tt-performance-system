"""
CVAnalyzer - 定量分析モジュール

Phase 2で実装する機能:
- FA-04: フォーム分析（姿勢推定）
- FA-05: フットワーク分析（移動距離、コートカバー率）
- FP-03: フォーム改善ドリル提案（LLMと連携）

技術スタック:
- MediaPipe Pose (Tasks API): 33点の骨格キーポイント検出
- OpenCV: 動画処理
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import math
import urllib.request
import os


@dataclass
class PoseFrame:
    """1フレームの姿勢データ"""
    frame_number: int
    timestamp_sec: float
    landmarks: List[Dict]  # 33点のランドマーク
    visibility_avg: float  # 平均可視性スコア


@dataclass
class JointAngles:
    """関節角度データ"""
    frame_number: int
    timestamp_sec: float
    right_elbow: float  # 右肘の角度
    left_elbow: float   # 左肘の角度
    right_shoulder: float  # 右肩の角度
    left_shoulder: float   # 左肩の角度
    right_knee: float   # 右膝の角度
    left_knee: float    # 左膝の角度
    trunk_angle: float  # 体幹の傾き


@dataclass
class FootworkMetrics:
    """フットワーク指標"""
    total_distance: float  # 総移動距離（正規化座標）
    avg_speed: float       # 平均移動速度
    max_speed: float       # 最大移動速度
    lateral_movement: float  # 左右移動量
    forward_backward: float  # 前後移動量
    position_history: List[Tuple[float, float]]  # 位置履歴


@dataclass
class SwingAnalysis:
    """スイング分析結果"""
    swing_count: int       # スイング回数
    avg_swing_speed: float  # 平均スイング速度
    swing_events: List[Dict]  # スイングイベント（タイムスタンプ、種類）


# ランドマークのインデックス（MediaPipe Pose）
class PoseLandmark:
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32


LANDMARK_NAMES = {
    0: "NOSE", 1: "LEFT_EYE_INNER", 2: "LEFT_EYE", 3: "LEFT_EYE_OUTER",
    4: "RIGHT_EYE_INNER", 5: "RIGHT_EYE", 6: "RIGHT_EYE_OUTER",
    7: "LEFT_EAR", 8: "RIGHT_EAR", 9: "MOUTH_LEFT", 10: "MOUTH_RIGHT",
    11: "LEFT_SHOULDER", 12: "RIGHT_SHOULDER", 13: "LEFT_ELBOW", 14: "RIGHT_ELBOW",
    15: "LEFT_WRIST", 16: "RIGHT_WRIST", 17: "LEFT_PINKY", 18: "RIGHT_PINKY",
    19: "LEFT_INDEX", 20: "RIGHT_INDEX", 21: "LEFT_THUMB", 22: "RIGHT_THUMB",
    23: "LEFT_HIP", 24: "RIGHT_HIP", 25: "LEFT_KNEE", 26: "RIGHT_KNEE",
    27: "LEFT_ANKLE", 28: "RIGHT_ANKLE", 29: "LEFT_HEEL", 30: "RIGHT_HEEL",
    31: "LEFT_FOOT_INDEX", 32: "RIGHT_FOOT_INDEX"
}


class CVAnalyzer:
    """
    定量分析モジュール
    
    動画から以下のデータを抽出:
    1. 姿勢データ（33点の骨格キーポイント）
    2. 関節角度（肘、肩、膝、体幹）
    3. フットワーク指標（移動距離、速度）
    4. スイング検出
    """
    
    MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
    MODEL_PATH = "/tmp/pose_landmarker.task"
    
    def __init__(self, video_path: str, sample_rate: int = 5):
        """
        Args:
            video_path: 動画ファイルのパス
            sample_rate: 何フレームごとに分析するか（デフォルト: 5フレームごと）
        """
        self.video_path = Path(video_path)
        self.sample_rate = sample_rate
        
        # モデルをダウンロード
        self._download_model()
        
        # 結果格納用
        self.pose_frames: List[PoseFrame] = []
        self.joint_angles: List[JointAngles] = []
        self.footwork: Optional[FootworkMetrics] = None
        self.swing_analysis: Optional[SwingAnalysis] = None
        
        # 動画情報
        self.fps: float = 0
        self.total_frames: int = 0
        self.duration_sec: float = 0
    
    def _download_model(self):
        """MediaPipeモデルをダウンロード"""
        if not os.path.exists(self.MODEL_PATH):
            print(f"[CVAnalyzer] モデルをダウンロード中...")
            urllib.request.urlretrieve(self.MODEL_URL, self.MODEL_PATH)
            print(f"[CVAnalyzer] モデルダウンロード完了")
        
    def run_analysis(self, verbose: bool = False) -> Dict:
        """
        全ての定量分析を実行
        
        Returns:
            分析結果の辞書
        """
        if verbose:
            print(f"[CVAnalyzer] 動画を読み込み中: {self.video_path}")
        
        # 動画を開く
        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            raise ValueError(f"動画を開けません: {self.video_path}")
        
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration_sec = self.total_frames / self.fps if self.fps > 0 else 0
        
        if verbose:
            print(f"[CVAnalyzer] FPS: {self.fps:.1f}, 総フレーム: {self.total_frames}, 長さ: {self.duration_sec:.1f}秒")
        
        # PoseLandmarkerを初期化
        base_options = mp_python.BaseOptions(model_asset_path=self.MODEL_PATH)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_poses=2,  # 最大2人まで検出
            min_pose_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        with vision.PoseLandmarker.create_from_options(options) as landmarker:
            # フレームごとに処理
            frame_number = 0
            processed_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # サンプリングレートに従って処理
                if frame_number % self.sample_rate == 0:
                    timestamp_sec = frame_number / self.fps if self.fps > 0 else 0
                    
                    # 姿勢推定
                    pose_result = self._process_pose(landmarker, frame, frame_number, timestamp_sec)
                    if pose_result:
                        self.pose_frames.append(pose_result)
                        
                        # 関節角度を計算
                        angles = self._calculate_joint_angles(pose_result)
                        if angles:
                            self.joint_angles.append(angles)
                    
                    processed_count += 1
                    
                    if verbose and processed_count % 50 == 0:
                        progress = (frame_number / self.total_frames) * 100
                        print(f"[CVAnalyzer] 進捗: {progress:.1f}% ({processed_count}フレーム処理)")
                
                frame_number += 1
        
        cap.release()
        
        if verbose:
            print(f"[CVAnalyzer] 姿勢推定完了: {len(self.pose_frames)}フレーム")
        
        # フットワーク分析
        self.footwork = self._analyze_footwork()
        
        # スイング検出
        self.swing_analysis = self._detect_swings()
        
        if verbose:
            print(f"[CVAnalyzer] 分析完了")
        
        return self._compile_results()
    
    def _process_pose(self, landmarker, frame: np.ndarray, frame_number: int, timestamp_sec: float) -> Optional[PoseFrame]:
        """1フレームの姿勢推定"""
        # BGRからRGBに変換
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # MediaPipe Imageに変換
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # 姿勢推定実行
        results = landmarker.detect(mp_image)
        
        if not results.pose_landmarks or len(results.pose_landmarks) == 0:
            return None
        
        # 最初に検出された人物のランドマークを使用
        pose_landmarks = results.pose_landmarks[0]
        
        # ランドマークを抽出
        landmarks = []
        visibility_sum = 0
        
        for idx, landmark in enumerate(pose_landmarks):
            landmarks.append({
                "index": idx,
                "name": LANDMARK_NAMES.get(idx, f"LANDMARK_{idx}"),
                "x": landmark.x,
                "y": landmark.y,
                "z": landmark.z,
                "visibility": landmark.visibility if hasattr(landmark, 'visibility') else 1.0
            })
            visibility_sum += landmark.visibility if hasattr(landmark, 'visibility') else 1.0
        
        visibility_avg = visibility_sum / len(landmarks) if landmarks else 0
        
        return PoseFrame(
            frame_number=frame_number,
            timestamp_sec=timestamp_sec,
            landmarks=landmarks,
            visibility_avg=visibility_avg
        )
    
    def _calculate_joint_angles(self, pose_frame: PoseFrame) -> Optional[JointAngles]:
        """関節角度を計算"""
        landmarks = {lm["name"]: lm for lm in pose_frame.landmarks}
        
        def get_angle(p1: Dict, p2: Dict, p3: Dict) -> float:
            """3点から角度を計算（p2が頂点）"""
            v1 = np.array([p1["x"] - p2["x"], p1["y"] - p2["y"]])
            v2 = np.array([p3["x"] - p2["x"], p3["y"] - p2["y"]])
            
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
            angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
            return np.degrees(angle)
        
        try:
            # 右肘の角度（肩-肘-手首）
            right_elbow = get_angle(
                landmarks["RIGHT_SHOULDER"],
                landmarks["RIGHT_ELBOW"],
                landmarks["RIGHT_WRIST"]
            )
            
            # 左肘の角度
            left_elbow = get_angle(
                landmarks["LEFT_SHOULDER"],
                landmarks["LEFT_ELBOW"],
                landmarks["LEFT_WRIST"]
            )
            
            # 右肩の角度（肘-肩-腰）
            right_shoulder = get_angle(
                landmarks["RIGHT_ELBOW"],
                landmarks["RIGHT_SHOULDER"],
                landmarks["RIGHT_HIP"]
            )
            
            # 左肩の角度
            left_shoulder = get_angle(
                landmarks["LEFT_ELBOW"],
                landmarks["LEFT_SHOULDER"],
                landmarks["LEFT_HIP"]
            )
            
            # 右膝の角度（腰-膝-足首）
            right_knee = get_angle(
                landmarks["RIGHT_HIP"],
                landmarks["RIGHT_KNEE"],
                landmarks["RIGHT_ANKLE"]
            )
            
            # 左膝の角度
            left_knee = get_angle(
                landmarks["LEFT_HIP"],
                landmarks["LEFT_KNEE"],
                landmarks["LEFT_ANKLE"]
            )
            
            # 体幹の傾き（肩の中点と腰の中点を結ぶ線の垂直からの角度）
            shoulder_mid_x = (landmarks["LEFT_SHOULDER"]["x"] + landmarks["RIGHT_SHOULDER"]["x"]) / 2
            shoulder_mid_y = (landmarks["LEFT_SHOULDER"]["y"] + landmarks["RIGHT_SHOULDER"]["y"]) / 2
            hip_mid_x = (landmarks["LEFT_HIP"]["x"] + landmarks["RIGHT_HIP"]["x"]) / 2
            hip_mid_y = (landmarks["LEFT_HIP"]["y"] + landmarks["RIGHT_HIP"]["y"]) / 2
            
            trunk_angle = np.degrees(np.arctan2(shoulder_mid_x - hip_mid_x, hip_mid_y - shoulder_mid_y))
            
            return JointAngles(
                frame_number=pose_frame.frame_number,
                timestamp_sec=pose_frame.timestamp_sec,
                right_elbow=right_elbow,
                left_elbow=left_elbow,
                right_shoulder=right_shoulder,
                left_shoulder=left_shoulder,
                right_knee=right_knee,
                left_knee=left_knee,
                trunk_angle=trunk_angle
            )
        except (KeyError, ZeroDivisionError):
            return None
    
    def _analyze_footwork(self) -> FootworkMetrics:
        """フットワーク分析"""
        if not self.pose_frames:
            return FootworkMetrics(0, 0, 0, 0, 0, [])
        
        # 腰の中点を追跡（体の中心として）
        positions = []
        for pf in self.pose_frames:
            landmarks = {lm["name"]: lm for lm in pf.landmarks}
            try:
                hip_x = (landmarks["LEFT_HIP"]["x"] + landmarks["RIGHT_HIP"]["x"]) / 2
                hip_y = (landmarks["LEFT_HIP"]["y"] + landmarks["RIGHT_HIP"]["y"]) / 2
                positions.append((hip_x, hip_y, pf.timestamp_sec))
            except KeyError:
                continue
        
        if len(positions) < 2:
            return FootworkMetrics(0, 0, 0, 0, 0, [])
        
        # 移動距離と速度を計算
        total_distance = 0
        speeds = []
        lateral_movement = 0
        forward_backward = 0
        
        for i in range(1, len(positions)):
            dx = positions[i][0] - positions[i-1][0]
            dy = positions[i][1] - positions[i-1][1]
            dt = positions[i][2] - positions[i-1][2]
            
            distance = math.sqrt(dx**2 + dy**2)
            total_distance += distance
            
            lateral_movement += abs(dx)
            forward_backward += abs(dy)
            
            if dt > 0:
                speeds.append(distance / dt)
        
        avg_speed = sum(speeds) / len(speeds) if speeds else 0
        max_speed = max(speeds) if speeds else 0
        
        position_history = [(p[0], p[1]) for p in positions]
        
        return FootworkMetrics(
            total_distance=total_distance,
            avg_speed=avg_speed,
            max_speed=max_speed,
            lateral_movement=lateral_movement,
            forward_backward=forward_backward,
            position_history=position_history
        )
    
    def _detect_swings(self) -> SwingAnalysis:
        """スイング検出（手首の急激な動きを検出）"""
        if len(self.pose_frames) < 3:
            return SwingAnalysis(0, 0, [])
        
        swing_events = []
        wrist_speeds = []
        
        # 手首の速度を計算
        for i in range(1, len(self.pose_frames)):
            prev_frame = self.pose_frames[i-1]
            curr_frame = self.pose_frames[i]
            
            prev_landmarks = {lm["name"]: lm for lm in prev_frame.landmarks}
            curr_landmarks = {lm["name"]: lm for lm in curr_frame.landmarks}
            
            try:
                # 右手首の速度
                dx_r = curr_landmarks["RIGHT_WRIST"]["x"] - prev_landmarks["RIGHT_WRIST"]["x"]
                dy_r = curr_landmarks["RIGHT_WRIST"]["y"] - prev_landmarks["RIGHT_WRIST"]["y"]
                dt = curr_frame.timestamp_sec - prev_frame.timestamp_sec
                
                if dt > 0:
                    speed_r = math.sqrt(dx_r**2 + dy_r**2) / dt
                    wrist_speeds.append((curr_frame.timestamp_sec, speed_r, "right"))
                    
                # 左手首の速度
                dx_l = curr_landmarks["LEFT_WRIST"]["x"] - prev_landmarks["LEFT_WRIST"]["x"]
                dy_l = curr_landmarks["LEFT_WRIST"]["y"] - prev_landmarks["LEFT_WRIST"]["y"]
                
                if dt > 0:
                    speed_l = math.sqrt(dx_l**2 + dy_l**2) / dt
                    wrist_speeds.append((curr_frame.timestamp_sec, speed_l, "left"))
                    
            except KeyError:
                continue
        
        if not wrist_speeds:
            return SwingAnalysis(0, 0, [])
        
        # 速度の閾値を計算（平均の2倍以上をスイングとみなす）
        avg_speed = sum(s[1] for s in wrist_speeds) / len(wrist_speeds)
        threshold = avg_speed * 2.0
        
        # スイングイベントを検出
        last_swing_time = -1
        for timestamp, speed, hand in wrist_speeds:
            if speed > threshold and timestamp - last_swing_time > 0.3:  # 0.3秒以上間隔を空ける
                swing_events.append({
                    "timestamp_sec": round(timestamp, 2),
                    "speed": round(speed, 4),
                    "hand": hand
                })
                last_swing_time = timestamp
        
        swing_speeds = [e["speed"] for e in swing_events]
        avg_swing_speed = sum(swing_speeds) / len(swing_speeds) if swing_speeds else 0
        
        return SwingAnalysis(
            swing_count=len(swing_events),
            avg_swing_speed=avg_swing_speed,
            swing_events=swing_events
        )
    
    def _compile_results(self) -> Dict:
        """分析結果をまとめる"""
        # 関節角度の統計
        if self.joint_angles:
            angle_stats = {
                "right_elbow": {
                    "avg": np.mean([a.right_elbow for a in self.joint_angles]),
                    "min": np.min([a.right_elbow for a in self.joint_angles]),
                    "max": np.max([a.right_elbow for a in self.joint_angles]),
                    "std": np.std([a.right_elbow for a in self.joint_angles])
                },
                "left_elbow": {
                    "avg": np.mean([a.left_elbow for a in self.joint_angles]),
                    "min": np.min([a.left_elbow for a in self.joint_angles]),
                    "max": np.max([a.left_elbow for a in self.joint_angles]),
                    "std": np.std([a.left_elbow for a in self.joint_angles])
                },
                "right_knee": {
                    "avg": np.mean([a.right_knee for a in self.joint_angles]),
                    "min": np.min([a.right_knee for a in self.joint_angles]),
                    "max": np.max([a.right_knee for a in self.joint_angles]),
                    "std": np.std([a.right_knee for a in self.joint_angles])
                },
                "left_knee": {
                    "avg": np.mean([a.left_knee for a in self.joint_angles]),
                    "min": np.min([a.left_knee for a in self.joint_angles]),
                    "max": np.max([a.left_knee for a in self.joint_angles]),
                    "std": np.std([a.left_knee for a in self.joint_angles])
                },
                "trunk_angle": {
                    "avg": np.mean([a.trunk_angle for a in self.joint_angles]),
                    "min": np.min([a.trunk_angle for a in self.joint_angles]),
                    "max": np.max([a.trunk_angle for a in self.joint_angles]),
                    "std": np.std([a.trunk_angle for a in self.joint_angles])
                }
            }
        else:
            angle_stats = {}
        
        return {
            "video_info": {
                "path": str(self.video_path),
                "fps": self.fps,
                "total_frames": self.total_frames,
                "duration_sec": round(self.duration_sec, 2),
                "analyzed_frames": len(self.pose_frames)
            },
            "pose_detection": {
                "frames_with_pose": len(self.pose_frames),
                "detection_rate": len(self.pose_frames) / (self.total_frames / self.sample_rate) if self.total_frames > 0 else 0,
                "avg_visibility": np.mean([pf.visibility_avg for pf in self.pose_frames]) if self.pose_frames else 0
            },
            "joint_angles": {
                "frame_count": len(self.joint_angles),
                "statistics": angle_stats
            },
            "footwork": asdict(self.footwork) if self.footwork else {},
            "swing_analysis": asdict(self.swing_analysis) if self.swing_analysis else {}
        }
    
    def get_pose_at_time(self, timestamp_sec: float) -> Optional[PoseFrame]:
        """指定時間に最も近い姿勢データを取得"""
        if not self.pose_frames:
            return None
        
        closest = min(self.pose_frames, key=lambda pf: abs(pf.timestamp_sec - timestamp_sec))
        return closest
    
    def get_angles_at_time(self, timestamp_sec: float) -> Optional[JointAngles]:
        """指定時間に最も近い関節角度データを取得"""
        if not self.joint_angles:
            return None
        
        closest = min(self.joint_angles, key=lambda a: abs(a.timestamp_sec - timestamp_sec))
        return closest
    
    def save_results(self, output_path: str):
        """分析結果をJSONファイルに保存"""
        results = self._compile_results()
        
        # numpy型をPython標準型に変換
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
        print("Usage: python cv_analyzer.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    analyzer = CVAnalyzer(video_path, sample_rate=5)
    results = analyzer.run_analysis(verbose=True)
    
    print("\n=== 分析結果 ===")
    print(json.dumps(results, ensure_ascii=False, indent=2))
