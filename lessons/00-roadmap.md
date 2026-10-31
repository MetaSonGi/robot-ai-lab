# 0. 로드맵과 참고 영상

## 전체 흐름

```
Python 기초 → 데이터 기록·시각화 → 관절 시간 계산 → 회귀로 오차 보정
          → 영상 인식(OpenCV) → 강화학습 → VLA
```

| 주차 | 목표 | 확인 방법 |
|---|---|---|
| 1 | Python 기본 문법, 함수, 리스트 | `trajectory.py` 의 `simple_time` 을 직접 다시 써보기 |
| 2 | 사다리꼴 속도 프로파일 이해 | 손으로 계산한 값과 `trapezoid_time` 결과 비교 |
| 3 | CSV·pandas·그래프 | `data/pick_place_log.csv` 를 열어 속도별 평균 시간 그래프 그리기 |
| 4 | 회귀 모델 | `train_model.py` MAE 가 왜 줄어드는지 설명하기 |
| 5 | OpenCV 기초 | `draw_light.py` 의 MotionTracker 단계를 한 줄씩 화면에 띄워보기 |
| 6 | 호모그래피 | 4점을 바꿔가며 변환 결과 확인 |
| 7 | 강화학습 | `rl_speed.py` 의 벌점·ε 값을 바꾸면 정책이 어떻게 바뀌나 |
| 8 | 통합 발표 | 웹 사이트 + 시연 영상으로 포트폴리오 정리 |

## 참고 영상

- AI 기초: https://youtu.be/N3st1ZrB_zc
- 보안(해킹) 1: https://youtu.be/BXAbKHPuM70
- 보안(해킹) 2: https://youtu.be/HX96Uqq7AMg

영상을 본 뒤 핵심 내용을 이 파일 아래에 3줄씩 메모해 두면 복습할 때 좋아요.

## 메모

- 
