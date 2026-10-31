"""
웹캠 ↔ 빔프로젝터 좌표 맞추기 (호모그래피 보정)

순서
1) 빔프로젝터를 보조 모니터로 연결하고 이 프로그램 실행
2) 프로젝터 화면에 4개의 원(좌상→우상→우하→좌하)이 투사된다
3) 웹캠 창에서 벽에 비친 그 4개의 원을 같은 순서로 클릭
4) calib.npy 가 저장되고, 이후 draw_light.py 가 이 값을 사용한다

원리: 평평한 벽이라면 카메라 좌표(x,y) → 프로젝터 좌표(u,v)는 3×3 행렬 H 하나로 변환된다.
      cv2.getPerspectiveTransform(카메라 4점, 프로젝터 4점) = H
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

OUT = Path(__file__).with_name("calib.npy")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cam", type=int, default=0, help="웹캠 번호")
    ap.add_argument("--pw", type=int, default=1280, help="프로젝터 가로 해상도")
    ap.add_argument("--ph", type=int, default=720, help="프로젝터 세로 해상도")
    ap.add_argument("--px", type=int, default=1920, help="프로젝터 화면이 시작하는 x 좌표(보조 모니터 위치)")
    args = ap.parse_args()

    m = 80  # 가장자리 여백
    proj_pts = np.float32([[m, m], [args.pw - m, m], [args.pw - m, args.ph - m], [m, args.ph - m]])

    # 프로젝터 창: 검은 배경 + 번호 붙은 흰 원
    pattern = np.zeros((args.ph, args.pw, 3), np.uint8)
    for i, (x, y) in enumerate(proj_pts.astype(int)):
        cv2.circle(pattern, (x, y), 25, (255, 255, 255), -1)
        cv2.putText(pattern, str(i + 1), (x + 35, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    cv2.namedWindow("projector", cv2.WINDOW_NORMAL)
    cv2.moveWindow("projector", args.px, 0)
    cv2.setWindowProperty("projector", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("projector", pattern)

    clicks: list[tuple[int, int]] = []

    def on_click(event, x, y, *_):
        if event == cv2.EVENT_LBUTTONDOWN and len(clicks) < 4:
            clicks.append((x, y))

    cap = cv2.VideoCapture(args.cam)
    cv2.namedWindow("camera")
    cv2.setMouseCallback("camera", on_click)
    print("카메라 창에서 벽에 비친 원 1→2→3→4 순서로 클릭하세요. (r: 다시, q: 종료)")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("웹캠을 열 수 없습니다. --cam 번호를 바꿔보세요.")
            break
        for i, p in enumerate(clicks):
            cv2.circle(frame, p, 8, (0, 0, 255), -1)
            cv2.putText(frame, str(i + 1), (p[0] + 10, p[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.imshow("camera", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("r"):
            clicks.clear()
        if key == ord("q"):
            break
        if len(clicks) == 4:
            H = cv2.getPerspectiveTransform(np.float32(clicks), proj_pts)
            np.save(OUT, {"H": H, "pw": args.pw, "ph": args.ph, "px": args.px}, allow_pickle=True)
            print("보정 완료 →", OUT)
            print("H =\n", np.round(H, 3))
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
