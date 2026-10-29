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

- **실제 분리 (2026-10-29, `src/download_musan.py`)**: HF `FluidInference/musan` `noise/**` 774개 wav(free-sound + sound-bible, 585MB)를
  `data/musan/noise/`에 받고, 파일명 정렬 후 seed 42로 20%를 test에 배정:

  | 묶음 | 파일 수 | MB | 경로 |
  |---|---|---|---|
  | noise_train | 619 | 462.5 | `data/musan_train/noise/` (하드링크) |
  | noise_test | 155 | 122.1 | `data/musan_test/noise/` (하드링크) |

  목록: `data/musan/noise_split.csv` (file, split, size). data/는 git 제외이므로 재현은 스크립트 재실행(결정적).
- train 혼합(온라인 `src/data.py: MusanMixer`, configs `aug.musan: true, musan_prob, musan_snr_range`)은 `musan_train`만,
  `test_noisy`는 `musan_test`만 사용. 같은 noise 파일이 양쪽에 등장하면 안 된다.
- `test_noisy` 생성: `src/musan_mix.py`(원본 `generate_musan_mixes.py` + `--only`, `--output-strip`)로 test orig 5,877클립 × SNR 20/15/10
  → `data/test_noisy/<label>/clips_2s/...` 17,631개. 인덱스 `data/splits/manifest_test_noisy.csv`
  (filepath, label_fine, source_file, snr, clean_filepath). 검증 `src/verify_musan_mixes.py`.
  평가: `python src/evaluate.py --config ... --eval-set noisy` → metrics.json `noisy_snr20/15/10`.
- HF에 올라온 기존 `musan_mixed_2s/`(fire_alarm만 존재)는 noise 분리가 안 돼 있으므로 **사용하지 않는다.**

### 증강 기준점 (2026-10-29)

- **E0m 이후 모든 모델(E0m, E1k, E2k, S*, SB*, A*)은 MUSAN train noise 온라인 증강을 사용한다**
  (`aug.musan: true, musan_prob: 0.5, musan_snr_range: [5, 20]`, noise = `data/musan_train`만).
- **E0 / E1 / E2는 증강 전 참고용**이다. 리더보드에서는 남기되 비교·융합의 기준은 E0m/E1k/E2k.
  증강 전 예측으로 만든 융합 결과는 실험명에 `pre-musan` 태그를 붙인다 (예: `F_generalist_soft_premusan`).

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

### 융합 방법 정의 (`src/fuse.py`, val로 피팅 → test/noisy 보고)

| method | 대상 | 정의 |
|---|---|---|
| `best_single` | 범용 | val macro-F1 최고 멤버의 예측 그대로 (앙상블 이득 기준선) |
| `hard_vote` | 범용 | argmax 다수결, 동점은 val F1 높은 멤버 |
| `soft_avg` | 범용 | 멤버별 val temperature scaling 후 확률 평균 |
| `weighted_soft` | 범용 | 보정 확률을 val macro-F1 비례 가중 평균 |
| `stacking` | 범용 | 보정 확률 concat → 로지스틱 회귀(C=1.0), val로 학습 |
| `rule` | 스페셜리스트 | 담당 클래스 확률 그대로, background = min_k prob_other |
| `gated` | 스페셜리스트 | p_k(c)·(1−p_k(other)), background = min_k prob_other |
| `stacked` | 스페셜리스트 | [담당 확률들 + prob_other] concat → 로지스틱 회귀 |
| `oracle` | 스페셜리스트 | 정답 라벨이 속한 그룹의 스페셜리스트만 사용(라우팅 상한). 정답 background는 모든 스페셜리스트가 other를 최대로 낼 때만 background |

운영점(표 D): val에서 클래스별 임계값 tau — 긴급 recall ≥ 0.95를 만족하는 가장 높은 tau, 일상(water/knock/baby_cry) precision ≥ 0.90을 만족하는
가장 낮은 tau, 나머지 F1 최대. 판정 = max_c p_c/tau_c, 전부 1 미만이면 background. FA/hour는 bg FA율 × 1800 프록시(스트리밍 테스트 전까지).
주의: 임계값은 클래스 간 혼동(alarm→fire_alarm)을 못 고치므로 긴급 recall 목표가 test에서 안 맞을 수 있다.

## 7. 라벨 정의: cry / baby_cry

- `label_fine`은 `baby_cry`를 출처로 둘로 나눈다. **AI Hub `울음`(S-21… 소스) → `cry`** (성인/아동 울음, 긴급 그룹),
  **ESC-50 + donateacry → `baby_cry`** (영아 울음, 편의음). 나머지 라벨은 `label`과 동일. 14클래스 = 이벤트 13 + background.
- 근거: 두 출처는 의미(성인 vs 영아)와 녹음 환경(AI Hub 스튜디오/시나리오 녹음 vs 가정/필드 스마트폰 녹음)이 다르다.
  하나로 합치면 모델이 "울음"이 아니라 녹음 환경을 학습할 위험이 있고, 긴급도(성인 비명성 울음 vs 영아 울음)도 다르다.
- **편향 주의**: 출처 = 라벨이므로 cry/baby_cry 구분 성능은 녹음 환경 구분 성능일 수 있다. evaluate.py가
  `cry_babycry_confusion`을 따로 기록하고, 필요하면 cross-source 테스트(예: 같은 환경에서 녹음한 소수 샘플)로 검증한다.
