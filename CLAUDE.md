# 소리인식 키링 — 스페셜리스트 앙상블

## 환경
- OS: Windows 11. Claude Code 셸은 **Git Bash** (`/bin/bash.exe`, MSYS). PowerShell 아님.
- Python: conda env `miimo` (py3.11). 절대경로 `C:\Users\Gamzadole\anaconda3\envs\miimo\python.exe`
  (Git Bash: `/c/Users/Gamzadole/anaconda3/envs/miimo/python.exe`).
  PATH 첫 `python`은 WindowsApps 스텁이라 쓰지 말 것. base env의 numpy 충돌은 건드리지 않는다.
- GPU: RTX 4060 Ti 8GB. 큰 모델은 batch 축소 또는 fp16.

## 실행 규칙
- 긴 작업(다운로드/전처리/학습)은 전부 Git Bash `nohup` 백그라운드로 실행:
  ```bash
  nohup /c/Users/Gamzadole/anaconda3/envs/miimo/python.exe src/<script>.py ... > logs/<작업명>.log 2>&1 &
  ```
  실행 후 완료를 기다리지 않는다. 명령과 로그 경로만 보고한다.
- 사용자가 명시적으로 시키기 전에는 학습을 시작하지 않는다.

## 실험 큐
- 전체 실험은 `configs/queue.yaml` + `src/run_queue.py`로 돌린다 (gpu 동시 2, 완료 판정 = `results/<name>/metrics.json`, 재실행 시 완료 단계 skip).
  시작: `nohup python src/run_queue.py --queue configs/queue.yaml > logs/queue/run.log 2>&1 &`. 상태: `python src/run_queue.py --status`.
  단계마다 evaluate(clean+noisy) → make_leaderboard → PROGRESS.md → `exp(<name>): ...` 커밋·푸시를 큐가 자동으로 한다.
- 라벨 v2 (S_103 alarm → fire_alarm). v1 결과는 `label_version: v1`로만 참고. v1 configs는 `configs/v1/`.

## 진행 기록
- 작업 상태가 바뀔 때마다 `PROGRESS.md`에 append:
  ```
  ## [YYYY-MM-DD HH:MM] 작업명
  - 작업: ...
  - 결과: ...
  - 다음 할 일: ...
  ```

## 데이터
- 분할은 반드시 `source_file` 단위 `GroupKFold`. 클립 단위 분할 금지.
- val/test는 `is_augmented == 0`인 orig 클립만 사용.
- **모든 학습/평가는 `data/splits/manifest.csv`의 `split` 컬럼만 사용한다. 재분할 금지.** (생성: `src/make_splits.py`, 요약: `docs/split_summary.md`)
  test는 최종 보고 외 사용 금지. val은 캘리브레이션/임계값/스태킹 용도. 상세: `docs/experiment_protocol.md`.
- 파일 경로: `clip_metadata.csv`의 `filepath`는 NFC, 디스크는 NFD(한글 파일명). 경로 직접 조합 금지,
  `unicodedata.normalize("NFD", ...)` 폴백 필수 (`src/verify_dataset.py`의 `resolve()` 재사용).
- 학습/평가 라벨은 `configs/labels.yaml`의 `label_fine` 14개 (baby_cry를 출처로 cry/baby_cry 분리). 원래 13개 `label`은 참고용.
- 학습: `python src/train.py --config configs/<exp>.yaml` → `python src/evaluate.py --config ...` → `python src/make_leaderboard.py`.
  전체 학습 전 `configs/smoke*.yaml`로 스모크 통과 필수.
- 라벨 13개 (원본 `label`, 고정 순서):
  `alarm, fire_alarm, water, scream, glass_break, bicycle, gunshot, baby_cry, car_horn, cat_meow, dog_bark, knock, background`

## 실험 종료 체크리스트
실험 하나를 끝낼 때마다 아래를 만들고 커밋한다:
1. `results/<실험명>/metrics.json` + `results/<실험명>/predictions.csv` (스키마: `docs/metrics_schema.md`)
2. `logs/<실험명>.summary.md` — 에폭별 loss / val macro-F1 표 + 최종 confusion matrix
3. `PROGRESS.md` 항목
4. 커밋 전 `python src/make_leaderboard.py` 실행해 `results/LEADERBOARD.md` 갱신

## Git
- 커밋 메시지: `exp(<실험명>): <한 줄 결과>` 또는 `feat/fix/docs/chore: ...`
- 기능 추가는 `feat/<기능명>` 브랜치에서 작업 후 `main`에 머지.
- 커밋 메시지에 AI 생성 표시/트레일러(`Co-Authored-By: Claude`, `Generated with Claude Code` 등)를 넣지 않는다.
  `.claude/settings.json`의 `includeCoAuthoredBy: false`로 강제.
- remote: https://github.com/26-DGU-CECD/ModelExperiment.git

## 디렉터리
- `data/` 원본/전처리 데이터 (git 제외)
- `logs/` 백그라운드 로그 (`*.log` git 제외, `*.summary.md` 포함)
- `results/` 실험 결과 + `LEADERBOARD.md`
- `src/` 코드
- `configs/` 실험 설정
- `docs/` 문서
