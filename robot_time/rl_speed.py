"""
강화학습 입문: 물건 무게에 따라 '가장 좋은 속도'를 스스로 찾기.

- 상태(state):  물건 무게 구간 (가벼움 / 보통 / 무거움)
- 행동(action): 속도 30% / 50% / 70% / 90%
- 보상(reward): -(작업 시간)  ...  물건을 떨어뜨리면 -10 벌점

알고리즘: 탭룰러 Q-러닝(한 번 행동하면 에피소드 끝 → 사실상 문맥 밴딧)
Q[state][action] ← Q + α · (reward − Q)

결과: 가벼우면 빠르게, 무거우면 천천히 옮기는 정책을 스스로 학습한다.
실제 로봇에서는 이 과정을 시뮬레이터(Isaac Sim, MuJoCo, Gazebo)에서 먼저 한다.
"""
from __future__ import annotations

import random

from simulate_data import fake_measure
from trajectory import EXAMPLE_TASK, Robot

STATES = ["가벼움(0~1kg)", "보통(1~2kg)", "무거움(2~3kg)"]
ACTIONS = [30, 50, 70, 90]
DROP_PENALTY = 10.0


def payload_to_state(kg: float) -> int:
    return min(int(kg), 2)


def run(episodes: int = 6000, alpha: float = 0.05, eps: float = 0.2, seed: int = 1):
    rng = random.Random(seed)
    robot = Robot()
    theory = {a: EXAMPLE_TASK.predict(robot, a)["total_s"] for a in ACTIONS}
    Q = [[0.0] * len(ACTIONS) for _ in STATES]

    for ep in range(episodes):
        kg = rng.uniform(0, 3)
        s = payload_to_state(kg)
        # ε-greedy: 가끔은 무작위로 탐험
        a = rng.randrange(len(ACTIONS)) if rng.random() < eps else max(
            range(len(ACTIONS)), key=lambda i: Q[s][i])
        speed = ACTIONS[a]
        t, ok = fake_measure(theory[speed], speed, kg, 6, rng)
        reward = -t - (0 if ok else DROP_PENALTY)
        Q[s][a] += alpha * (reward - Q[s][a])

    return Q


if __name__ == "__main__":
    Q = run()
    print("학습된 Q값 (값이 클수록 좋은 선택, 단위 ≈ -초)\n")
    print(" " * 16 + "".join(f"{a:>8}%" for a in ACTIONS))
    for s, row in enumerate(Q):
        best = max(range(len(ACTIONS)), key=lambda i: row[i])
        cells = "".join(f"{v:9.2f}" + ("★" if i == best else " ") for i, v in enumerate(row))
        print(f"{STATES[s]:<14}{cells}")
    print("\n★ = 학습된 최적 속도")
