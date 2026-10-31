"""
관절 각도·속도·가속도로 로봇 동작 시간을 계산하는 모듈.

핵심 아이디어
-------------
1) 가장 단순한 식:      시간 = 이동각도 / 회전속도
2) 실제 로봇(사다리꼴 속도):  가속 → 등속 → 감속
3) 여러 관절이 동시에 움직이면 '가장 오래 걸리는 관절'이 구간 시간을 결정
4) 전체 작업 시간 = 이동 구간 합 + 그리퍼(집기/놓기) 시간 + 대기 시간
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field


def simple_time(angle_deg: float, speed_deg_s: float) -> float:
    """등속 가정: 90° / 30°/s = 3초"""
    return abs(angle_deg) / speed_deg_s


def trapezoid_time(angle_deg: float, v_max: float, a_max: float) -> float:
    """사다리꼴 속도 프로파일로 한 관절이 angle_deg 만큼 움직이는 시간.

    가속 구간에서 최고속도까지 가는 데 필요한 각도 = v_max^2 / a_max (가속+감속 합)
    - 이동각도가 그보다 크면: 가속 → 등속 → 감속 (사다리꼴)
    - 작으면: 최고속도에 도달하지 못하고 바로 감속 (삼각형)
    """
    d = abs(angle_deg)
    if d == 0:
        return 0.0
    d_accel_decel = v_max ** 2 / a_max
    if d >= d_accel_decel:
        return d / v_max + v_max / a_max          # 사다리꼴
    return 2 * math.sqrt(d / a_max)               # 삼각형


def trapezoid_profile(angle_deg: float, v_max: float, a_max: float, dt: float = 0.01):
    """시간별 속도 곡선 (그래프 그리기용). [(t, v), ...] 반환"""
    d = abs(angle_deg)
    T = trapezoid_time(d, v_max, a_max)
    if T == 0:
        return [(0.0, 0.0)]
    v_peak = min(v_max, math.sqrt(d * a_max))
    t_acc = v_peak / a_max
    pts, t = [], 0.0
    while t <= T + 1e-9:
        if t < t_acc:
            v = a_max * t
        elif t > T - t_acc:
            v = a_max * (T - t)
        else:
            v = v_peak
        pts.append((round(t, 4), max(v, 0.0)))
        t += dt
    return pts


@dataclass
class Robot:
    """관절별 최대 속도(°/s)와 최대 가속도(°/s²). 값은 6축 소형 협동로봇 예시."""
    v_max: list[float] = field(default_factory=lambda: [180, 180, 180, 225, 225, 225])
    a_max: list[float] = field(default_factory=lambda: [360, 360, 360, 450, 450, 450])

    def segment_time(self, q_from: list[float], q_to: list[float], speed_pct: float) -> float:
        """한 구간(포즈 A → 포즈 B)의 시간. speed_pct=50 이면 속도·가속도 50%."""
        s = speed_pct / 100.0
        times = [
            trapezoid_time(b - a, v * s, acc * s)
            for a, b, v, acc in zip(q_from, q_to, self.v_max, self.a_max)
        ]
        return max(times)  # 모든 관절이 같이 도착하도록 가장 느린 관절에 맞춤


@dataclass
class PickPlaceTask:
    """티칭한 포즈 목록 + 그리퍼 시간"""
    waypoints: list[list[float]]       # 관절각(°) 리스트: 홈 → 집기위 → 집기 → 들기 → 놓기위 → 놓기 → 홈
    grip_close_s: float = 0.5
    grip_open_s: float = 0.4
    grip_after_index: int = 2          # 이 웨이포인트 도착 후 집기
    release_after_index: int = 5       # 이 웨이포인트 도착 후 놓기

    def predict(self, robot: Robot, speed_pct: float) -> dict:
        segs = [
            robot.segment_time(self.waypoints[i], self.waypoints[i + 1], speed_pct)
            for i in range(len(self.waypoints) - 1)
        ]
        move = sum(segs)
        total = move + self.grip_close_s + self.grip_open_s
        return {"segments": segs, "move_s": move, "total_s": total}


# 예제 티칭 데이터 (관절각, 단위 °)
EXAMPLE_TASK = PickPlaceTask(
    waypoints=[
        [0, -30, 60, 0, 60, 0],     # 0 홈
        [35, -10, 70, 0, 30, 35],   # 1 물건 위
        [35, 5, 80, 0, 5, 35],      # 2 물건 집는 위치
        [35, -10, 70, 0, 30, 35],   # 3 들어올림
        [-60, -15, 65, 0, 40, -60], # 4 목표 위
        [-60, 0, 78, 0, 12, -60],   # 5 놓는 위치
        [0, -30, 60, 0, 60, 0],     # 6 홈 복귀
    ]
)


if __name__ == "__main__":
    print("① 단순식: 90° / 30°/s =", simple_time(90, 30), "초")
    print("② 사다리꼴: 90°, v=30°/s, a=60°/s² =", round(trapezoid_time(90, 30, 60), 3), "초 (가감속 때문에 더 김)")
    robot = Robot()
    print("\n③ 물건 옮기기 작업 예측")
    for pct in (30, 50, 70, 100):
        r = EXAMPLE_TASK.predict(robot, pct)
        segs = ", ".join(f"{s:.2f}" for s in r["segments"])
        print(f"  속도 {pct:>3}% → 총 {r['total_s']:.2f}초  (구간: {segs})")
