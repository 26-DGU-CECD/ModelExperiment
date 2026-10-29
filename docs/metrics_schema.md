# 결과 파일 스키마

생성: `src/evaluate.py --config configs/<exp>.yaml` → `results/<exp>/metrics.json`, `predictions_{val,test}.csv`.
`src/make_leaderboard.py`가 `results/*/metrics.json`만 읽어 `results/LEADERBOARD.md`를 만든다 (`smoke_*` 제외).
라벨 공간은 `configs/labels.yaml`의 `label_fine` 14개 (background 마지막).

## metrics.json 공통 키

| 키 | 타입 | 설명 |
|---|---|---|
| `experiment` | str | 실험명 = 디렉터리명 = config `exp_name` |
| `model` | str | `efficientat` / `yamnet` / `mnv4` / ... |
| `condition` | str | `generalist` / `specialist` / `ensemble` (leaderboard 표 선택용) |
| `mode` | str | `generalist` / `specialist` |
| `group` | str/null | specialist일 때 group_set (`semantic` / `best`) |
| `classes` | list | 모델 출력 순서. generalist = 14 labels, specialist = 담당 k + `other` |
| `date` | str | YYYY-MM-DD |
| `best_epoch`, `best_val_macro_f1` | int, float | 학습 시 선택된 체크포인트 |
| `config` | dict | 학습 config 전체 |
| `val`, `test` | dict | split별 지표 (아래) |
| `accuracy`, `macro_f1`, `danger_recall`, `background_fa_rate`, `bg_fa_strict` | float | **test** 값 복사본 (leaderboard 호환, `danger_recall` = `test.emergency_recall`) |
| `operating_point` | dict | 선택. `{rule, threshold, emergency_recall, precision, fa_per_hour}` (표 D) |

## 융합(`src/fuse.py`) 전용 키

| 키 | 설명 |
|---|---|
| `condition` | `ensemble` |
| `mode` | `generalist_fusion` / `specialist_fusion` |
| `method` | `hard_vote` / `soft_avg` / `weighted_soft` / `stacking` / `best_single` / `rule` / `gated` / `stacked` / `oracle` |
| `members` | 멤버 실험명 목록 |
| `tag` | 예: `premusan` (증강 전 멤버로 만든 결과) |
| `fit_info` | val에서 피팅한 값: temperature, val_macro_f1, weights, best_single, groups |
| `operating_point` | 표 D. `{rule, thresholds{class: tau}, threshold(평균), emergency_recall, precision, bg_fa_rate, bg_fa_strict, fa_per_hour, macro_f1, accuracy}`. val에서 클래스별 tau를 정해 test에 적용. `fa_per_hour`는 bg FA율 × 1800(2초 클립/시간) 프록시 |
| `val`/`test`/`noisy_snr*` | generalist 블록과 동일 (+ `operating_point`) |

## generalist `val`/`test` 블록

| 키 | 설명 |
|---|---|
| `accuracy`, `macro_f1` | 14클래스 argmax |
| `emergency_recall` | `labels.yaml: emergency` (alarm, fire_alarm, scream, cry, glass_break, gunshot, car_horn) 샘플의 micro recall |
| `background_fa_rate` | background 정답 중 비-background 예측 비율 |
| `bg_fa_strict` | 그중 peak 100ms-세그먼트 RMS < -40 dBFS인 "진짜 무음" 부분집합(`data/splits/bg_strict.csv`, `src/bg_strict.py`)의 FA율. `n_bg_strict` = 부분집합 크기 (test 760 / val 826) |
| `per_class` | `{label: {precision, recall, f1, support}}` |
| `confusion_matrix` | 14×14, `classes` 순서, 행=정답 열=예측 |
| `cry_babycry_confusion` | `{cry_as_baby_cry, baby_cry_as_cry, cry_support, baby_cry_support}` |

## specialist `val`/`test` 블록

| 키 | 설명 |
|---|---|
| `accuracy` | k+1 공간 argmax 정확도 |
| `macro_f1` | **담당 클래스만**의 macro-F1 (other 제외) |
| `own_class` | `{label: {precision, recall, f1, support}}` 담당 클래스 |
| `other` | other 클래스의 P/R/F1 |
| `reject_rate_non_target_events` | 비담당 **이벤트** 정답 중 `other`로 예측된 비율 |
| `reject_rate_background` | background 정답 중 `other`로 예측된 비율 |
| `reject_rate_by_origin` | 원래 14클래스 라벨별 거절률 |
| `confusion_matrix` | (k+1)×(k+1) |

## predictions_{val,test}.csv

generalist: `filepath, label_fine, split, pred, prob_<label>×14`.
specialist (14클래스 공간으로 투영, 융합 입력용): `filepath, label_fine(원래 14클래스), label_group(담당/other), split, pred, prob_<label>×14 (담당 클래스만 값, 나머지 빈칸=NaN), prob_other`.

## logs/<exp>.summary.md

train.py가 에폭 표(`epoch, train_loss, val_loss, val_macro_f1, val_acc, lr, sec, best`)를 append, evaluate.py가 split별 요약 + confusion matrix를 append.

## 과거 스키마와의 차이
초기 스키마의 `danger_recall`(5클래스)은 `emergency_recall`(7클래스, cry 포함)로 대체. 최상위 `danger_recall` 키는 호환용으로 유지.
