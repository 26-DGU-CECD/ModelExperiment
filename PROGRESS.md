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

## [2026-10-29 18:10] 다운로드 가속: hf CLI → src/download_dataset.py
- 작업: HF 토큰 로그인(.env HF_READ, 계정 gamzadole), `hf download` 16/64 워커 재시작, 속도 진단, 전용 다운로더 작성.
- 결과:
  - `hf download`는 워커 수 무관 약 5 files/s (로그에 429 없음). 직접 HTTP GET은 16→14.6/s, 32→28.8/s 선형 확장 → CLI 내부 병목.
  - 파일은 LFS/xet-bridge 128KB, CDN 미국. hf_xet 미사용.
  - `src/download_dataset.py --workers 64`: 62.8 files/s, 8 MB/s, todo 76,040 (9.74GB), ETA 약 20분. 이어받기(크기 일치 파일 skip).
  - 제외: `musan_mixed_2s/*` (HF에 fire_alarm만 있음), `*/raw/*` (학습 불필요). 목표 80,261 파일.
- 다음 할 일: 완료 후 `python src/verify_dataset.py` 실행, results/dataset_verify.json 확인.

## [2026-10-29 19:15] 데이터 다운로드 완료 + 검증 통과
- 작업: per-file resolver 한도(5000/300s) 회피용으로 download_dataset.py를 git-LFS batch API 방식으로 교체. 38.4분, 24 files/s. 실패 193개는 전부 비-wav(끝 공백 폴더 `esc50 /`, `data_augmented /`) → 경로 strip 패치 후 재실행 중. verify_dataset.py 실행.
- 결과:
  - wav 80,049 / 80,049 (CSV 행 수와 일치). data/miimo 약 10GB.
  - 첫 verify에서 474개 "누락"은 CSV(NFC) vs 디스크(NFD) 정규화 차이. verify에 NFC/NFD 폴백 추가 후 0 missing.
  - 라벨별 클립 수·독립 source_file 수 README와 전부 일치. orig:aug = 이벤트 1:2, background 1:1. 오디오 포맷 130개 샘플 이상 없음.
  - results/dataset_verify.json 저장. 로그 logs/verify_dataset.log.
- 다음 할 일: 비-wav 재다운로드 완료 확인. GroupKFold 분할 스크립트 / 베이스라인 설계 (사용자 지시 대기).

## [2026-10-29 19:40] feat/splits: 소스 단위 분할 + 실험 프로토콜
- 작업: src/make_splits.py 작성·실행, docs/split_summary.md, docs/experiment_protocol.md, CLAUDE.md 분할 규칙, generate_musan_mixes.py 옵션 조사.
- 결과:
  - manifest 59,699행 (train 48,060 orig+aug / val 5,762 / test 5,877 orig만). source 2,073 = train 1,243 / val 415 / test 415. 누수 assert 3종 통과. test source < 10인 라벨 없음 (최소 car_horn 12).
  - clip_metadata.csv의 filepath는 NFD로 치환해 저장 (디스크 실존 경로).
  - generate_musan_mixes.py: `--metadata`로 CSV 바꿔도 `*/clips_2s/*.wav` 전체를 glob해 합치므로 클립 서브셋 지정 불가 → `--only` 옵션 추가 필요. noise는 `--musan-root` 아래 전부 사용, train/test 분리 옵션 없음 → 루트 폴더 두 개로 분리 운용. MUSAN noise HF `FluidInference/musan` 777파일 약 585MB. SNR은 `--snrs 20 15 10`.
- 다음 할 일: main 머지. 비-wav 재다운로드 확인. E0 베이스라인 설계 (사용자 지시 대기).

## [2026-10-29 20:40] feat/train-framework: 학습 프레임워크 + 스모크 통과
- 작업: label_fine(cry/baby_cry) 추가, configs/labels.yaml·groups.yaml, src/data.py, src/models/(efficientat, mnv4·yamnet 스텁), src/train.py, src/evaluate.py, make_leaderboard 4표, docs(metrics_schema, experiment_protocol 7~10절, third_party), 스모크 2종.
- 결과:
  - 스모크 generalist(14클래스)·specialist(caution, 5클래스) 모두 train→evaluate 통과. results/smoke_*/ (git 제외).
  - EfficientAT a425fdc clone, mn10_as 프리트레인 checkpoints/pretrained/mn10_as_mAP_471.pt (19.7MB) 자동 다운로드. 파라미터 4.22M.
  - 처리량 batch 64 AMP: 42 ms/step, 656 step/epoch(cap 3000×14) → 학습 약 0.5분 + val 약 0.2분 = **약 1분/epoch**, 30 epoch ≤ 40분. VRAM 최대 1.03 GB.
  - 팀원 모델 retrina0678/miimo-efficientat-target4: mn10_as + mlp head, 32kHz/128mel, 4클래스, 학습 코드 없음(체크포인트·리포트만). 설정값만 참고.
  - 함정: EfficientAT `helpers.utils`가 cwd 상대 metadata를 읽어 import 시 chdir 필요. Windows DataLoader 워커는 stdin 스크립트에서 못 돎(파일로 실행).
