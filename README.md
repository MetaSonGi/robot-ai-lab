# Robot AI Lab · 로봇 AI 실습실

로봇이 물건을 옮기는 시간을 **관절 속도·회전각도로 예측**하고, **AI로 오차를 줄이고**, **강화학습으로 속도를 최적화**하는 과정을 단계별로 배우는 저장소입니다.
덤으로 **웹캠 + 빔프로젝터 인터랙티브 미디어아트**도 함께 만듭니다.

> 🌐 웹에서 보기: `docs/index.html` (GitHub Pages로 자동 배포 — 아래 "웹 사이트 켜기" 참고)

## 무엇을 만드나

| 프로젝트 | 흐름 | 폴더 |
|---|---|---|
| ① 로봇 운반 시간 예측·속도 최적화 | 티칭 → 궤적 시간 계산 → 실제 측정 → AI 보정 → 강화학습 최적화 | `robot_time/` |
| ② 웹캠 인터랙티브 프로젝션 | 웹캠 → 손/움직임 추적 → 좌표 보정 → 빛 그리기 → 빔프로젝터 | `mediaart/` |

## 빠른 시작

```bash
git clone <이 저장소 주소>
cd robot-ai-lab
pip install -r requirements.txt

# ① 로봇 시간 예측
python robot_time/trajectory.py      # 관절 속도로 시간 계산
python robot_time/simulate_data.py   # 측정 데이터(가상) 600개 생성
python robot_time/train_model.py     # AI로 예측 오차 줄이기
python robot_time/rl_speed.py        # 강화학습으로 무게별 최적 속도 찾기

# ② 미디어아트 (웹캠 필요)
python mediaart/calibrate.py         # 웹캠 ↔ 프로젝터 좌표 맞추기
python mediaart/draw_light.py        # 손으로 벽에 빛 그리기
```

## 실행 결과 예시

```
속도  30% → 총 8.55초
속도  50% → 총 6.54초
속도 100% → 총 4.81초

평균 절대 오차(MAE)
  1) 이론값 그대로   1.276초
  2) 선형회귀 보정   0.106초   ← AI 보정으로 오차 92% 감소

강화학습 최적 속도:  가벼움 70%  |  보통 50%  |  무거움 50%
```

## 학습 순서

| 단계 | 문서 | 실습 코드 |
|---|---|---|
| 0 | [로드맵과 참고 영상](lessons/00-roadmap.md) | – |
| 1 | [관절 속도로 시간 계산](lessons/01-joint-time.md) | `trajectory.py` |
| 2 | [AI로 예측 오차 보정](lessons/02-ai-correction.md) | `simulate_data.py`, `train_model.py` |
| 3 | [강화학습으로 속도 최적화](lessons/03-reinforcement-learning.md) | `rl_speed.py` |
| 4 | [VLA: 보고, 듣고, 움직이는 로봇](lessons/04-vla.md) | – |
| 5 | [웹캠 + 빔프로젝터 미디어아트](lessons/05-webcam-projection.md) | `calibrate.py`, `draw_light.py` |
| 6 | [로봇·카메라 시스템 보안 기초](lessons/06-security-basics.md) | – |

## 폴더 구조

```
robot-ai-lab/
├── robot_time/      로봇 시간 예측 코드
├── mediaart/        웹캠 미디어아트 코드
├── lessons/         단계별 학습 문서
├── data/            측정(가상) 데이터 CSV
└── docs/            웹 학습 사이트 (GitHub Pages)
```

## GitHub에 올리기

```bash
# GitHub에서 빈 저장소 robot-ai-lab 를 만든 뒤
git remote add origin https://github.com/<내아이디>/robot-ai-lab.git
git push -u origin main
```

## 웹 사이트 켜기 (GitHub Pages)

1. 저장소 → **Settings → Pages**
2. **Source: GitHub Actions** 선택
3. `main` 에 push 하면 `.github/workflows/pages.yml` 이 `docs/` 를 배포
4. 주소: `https://<내아이디>.github.io/robot-ai-lab/`

웹 사이트에서는 관절 시간 계산기, AI 보정, 강화학습, 빛 그리기를 브라우저에서 바로 실습할 수 있고, GitHub Pages(https)에서는 웹캠 모드도 동작합니다.

## 실제 로봇으로 확장하기

`simulate_data.py` 의 가상 측정 대신 실제 로봇 로그를 같은 CSV 열(`speed_pct, payload_kg, total_angle_deg, n_segments, theory_s, actual_s, success`)로 저장하면 나머지 코드는 그대로 동작합니다. ROS 2 + MoveIt 을 쓴다면 MoveIt 의 시간 매개변수화(Time Parameterization) 결과를 `theory_s` 로 사용하세요.
