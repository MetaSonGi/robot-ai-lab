"""
손으로 벽에 빛을 그리는 인터랙티브 드로잉

웹캠 → 손(또는 움직임) 위치 찾기 → 호모그래피로 프로젝터 좌표 변환 → 빛 궤적 그리기 → 빔프로젝터 출력

추적 방법 2가지
- mediapipe 가 설치돼 있으면: 검지 끝(랜드마크 8번)을 추적
- 없으면: 프레임 차이(움직임)가 가장 큰 곳의 중심을 추적  ← OpenCV 만으로 동작

키:  c 지우기 | m 추적 모드 전환 | q 종료
"""
from __future__ import annotations

import argparse
import colorsys
import time
from pathlib import Path

import cv2
import numpy as np

CALIB = Path(__file__).with_name("calib.npy")


def load_calib(pw: int, ph: int):
    if CALIB.exists():
        c = np.load(CALIB, allow_pickle=True).item()
        return c["H"], c["pw"], c["ph"], c["px"]
    print("calib.npy 없음 → 보정 없이 카메라 화면을 그대로 늘려서 사용합니다.")
    return None, pw, ph, None


class MotionTracker:
    """움직임 중심 추적 (OpenCV 기초: 흑백 → 블러 → 차이 → 이진화 → 모멘트)"""

    def __init__(self):
        self.prev = None

    def __call__(self, frame):
        gray = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (21, 21), 0)
        if self.prev is None:
            self.prev = gray
            return None
        diff = cv2.absdiff(self.prev, gray)
        self.prev = gray
        _, th = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        M = cv2.moments(th)
        if M["m00"] < 255 * 400:  # 움직임이 너무 작으면 무시
            return None
        return M["m10"] / M["m00"], M["m01"] / M["m00"]


class HandTracker:
    """mediapipe 손 추적 (설치돼 있을 때만)"""

    def __init__(self):
        import mediapipe as mp  # noqa: F401
        self.hands = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.6)

    def __call__(self, frame):
        h, w = frame.shape[:2]
        res = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if not res.multi_hand_landmarks:
            return None
        tip = res.multi_hand_landmarks[0].landmark[8]  # 검지 끝
        return tip.x * w, tip.y * h


def make_trackers():
    trackers = {"motion": MotionTracker()}
    try:
        trackers["hand"] = HandTracker()
    except Exception as e:  # mediapipe 미설치 또는 버전 차이
        print("손 추적 사용 불가 → 움직임 추적만 사용:", type(e).__name__)
    return trackers


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cam", type=int, default=0)
    ap.add_argument("--pw", type=int, default=1280)
    ap.add_argument("--ph", type=int, default=720)
    ap.add_argument("--fade", type=float, default=0.96, help="잔상 유지율 (1에 가까울수록 오래 남음)")
    args = ap.parse_args()

    H, pw, ph, px = load_calib(args.pw, args.ph)
    trackers = make_trackers()
    mode = "hand" if "hand" in trackers else "motion"

    cap = cv2.VideoCapture(args.cam)
    canvas = np.zeros((ph, pw, 3), np.float32)
    last = None
    cv2.namedWindow("projector", cv2.WINDOW_NORMAL)
    if px is not None:
        cv2.moveWindow("projector", px, 0)
        cv2.setWindowProperty("projector", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        ok, frame = cap.read()
        if not ok:
            print("웹캠을 열 수 없습니다.")
            break
        if H is None:
            frame_for_track = cv2.flip(frame, 1)  # 보정 없으면 거울 모드
        else:
            frame_for_track = frame
        p = trackers[mode](frame_for_track)

        canvas *= args.fade  # 잔상이 서서히 사라짐
        if p is not None:
            if H is not None:
                u, v = cv2.perspectiveTransform(np.float32([[p]]), H)[0, 0]
            else:
                h, w = frame.shape[:2]
                u, v = p[0] / w * pw, p[1] / h * ph
            pt = (int(u), int(v))
            hue = (time.time() * 0.15) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
            color = (b, g, r)
            if last is not None:
                cv2.line(canvas, last, pt, color, 14, cv2.LINE_AA)
            cv2.circle(canvas, pt, 10, (1, 1, 1), -1, cv2.LINE_AA)
            last = pt
        else:
            last = None

        glow = cv2.GaussianBlur(canvas, (0, 0), 12)  # 빛 번짐 효과
        out = np.clip((canvas + glow * 1.5) * 255, 0, 255).astype(np.uint8)
        cv2.imshow("projector", out)
        preview = frame_for_track.copy()
        cv2.putText(preview, f"mode: {mode}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        if p is not None:
            cv2.circle(preview, (int(p[0]), int(p[1])), 10, (0, 255, 0), 2)
        cv2.imshow("camera", preview)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("c"):
            canvas[:] = 0
        if key == ord("m") and len(trackers) > 1:
            mode = "motion" if mode == "hand" else "hand"

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