- 다음 할 일: 사용자 "E0 시작" 지시 시 configs/E0_efficientat_generalist.yaml 백그라운드 학습.

## [2026-10-29 21:20] feat/models: mnv4 / yamnet 래퍼 + KD 모드
- 작업: src/models/mnv4.py (timm mobilenetv4_conv_small ImageNet, in_chans=1, 16kHz 64mel hop160), src/models/yamnet.py (frozen: TF-Hub 임베딩 캐시 + MLP, ft: torch_audioset 포트 전체 fine-tune), src/cache_yamnet_emb.py, train.py KD(--teacher, 0.5 CE + 0.5 KL T=3), configs E1/E1k/E2/E2k/S1/S2/S3/A1 + smoke 6종.
- 결과:
  - 스모크 전부 통과: mnv4 gen/spec, yamnet_frozen gen/spec, yamnet_ft gen, KD(mnv4 ← E0 best.pt).
  - yamnet_ft 가능. torch_audioset(daed697) `yamnet.pth`를 TF-Hub와 비교: 0.96s 패치 2개 입력 시 임베딩 상관 0.914(최소 0.43), AudioSet top-1 일치 11/16. 2초 통째 입력은 0.67이라 패치 모드 채택. 비트 일치는 아니지만 fine-tune 초기화로 충분.
  - YAMNet 임베딩 캐시 data/cache/yamnet_emb/{train,val,test}.npy (CPU 80 clips/s, 전체 약 13분).
  - 함정: fp16 autocast 안에서 power-mel이 overflow → NaN loss. mel 프론트엔드는 autocast 끄고 fp32 (mnv4, yamnet_ft 적용). ImageNet 분류기 초기값 때문에 mnv4 초기 loss 5.6은 정상.
  - groups.yaml 키는 모델 베이스명(yamnet_frozen/yamnet_ft → yamnet). `group_model`로 override 가능.
- 다음 할 일: E0 평가·커밋. 이후 E1/E2/E2k/S1~S3 순차 실행 (사용자 지시 대기).

## [2026-10-29 21:25] exp E0_efficientat_generalist 완료
- 작업: mn10_as 14클래스 fine-tune, 30 epoch(early stop 안 걸림), batch 64 AMP, cap 3000/class, mixup 0.3, SpecAug 48/192. 약 38s/epoch, VRAM 1.03GB.
- 결과: best epoch 27, val macro-F1 0.8848 / **test macro-F1 0.8844**, acc 0.872, 긴급 recall 0.855, bg FA 0.185.
  - 약한 클래스(test F1): car_horn 0.595, fire_alarm 0.656, alarm 0.752. 최대 혼동 alarm→fire_alarm 380건. background→water 64, →glass_break 41.
  - cry/baby_cry 혼동: cry→baby_cry 0, baby_cry→cry 2 (support 411/196). 출처 분리는 쉽게 학습됨.
  - 강한 클래스: dog_bark 0.981, scream 0.964, glass_break 0.960, knock 0.954, baby_cry 0.950.
- 다음 할 일: E1(yamnet frozen), E2(mnv4), E2k(KD) 실행 후 per-class 진단으로 groups.yaml best 채우기.

## [2026-10-29 21:55] exp E1_yamnet_generalist 완료
- 작업: TF-Hub YAMNet 임베딩(캐시) + MLP 헤드, lr 1e-3, early stop epoch 42 (patience 10), best epoch 32. 수 초/epoch, VRAM 0.03GB.
- 결과: val macro-F1 0.8384 / **test macro-F1 0.8095**, acc 0.813, 긴급 recall 0.798, bg FA 0.211. E0 대비 -0.075.
  - 약한 클래스: car_horn 0.463, fire_alarm 0.630, alarm 0.744, cat_meow 0.768. E0와 같은 약점 + cat_meow/gunshot 추가 하락.
  - 강한 클래스: dog_bark 0.924, glass_break 0.914, scream 0.903.
- 다음 할 일: E2 완료 대기, noisy 평가.

## [2026-10-29 22:20] exp E2_mnv4_generalist 완료
- 작업: timm mobilenetv4_conv_small(ImageNet, in_chans=1) + 16kHz 64mel/hop160, 30 epoch (early stop 없음, best 26), 약 1분/epoch, VRAM 0.24GB.
- 결과: val macro-F1 0.8812 / **test macro-F1 0.8706**, acc 0.851, 긴급 recall 0.827, bg FA 0.137 (E0 0.185보다 낮음).
  - 약한 클래스: fire_alarm 0.636, car_horn 0.679, alarm 0.753 (E0와 같은 약점). cry 0.918(E0 0.944).
  - E0보다 나은 클래스: glass_break 0.966, car_horn 0.679(E0 0.595), bg FA.
  - noisy: SNR20 0.796 / SNR15 0.768 / SNR10 0.695. E0(0.861/0.830/0.778)보다 잡음에 훨씬 약함 (ImageNet 프리트레인 + 작은 mel).
- 다음 할 일: E0~E2 per-class 비교로 groups.yaml best 채우기, E2k(KD) 실행.