- 분할은 변경하지 않았다 (source 단위 fold 그대로). 표: `docs/split_summary.md` (label_fine 기준).

### v2 라벨 (2026-10-30, `src/relabel.py --mode relabel_s103`)

- **S_103 시나리오의 alarm 클립 → fire_alarm 재라벨.** 근거: 청취 확인 — S_103 "alarm"은 전부 화재경보음(fire_alarm과 동일),
  다른 시나리오(S_101/S_102)의 alarm은 차량 사이렌(구급차 등). fire_alarm 소스는 원래부터 전부 S_103.
  E0(v1) test에서 S_103 alarm recall 0.061 (412 중 380이 fire_alarm 예측).
- 영향: 4,570클립 / 166소스 (train 3,777 / val 381 / test 412 클립; 소스 103 / 32 / 31). split/fold는 그대로, `label_fine`만 변경.
  alarm 클립 11,714 → 7,144, fire_alarm 4,558 → 9,128. **alarm 클래스는 실질적으로 "차량 사이렌"**.
- 발견: S_103 alarm 소스 166개 중 **164개는 fire_alarm 소스와 `source_file` 이름이 같다**(오디오는 다름 — AI Hub가 같은 녹음 ID를
  경보/화재경보 폴더에 각각 둔 것). 분할 키가 `source_file`이라 같은 이름은 이미 같은 fold에 있었고(누수 없음), 재라벨 후 fire_alarm
  소스 수가 169로 거의 안 느는 이유도 이것. 소스 수 표는 "이름 기준"임에 주의.
- 원본 라벨은 `data/splits/manifest_v1.csv`(git 제외; `src/make_splits.py` → `relabel.py`로 재현). `configs/labels.yaml: version: v2`.
- 기존 결과(E0/E0m/E1/E2/E2k/E1k/F_generalist_*_premusan)는 metrics.json `label_version: v1`로 스탬프되어 리더보드 `labels` 열에서 분리.
  v2 모델은 큐(`configs/queue.yaml`)에서 `*_v2` 이름으로 전부 재학습. v1과 v2는 직접 비교하지 않는다.
- 라벨 감사(`docs/label_audit.md`, E0 v1): F1* < 0.6 시나리오는 alarm/S_103 외에 background/S_202(0.578), background/W_102(0.514) —
  조용한 bicycle/gunshot 구간을 background로 라벨한 클립이 이벤트로 예측되는 경우. -30 dBFS 무음 판정 경계 문제이지 라벨 오류는 아님.

## 8. 스페셜리스트 배정 두 버전

| 버전 | 정의 | 파일 |
|---|---|---|
| **S-semantic** | 의미 기반 사전 배정. efficientat→caution(bicycle, baby_cry, gunshot, glass_break), yamnet→emergency(alarm, fire_alarm, scream, cry, car_horn), mnv4→daily(water, knock, dog_bark, cat_meow) | `configs/groups.yaml: semantic` |
| **S-best** | E0~E2 범용 결과의 per-class F1로 각 클래스를 가장 잘 맞춘 모델에 배정 (val 기준) | `configs/groups.yaml: best` (E2 후 채움) |

각 스페셜리스트 학습 라벨 = 담당 라벨 + `other`(나머지 이벤트 + background). other는 train에서 담당 클립 합의 1.5배로 cap,
background와 `confusers`를 우선 포함. val/test는 cap 없이 전부 평가 (거절률 측정).

## 9. 결과표 A~D (`results/LEADERBOARD.md`)

| 표 | 내용 | 행 |
|---|---|---|
| A | 범용 per-class F1 (모델 × 14클래스 + macro-F1) | generalist 실험 |
| B | 스페셜리스트 개별: 담당 클래스 F1, 같은 모델 범용의 동일 클래스 F1, Δ, 비담당 이벤트 거절률, background 거절률 | specialist 실험 × 담당 클래스 |
| C | 조건별 요약: macro-F1 / accuracy / 긴급 recall / bg FA | generalist + ensemble (best-single, oracle-routing 포함) |
| D | 운영점: 규칙/임계값, 긴급 recall, precision, FA/hour | `operating_point` 있는 실험 |

빈 셀은 `-`. 전부 `results/*/metrics.json`에서 재생성.

## 10. 실험명 규칙

`E<n>_<model>_generalist` 범용, `S<n>_<model>_<group>` semantic 스페셜리스트, `SB_<model>_<group>` best 배정, `F<n>_<...>` 융합, `A<n>_<...>` 어블레이션.

| 실험명 | 내용 |
|---|---|
| `E0_efficientat_generalist` | mn10_as 14클래스 |
| `E1_yamnet_generalist` | YAMNet 임베딩 + MLP (CPU) |
| `E2_mnv4_generalist` | MobileNetV4 (timm) |
| `S1_efficientat_caution` | caution 4 + other |
| `S2_yamnet_emergency` | emergency 5 + other |
| `S3_mnv4_daily` | daily 4 + other |
| `SB_*` | best 배정 버전 |

config는 `configs/<실험명>.yaml`, 결과는 `results/<실험명>/`, 체크포인트 `checkpoints/<실험명>/best.pt`(git 제외), 로그 `logs/<실험명>.summary.md`.
