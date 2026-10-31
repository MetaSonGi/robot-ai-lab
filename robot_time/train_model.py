"""
지도학습으로 '이론 계산 시간'의 오차를 보정한다.

비교하는 3가지 방법
1) 이론값 그대로 사용       (궤적 계산만)
2) 선형회귀                (이론값 + 속도 + 무게 → 실제 시간)
3) 랜덤포레스트            (비선형 관계까지 학습)

실행:  python robot_time/simulate_data.py  →  python robot_time/train_model.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

DATA = Path(__file__).resolve().parent.parent / "data" / "pick_place_log.csv"
FEATURES = ["theory_s", "speed_pct", "payload_kg", "total_angle_deg", "n_segments"]


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """물리적으로 의미 있는 조합 특징을 추가 (특징 공학)"""
    df = df.copy()
    s = df["speed_pct"] / 100
    df["theory_x_payload_speed"] = df["theory_s"] * df["payload_kg"] * s
    df["speed_sq"] = s ** 2
    return df


def main() -> None:
    df = add_features(pd.read_csv(DATA))
    feats = FEATURES + ["theory_x_payload_speed", "speed_sq"]
    X, y = df[feats], df["actual_s"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=0)

    results = {"1) 이론값 그대로": mean_absolute_error(y_te, X_te["theory_s"])}

    lin = LinearRegression().fit(X_tr, y_tr)
    results["2) 선형회귀 보정"] = mean_absolute_error(y_te, lin.predict(X_te))

    rf = RandomForestRegressor(n_estimators=200, random_state=0).fit(X_tr, y_tr)
    results["3) 랜덤포레스트"] = mean_absolute_error(y_te, rf.predict(X_te))

    print(f"테스트 작업 {len(y_te)}개, 평균 실제 시간 {y_te.mean():.2f}초\n")
    print("평균 절대 오차(MAE) — 작을수록 좋음")
    for name, mae in results.items():
        bar = "█" * int(mae * 40)
        print(f"  {name:<14} {mae:6.3f}초  {bar}")

    print("\n선형회귀 계수 (어떤 요인이 시간에 영향을 주나)")
    for f, c in zip(feats, lin.coef_):
        print(f"  {f:<24} {c:+.4f}")

    # 새 작업 예측 예시
    sample = add_features(pd.DataFrame([{
        "theory_s": 5.6, "speed_pct": 70, "payload_kg": 2.0,
        "total_angle_deg": 420, "n_segments": 6,
    }]))[feats]
    print(f"\n예시: 이론 5.60초, 속도 70%, 2kg → 실제 예측 {lin.predict(sample)[0]:.2f}초 (선형회귀)")


if __name__ == "__main__":
    np.random.seed(0)
    main()
