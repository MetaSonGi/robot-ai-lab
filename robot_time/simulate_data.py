"""
'실제 로봇에서 측정했다'고 가정한 가짜 데이터를 만든다.

실제 로봇이 이론보다 느린 이유(여기서 흉내 냄):
- 무거운 물건 → 모터 토크 한계로 가속이 덜 됨
- 목표 도착 후 진동이 멈출 때까지 기다리는 정착(settling) 시간
- 제어기·통신 지연
- 측정 잡음

실제 로봇이 있다면 이 파일 대신 robot_logger 로 측정값을 같은 CSV 형식으로 저장하면 된다.
"""
from __future__ import annotations

import csv
import math
import random
from pathlib import Path

from trajectory import EXAMPLE_TASK, PickPlaceTask, Robot

COLUMNS = [
    "speed_pct", "payload_kg", "total_angle_deg", "n_segments",
    "theory_s", "actual_s", "success",
]


def random_task(rng: random.Random) -> PickPlaceTask:
    """예제 티칭 포즈를 조금씩 바꿔 다양한 작업을 만든다."""
    wps = []
    for wp in EXAMPLE_TASK.waypoints:
        wps.append([q + rng.uniform(-15, 15) for q in wp])
    wps[-1] = wps[0][:]  # 홈 복귀
    return PickPlaceTask(waypoints=wps)


def fake_measure(theory_s: float, speed_pct: float, payload_kg: float,
                 n_segments: int, rng: random.Random) -> tuple[float, int]:
    s = speed_pct / 100
    payload_slow = 1 + 0.12 * payload_kg * s          # 빠를수록 무게 영향 큼
    settle = n_segments * (0.03 + 0.10 * s ** 2)       # 빠르게 멈추면 진동이 커서 더 기다림
    latency = n_segments * 0.04
    noise = rng.gauss(0, 0.05 * theory_s ** 0.5)
    actual = theory_s * payload_slow + settle + latency + noise

    # 너무 빠르고 무거우면 물건을 떨어뜨릴 확률 증가
    p_drop = 1 / (1 + math.exp(-(6 * s + 1.2 * payload_kg - 7.5)))
    success = int(rng.random() > p_drop)
    return round(actual, 3), success


def generate(n: int = 600, seed: int = 0) -> list[dict]:
    rng = random.Random(seed)
    robot = Robot()
    rows = []
    for _ in range(n):
        task = random_task(rng)
        speed = rng.choice([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        payload = round(rng.uniform(0, 3), 2)
        pred = task.predict(robot, speed)
        total_angle = sum(
            max(abs(b - a) for a, b in zip(task.waypoints[i], task.waypoints[i + 1]))
            for i in range(len(task.waypoints) - 1)
        )
        n_seg = len(task.waypoints) - 1
        actual, ok = fake_measure(pred["total_s"], speed, payload, n_seg, rng)
        rows.append({
            "speed_pct": speed, "payload_kg": payload,
            "total_angle_deg": round(total_angle, 1), "n_segments": n_seg,
            "theory_s": round(pred["total_s"], 3), "actual_s": actual, "success": ok,
        })
    return rows


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "data" / "pick_place_log.csv"
    out.parent.mkdir(exist_ok=True)
    rows = generate()
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)}개 작업 기록 저장 → {out}")
    print("첫 3줄:", *rows[:3], sep="\n  ")
