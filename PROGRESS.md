# PROGRESS

## [2026-10-29 17:20] 환경 조사 + 뼈대 세팅
- 작업: 환경 조사(GPU/디스크/RAM/CPU/python/패키지), 디렉터리 생성, CLAUDE.md 작성
- 결과:
  | 항목 | 값 |
  |---|---|
  | GPU | NVIDIA GeForce RTX 4060 Ti ×1, 8 GB VRAM, driver 610.88, CUDA UMD 13.3 |
  | nvcc | 없음 (CUDA toolkit 미설치, pip torch는 자체 런타임 포함이라 무관) |
  | 디스크 D: | 377G 중 40G 여유 (90% 사용) — **50GB 요구 미달** |
  | 디스크 C: | 477G 중 101G 여유 |
  | RAM | 32 GB |
  | CPU | i5-12400F, 6코어 12스레드 |
  | Python | anaconda3 base 3.11.7, env `depth` 3.11.15 |
  | 환경관리 | conda 24.1.2, uv 0.11.29, venv 사용 가능 |
  | 설치됨 | pandas 2.2.3 (base, numpy 2.4.6과 충돌로 import 실패) |
  | 미설치 | torch, torchaudio, tensorflow, tensorflow_hub, timm, librosa, soundfile, huggingface_hub, scikit-learn |
- 다음 할 일:
  - 디스크 결정: D: 40G로는 부족. C:에 data/ 두거나 D: 정리(10GB+) 필요
  - 새 conda/uv 환경 생성 후 패키지 설치 (아직 미실행)
  - 데이터 다운로드는 사용자 승인 후

## [2026-10-29 17:25] 환경 재조사
- 작업: 환경 조사 재실행 (GPU/디스크/RAM/CPU/python/패키지)
- 결과: 디스크 D: 여유 40G → **161G** (377G 중 217G 사용, 58%)로 변동. 나머지 항목 이전과 동일.
  50GB 요구 충족. 패키지 미설치 상태 동일 (torch, torchaudio, tensorflow, tensorflow_hub, timm, librosa, soundfile, huggingface_hub, scikit-learn).
- 다음 할 일:
  - 프로젝트 전용 conda/uv 환경 생성 후 패키지 설치 (사용자 지시 대기)
  - 데이터 다운로드는 사용자 승인 후

## [2026-10-29 17:40] Windows 맞춤 수정 + GitHub 연결
- 작업: CLAUDE.md Git Bash nohup 규칙으로 수정, 실험 체크리스트/커밋 규칙 추가, .gitignore,
  src/make_leaderboard.py, docs/metrics_schema.md 작성, conda env `miimo` 생성 + 패키지 설치, git init + remote
- 결과: (설치/push 결과는 아래 항목에 기록)
- 다음 할 일: 데이터 다운로드 (사용자 승인 후)

## [2026-10-29 18:05] conda env miimo 설치 완료
- 작업: conda env `miimo` (py3.11) 생성, requirements.txt 설치
- 결과:
  - 첫 설치 시 torch가 CPU 휠로 잡힘 (`--extra-index-url`은 PyPI 우선). cu124 인덱스는 torch 2.6.0까지만 있어 cu126으로 재설치.
  - torch 2.14.1+cu126, `torch.cuda.is_available()==True`, RTX 4060 Ti matmul 확인.
  - tensorflow-cpu 2.21.0 + tensorflow_hub 0.16.1 (CPU). setuptools 82+가 `pkg_resources` 제거해 hub import 실패 → `setuptools<81`로 고정.
  - requirements.txt 버전 고정. 로그: logs/env_setup.log, logs/env_setup_torch_cu126.log
- 다음 할 일: git 첫 커밋 + push, 데이터 다운로드 (사용자 승인 후)

## [2026-10-29 17:35] 커밋 AI 표시 제거 + 데이터셋 조사/다운로드 시작
- 작업: `.claude/settings.json` includeCoAuthoredBy=false, CLAUDE.md 규칙 추가, 기존 커밋 1개 amend 후 force-with-lease push.
  HF `retrina0678/miimo-audio-dataset` 파일 목록 조사, docs/dataset_notes.md, src/verify_dataset.py 작성, 다운로드 시작.
- 결과:
  - git log 깨끗함 (`e00ddae chore: project scaffold`, 트레일러 없음).
  - HF 총 86,623 파일 / 12.84 GB. D: 여유 163 GB, 충분. clip_metadata.csv / README.md / generate_musan_mixes.py 존재.
  - musan_mixed_2s는 README상 240k/29GB지만 HF에는 fire_alarm 3,583개(0.46GB)만 있음 (업로드 미완).
  - huggingface_hub 2.x는 CLI 이름이 `hf` (`huggingface-cli` 없음). `hf download ... --local-dir data/miimo`, 로그 logs/download.log.
- 다음 할 일: 다운로드 완료 후 `python src/verify_dataset.py` 실행, results/dataset_verify.json 확인.
