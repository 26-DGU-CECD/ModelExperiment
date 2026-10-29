# 실험 프로토콜

## 1. 데이터 분할 (고정)

- 유일한 분할 소스: `data/splits/manifest.csv`의 `split` 컬럼. 생성 스크립트 `src/make_splits.py`, 요약 `docs/split_summary.md`.
  **재분할 금지.** 분할을 바꿔야 하면 스크립트 수정 + 새 커밋 + 모든 실험 재실행.
- 그룹 = `source_file`. StratifiedGroupKFold(5, shuffle, seed 42), 층화 키 = 이벤트 라벨 + `source_origin`
  (aihub / esc50 / donateacry / other). background 클립은 원래 소스의 이벤트 클립과 항상 같은 split.
- fold 0 = **test**, fold 1 = **val**, fold 2~4 = **train**. val/test는 `is_augmented == 0`(orig)만.
- 용도:
  - **train**: 학습 전용. orig + aug 전부.
  - **val**: 체크포인트 선택, 캘리브레이션(temperature), 클래스별 임계값, 스태킹/라우터 학습, KD 교사 선택.
  - **test**: **최종 보고 외 사용 금지.** 개발 중 test 점수를 보고 결정하지 않는다. 실험당 test 평가는 1회가 원칙.

## 2. 테스트셋 3종

| 이름 | 구성 | 목적 |
|---|---|---|
| `test_clean` | test split orig 클립 5,877개 | 기본 분류 성능 |
| `test_noisy` | `test_clean` × MUSAN noise SNR 20 / 15 / 10 dB (각 5,877) | 잡음 강건성. SNR별 별도 보고 |
| `test_stream` | test split 소스의 **raw 원본**(2초 분할 전)을 연속 재생 + background 구간 삽입, 1초 hop 슬라이딩 | FA/hour, 지연, 이벤트 단위 recall |

- `test_noisy`는 `generate_musan_mixes.py`로 test 클립에만 생성 (아래 3절 제약 참고). train용 MUSAN 혼합본과 noise 파일이 겹치면 안 된다.
- `test_stream`은 raw가 현재 다운로드 제외 상태라 필요 시 test 소스의 raw만 추가로 받는다 (`*/raw/*` 중 test source_file만).
- 모든 테스트셋 결과는 `results/<실험명>/metrics.json`에 `test_clean`, `test_noisy_snr20/15/10`, `test_stream` 키로 분리 기록.

## 3. MUSAN noise 파일 train/test 분리 원칙

- MUSAN noise 777개(free-sound 730 + sound-bible 47, 약 585MB) 파일을 **파일 단위로** 두 묶음으로 나눈다:
  `noise_train` 80% / `noise_test` 20%, seed 42, 파일명 정렬 후 분배. 목록은 `data/splits/musan_noise_split.csv`로 커밋.
- train 혼합본(온라인/오프라인 증강)은 `noise_train`만, `test_noisy`는 `noise_test`만 사용. 같은 noise 파일이 양쪽에 등장하면 안 된다.
- 현재 `generate_musan_mixes.py`는 `--musan-root` 아래 모든 noise wav를 쓴다. 코드 수정 없이 분리하려면
  `data/musan_train/noise/...`, `data/musan_test/noise/...`에 해당 파일만 복사(또는 링크)하고 `--musan-root`로 각각 지정한다.
- HF에 올라온 기존 `musan_mixed_2s/`(fire_alarm만 존재)는 noise 분리가 안 돼 있으므로 **사용하지 않는다.**

## 4. 클래스별 목표 지표

| 그룹 | 클래스 | 1차 지표 | 2차 | 이유 |
|---|---|---|---|---|
| 위험음 | alarm, fire_alarm, scream, glass_break, gunshot, car_horn | **Recall** (목표 ≥ 0.95 @ test_clean) | Precision ≥ 0.80 | 놓치면 안전 문제 |
| 편의음 | water, knock, baby_cry | **Precision** (목표 ≥ 0.90) | Recall | 오알림이 사용성 해침 |
| 동물/이동 | dog_bark, cat_meow, bicycle | **F1** | — | 균형 |
| background | background | **FA/hour** (`test_stream`, 목표 ≤ 2/h) | background recall | 조용할 때 조용해야 함 |

- 집계 지표: macro-F1(13클래스), accuracy, 위험음 micro recall, background FA율 (`docs/metrics_schema.md`).
- 임계값은 **val**에서 클래스별로 정하고 test에 그대로 적용. test에서 임계값 조정 금지.

## 5. 실험 순서

| 단계 | 내용 | 산출물 |
|---|---|---|
| E0 | 베이스라인 범용 3개: YAMNet 임베딩+MLP(CPU), EfficientAT mn10, AST 또는 BEATs 소형 | per-class 표, confusion matrix |
| E1 | per-class 진단: 어느 모델이 어느 클래스에 강한지, 혼동쌍(alarm↔fire_alarm, scream↔baby_cry 등) | `docs/diagnosis_E1.md` |
| E2 | KD로 약한 멤버 보강: 강한 모델을 교사로 약한 클래스에 soft-label 증류 | E0 대비 per-class 변화 |
| E3 | 동질 스페셜리스트: mn10 범용 1개 vs mn04 스페셜리스트 3개 (위험/편의/동물+bg), **동일 MACs 예산** | MACs 표 + 성능 |
| E4 | 이종 스페셜리스트 + 스태킹: 멤버 확률을 val에서 학습한 스태커(LogReg/소형 MLP)로 결합 | 스태커 가중치 분석 |
| E5 | 어블레이션: (a) 스페셜리스트 쌩 학습(KD 없음) (b) 클래스 무작위 배정 (c) 캐스케이드(bg 게이트 → 분류기) | 각 항목 1행 |

- 각 실험은 `results/<실험명>/`에 metrics.json + predictions.csv, `logs/<실험명>.summary.md`, PROGRESS.md 항목, LEADERBOARD 갱신 후 커밋 (CLAUDE.md 체크리스트).
- 실험명 규칙: `E<단계>_<모델>_<조건>` 예) `E0_mn10_generalist`, `E3_mn04x3_specialist`, `E4_stack_hetero`.

## 6. 결과표 필수 행

모든 비교표에는 아래 두 행을 **항상** 포함한다:

- **best-single**: 같은 예산 내 단일 모델 최고 성능 (앙상블 이득의 기준선).
- **oracle-routing**: 클립마다 정답 클래스를 아는 스페셜리스트에게 보냈을 때의 상한 (라우터/스태커 손실의 기준선).

앙상블 이득 = 앙상블 − best-single, 라우팅 손실 = oracle-routing − 앙상블 로 보고한다.
