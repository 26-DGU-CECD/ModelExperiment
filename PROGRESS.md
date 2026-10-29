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

## [2026-10-29 22:35] feat/musan: MUSAN noisy 테스트셋 + 온라인 노이즈 훅
- 작업: src/download_musan.py (HF FluidInference/musan noise 774파일, seed 42 파일 단위 80/20 → data/musan_train 619 / data/musan_test 155, 하드링크, data/musan/noise_split.csv),
  src/musan_mix.py (원본 + `--only`, `--output-strip`), test orig 5,877 × SNR 20/15/10 = 17,631 → data/test_noisy/, data/splits/manifest_test_noisy.csv,
  verify_musan_mixes.py 통과(17,631/17,631, SNR 오차 0), src/data.py MusanMixer(기본 off, aug.musan/musan_prob/musan_snr_range), build_noisy_test,
  evaluate.py `--eval-set clean|noisy|all` (metrics.json noisy_snr20/15/10), cache_yamnet_emb.py noisy 세트 지원, leaderboard 표 C에 noisy SNR10 열.
- 결과 (test macro-F1, clean / SNR20 / SNR15 / SNR10):
  | 실험 | clean | 20 | 15 | 10 |
  |---|---|---|---|---|
  | E0 efficientat | 0.884 | 0.861 | 0.830 | 0.778 |
  | E2 mnv4 | 0.871 | 0.796 | 0.768 | 0.695 |
  | E1 yamnet frozen | 0.810 | 0.658 | 0.600 | 0.533 |
  - E0 SNR10 클래스별 F1 하락 최대: knock 0.954→0.545, car_horn 0.595→0.447, cat_meow 0.942→0.804. bg FA 0.185→0.345.
  - E0 조사 (docs/e0_alarm_water_confusions.md): alarm→water는 0건. background→water 64건은 21개 소스, 상위 3개 소스가 24/64(38%),
    61/64가 원래 water 소스(`물소리__` 접두어)의 무음 판정 클립. 즉 "조용한 물소리"를 background로 라벨한 클립이 water로 예측됨 — 라벨 경계 문제.
  - 함정: musan_mix `--only`가 label_fine을 label로 넣어 verify가 불일치 보고 → mix_metadata label을 원본 label로 통일. yamnet_frozen은 noisy 임베딩 캐시 필요(추가).
- 다음 할 일: E2k(KD), S1~S3, groups.yaml best 결정.

## [2026-10-29 23:30] feat/fusion: 융합 방법 + strict bg FA + best 배정 스크립트
- 작업: src/fuse.py (범용 hard/soft/weighted/stacking/best_single, 스페셜리스트 rule/gated/stacked/oracle, 운영점 표 D, clean+noisy 전부),
  src/bg_strict.py → data/splits/bg_strict.csv (peak RMS < -40 dBFS: test 760/1410, val 826/1518), evaluate.py `bg_fa_strict`, 표 C/D 열 추가,
  src/assign_best.py (val per-class F1 argmax → groups.yaml best + docs/assignment_best.md; 담당 0개 모델 제외), 문서 갱신.
- 결과 (pre-musan, 멤버 E0/E1/E2, test macro-F1 / bg FA / strict / SNR10):
  | 융합 | macro-F1 | bg FA | strict | SNR10 |
  |---|---|---|---|---|
  | best_single (E0) | 0.8844 | 0.185 | 0.011 | 0.778 |
  | hard_vote | 0.8842 | 0.157 | 0.004 | 0.777 |
  | soft_avg | 0.8895 | 0.145 | 0.004 | 0.781 |
  | weighted_soft | **0.8898** | 0.145 | 0.004 | 0.782 |
  | stacking | 0.8862 | **0.121** | **0.001** | **0.784** |
  - 앙상블 이득 +0.005 (약함: E1이 전 클래스 열세, E0/E2 오류가 상관). bg FA와 noisy에서는 stacking이 가장 좋음.
  - strict bg FA가 전체 bg FA의 1/20 수준 → background 오경보 대부분은 -40~-30 dBFS "소리 있는 배경"(물소리 등)에서 발생.
  - 운영점(soft_avg): 긴급 recall 0.829(목표 0.95 미달 — alarm→fire_alarm 혼동은 임계값으로 못 고침), bg FA 0.152, FA/hour 프록시 274.
  - E0 긴급 쌍 혼동: alarm→fire_alarm 380 / fire_alarm→alarm 25 / alarm→car_horn 20 / 그 외 0. 380건 전부 시나리오 S_103(412개 중 92%), 27개 소스 100% 오분류. 라벨 경계 문제로 판단 (docs/e0_alarm_water_confusions.md).
  - assign_best 드라이런(E0/E1/E2): efficientat {alarm, water, scream, gunshot, cry}, mnv4 {나머지 8}, yamnet 0개 → 2-모델. 실제 배정은 E0m/E1k/E2k 완료 후.
- 다음 할 일: E0m/E2k/E1k 완료 → evaluate 커밋 → assign_best → S*/SB* 학습.

## [2026-10-30 00:10] exp E0m_efficientat_generalist_musan / E2k_mnv4_kd 완료
- 작업: E0m = E0 + MUSAN 온라인 증강(p 0.5, SNR 5~20), 20 epoch(best 14). E2k = mnv4 + KD(teacher E0 best.pt, 0.5 CE + 0.5 KL T=3) + MUSAN 증강, 20 epoch(best 16).
- 결과 (test macro-F1 clean / SNR20 / SNR15 / SNR10, bg FA):
  | 실험 | clean | 20 | 15 | 10 | bg FA | strict |
  |---|---|---|---|---|---|---|
  | E0 (참고) | 0.884 | 0.861 | 0.830 | 0.778 | 0.185 | 0.011 |
  | **E0m** | 0.870 | 0.855 | 0.843 | **0.821** | 0.169 | 0.013 |
  | E2 (참고) | 0.871 | 0.796 | 0.768 | 0.695 | 0.137 | 0.011 |
  | **E2k** | 0.869 | 0.831 | 0.823 | **0.807** | 0.186 | 0.030 |
  - E0m: clean -0.015 (knock -0.08, car_horn -0.056이 대부분), SNR10 +0.043. 20 epoch 제한도 영향 가능(E0는 30).
  - E2k: clean 동일, SNR10 **+0.11**. KD + 증강으로 잡음 강건성이 E0m 수준까지. 단 bg FA 0.137→0.186, strict 0.011→0.030 악화 (KD가 teacher의 bg 과민을 전이한 듯).
- 다음 할 일: E1k 학습 중(큐). 완료 후 assign_best(E0m, E1k, E2k).

## [2026-10-30 01:00] exp E1k_yamnet_kd 완료 (v1 라벨, 참고용) + best 배정(v1)
- 작업: yamnet_ft(torch_audioset 포트) + KD(teacher E0) + MUSAN 증강, early stop epoch 14 (best 8), VRAM 0.66GB. assign_best(E0m, E1k, E2k).
- 결과: val 0.8798 / **test macro-F1 0.8517** (E1 frozen 0.8095 대비 +0.042), bg FA **0.132**(최저), strict 0.012, noisy SNR20/15/10 = 0.830 / 0.822 / 0.780 (E1 0.658/0.600/0.533).
  - per-class 상승: gunshot +0.11, cat_meow +0.09, bg +0.07, water/baby_cry/knock +0.06. dog_bark -0.07.
  - best 배정(v1, docs/assignment_best.md): efficientat {alarm, scream, glass_break, cry, cat_meow}, yamnet {water, gunshot, baby_cry, knock}, mnv4 {fire_alarm, bicycle, car_horn, dog_bark}.
  - **v1 라벨 결과는 참고용**: S_103 재라벨 후 큐에서 *_v2로 전부 재학습. E1k 체크포인트는 큐에서 재사용하지 않음.

## [2026-10-30 01:10] S_103 조사 + 그룹 지표 + 라벨 수정 스크립트 (4-3.5 [2],[3] 마무리)
- 작업: docs/listen/ 청취 세트 15개(A_s103_alarm_wrong 5, B_alarm_other_scen 5, C_fire_alarm 5; wav는 git 제외, README.md만),
  evaluate/fuse/leaderboard에 그룹 단위 지표(group_recall/precision: 긴급/주의/일상/bg; 표 C/D 열) 추가 후 v1 실험 전부 재평가, src/relabel.py (--mode relabel_s103 | merge_siren), metrics.json `label_version` 키 + 리더보드 `labels` 열 (기존 결과 전부 v1 스탬프).
- 결과:
  - 시나리오 코드 설명은 repo 문서/CSV에 없음. 파일명 규칙으로 추정: 문자 = 대분류(S 경보, H 사람, L 생활, O 물체, W 무기). **fire_alarm 소스 167개 전부 S_103**, alarm은 S_101 97 / S_102 132 / S_103 166.
  - alarm 시나리오별 E0 test recall: S_101 0.928, S_102 0.988, **S_103 0.061** (412클립 중 380 fire_alarm 예측).
  - 청취 결과(사용자): S_103 alarm = 화재경보음, 다른 시나리오 alarm = 차량 사이렌 → **relabel_s103 확정**.
- 다음 할 일: feat/relabel에서 relabel_s103 실행, 라벨 감사, 큐 구축.

## [2026-10-30 01:30] feat/relabel: v2 라벨 (S_103 alarm → fire_alarm)
- 작업: `src/relabel.py --mode relabel_s103` 실행 (백업 data/splits/manifest_v1.csv), configs/labels.yaml version v2, docs/split_summary.md 재생성, src/label_audit.py → docs/label_audit.md, 프로토콜 v2 라벨 절.
- 결과: 4,570클립 / 166소스 변경 (train 3,777 / val 381 / test 412; 소스 103 / 32 / 31). alarm 11,714→7,144 (소스 395→229), fire_alarm 4,558→9,128 (소스 167→169). split/fold 불변.
  - S_103 alarm 소스 166개 중 164개가 fire_alarm 소스와 이름 동일(오디오 상이) → 같은 fold였음, 누수 없음.
  - 라벨 감사(E0 v1, F1* < 0.6): alarm/S_103 0.107 외 background/S_202 0.578, background/W_102 0.514 (조용한 bicycle/gunshot → 이벤트 예측; 무음 판정 경계 문제).
- 다음 할 일: feat/queue 큐 구축 후 *_v2 재학습.

## [2026-10-29 22:20] feat/queue: 실험 큐 구축 (v2 재학습)
- 작업: src/run_queue.py (단계 = name/cmd/depends_on/gpu/post, gpu 동시 2, 완료 = results/<name>/metrics.json, 실패 시 의존 단계만 중단, 완료 후 evaluate(clean+noisy)→leaderboard→PROGRESS→exp 커밋·푸시 자동),
  configs/queue.yaml (28단계), v2 configs (E0m_v2, E2k_v2, E1k_v2, E1_v2, S1~S3, A1, A2_*_random; 전부 aug.musan true, max 20 epoch), train.py `init_from`(S3 ← E2k_v2),
  src/make_random_groups.py(A2), src/make_sb_configs.py(best≠semantic만 SB 생성), src/fuse_best.py, src/results_summary.py(docs/results_summary.md). v1 configs → configs/v1/.
- 결과: dry-run 통과. 큐 시작 후 로그 logs/queue/run.log, 단계별 logs/queue/<name>.log, 상태 `python src/run_queue.py --status`.
- 다음 할 일: 큐 완료 대기, 중간에 "진행 상황" 요청 시 상태표 + 리더보드.

## [2026-10-29 22:16] queue: E1_v2
- 작업: `{PY} -u -W ignore src/train.py --config configs/E1_v2.yaml`
- 결과: test macro-F1 0.8578, emerg recall 0.921, group 0.957, bg FA 0.223, SNR10 0.530
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 22:27] queue: E1_v2
- 작업: `{PY} -u -W ignore src/train.py --config configs/E1_v2.yaml`
- 결과: test macro-F1 0.8578, emerg recall 0.921, group 0.957, bg FA 0.223, SNR10 0.530
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 22:38] queue: E0m_v2
- 작업: `{PY} -u -W ignore src/train.py --config configs/E0m_v2.yaml`
- 결과: test macro-F1 0.9170, emerg recall 0.970, group 0.986, bg FA 0.176, SNR10 0.825
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 22:52] queue: E2k_v2
- 작업: `{PY} -u -W ignore src/train.py --config configs/E2k_v2.yaml`
- 결과: test macro-F1 0.9100, emerg recall 0.955, group 0.961, bg FA 0.176, SNR10 0.818
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 22:58] queue: E1k_v2
- 작업: `{PY} -u -W ignore src/train.py --config configs/E1k_v2.yaml`
- 결과: test macro-F1 0.8833, emerg recall 0.955, group 0.975, bg FA 0.128, SNR10 0.796
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 22:58] queue: F_best_single
- 작업: `{PY} -u -W ignore src/fuse.py --name F_best_single --method best_single --exps E0m_v2 E1k_v2 E2k_v2`
- 결과: test macro-F1 0.8833, emerg recall 0.955, group 0.975, bg FA 0.128, SNR10 0.796
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 22:58] queue: F_generalist_hard
- 작업: `{PY} -u -W ignore src/fuse.py --name F_generalist_hard --method hard_vote --exps E0m_v2 E1k_v2 E2k_v2`
- 결과: test macro-F1 0.9103, emerg recall 0.969, group 0.984, bg FA 0.148, SNR10 0.834
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 22:58] queue: F_generalist_soft
- 작업: `{PY} -u -W ignore src/fuse.py --name F_generalist_soft --method soft_avg --exps E0m_v2 E1k_v2 E2k_v2`
- 결과: test macro-F1 0.9129, emerg recall 0.969, group 0.981, bg FA 0.141, SNR10 0.838
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 22:58] queue: F_generalist_weighted
- 작업: `{PY} -u -W ignore src/fuse.py --name F_generalist_weighted --method weighted_soft --exps E0m_v2 E1k_v2 E2k_v2`
- 결과: test macro-F1 0.9129, emerg recall 0.969, group 0.981, bg FA 0.141, SNR10 0.837
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 22:58] queue: F_generalist_stacking
- 작업: `{PY} -u -W ignore src/fuse.py --name F_generalist_stacking --method stacking --exps E0m_v2 E1k_v2 E2k_v2`
- 결과: test macro-F1 0.9217, emerg recall 0.968, group 0.978, bg FA 0.114, SNR10 0.855
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 22:58] queue: assign_best
- 작업: `{PY} -u src/assign_best.py --exps E0m_v2 E1k_v2 E2k_v2 && {PY} -u src/make_sb_configs.py && echo E0m_v2 E1k_v2 E2k_v2 > results/assign_best_v2.done`
- 결과: done
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 22:58] queue: overlap_hetero
- 작업: `{PY} -u -W ignore src/error_overlap.py --name overlap_hetero --exps E0m_v2 E1k_v2 E2k_v2`
- 결과: test macro-F1 0.9598, emerg recall 0.989, group 0.994, bg FA 0.093
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 23:04] queue: S2_yamnet_emergency
- 작업: `{PY} -u -W ignore src/train.py --config configs/S2_yamnet_emergency.yaml`
- 결과: test macro-F1 0.8516, SNR10 0.707, reject non-target 0.994 bg 0.955
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 23:06] queue: S1_efficientat_caution
- 작업: `{PY} -u -W ignore src/train.py --config configs/S1_efficientat_caution.yaml`
- 결과: test macro-F1 0.8896, SNR10 0.831, reject non-target 0.982 bg 0.813
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 23:09] queue: S3_mnv4_daily
- 작업: `{PY} -u -W ignore src/train.py --config configs/S3_mnv4_daily.yaml`
- 결과: test macro-F1 0.8685, SNR10 0.791, reject non-target 0.996 bg 0.922
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 23:09] queue: F_semantic_rule
- 작업: `{PY} -u -W ignore src/fuse.py --name F_semantic_rule --method rule --exps S1_efficientat_caution S2_yamnet_emergency S3_mnv4_daily`
- 결과: test macro-F1 0.8683, emerg recall 0.959, group 0.978, bg FA 0.310, SNR10 0.784
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 23:09] queue: F_semantic_gated
- 작업: `{PY} -u -W ignore src/fuse.py --name F_semantic_gated --method gated --exps S1_efficientat_caution S2_yamnet_emergency S3_mnv4_daily`
- 결과: test macro-F1 0.8734, emerg recall 0.956, group 0.973, bg FA 0.267, SNR10 0.792
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 23:09] queue: F_semantic_stacked
- 작업: `{PY} -u -W ignore src/fuse.py --name F_semantic_stacked --method stacked --exps S1_efficientat_caution S2_yamnet_emergency S3_mnv4_daily`
- 결과: test macro-F1 0.8775, emerg recall 0.952, group 0.966, bg FA 0.215, SNR10 0.797
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 23:09] queue: oracle_semantic
- 작업: `{PY} -u -W ignore src/fuse.py --name oracle_semantic --method oracle --exps S1_efficientat_caution S2_yamnet_emergency S3_mnv4_daily`
- 결과: test macro-F1 0.8747, emerg recall 0.961, group 0.979, bg FA 0.310, SNR10 0.799
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 23:15] queue: SB_yamnet_best
- 작업: `{PY} -u -W ignore src/train.py --config configs/SB_yamnet_best.yaml`
- 결과: test macro-F1 0.8877, SNR10 0.720, reject non-target 0.982 bg 0.974
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 23:52] queue: S2_yamnet_emergency
- 작업: `{PY} -u -W ignore src/train.py --config configs/S2_yamnet_emergency.yaml`
- 결과: test macro-F1 0.8461, SNR10 0.720, reject non-target 0.992 bg 0.970
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 23:50] 스페셜리스트 레시피 v2 + 운영점 주 지표 (feat/spec-recipe2 머지)
- 작업: naive S*/SB* 결과 → results/naive/(recipe: naive), 레시피 v2(범용 warm start, 백본 2e-5/헤드 1e-3, 14라벨 균형 샘플링, other smoothing 0.2, 그룹 objective CE 가중치),
  evaluate `vs_generalist` 표, src/opoint.py 공통 운영점(val strict FA ≤ 0.005, 클래스별 tau + FA 유발 클래스 greedy 인상, 비용 점수, 그룹 PR-AUC), 표 D 주 결과표, MLP 스태커(5-fold CV), car_horn 제외 열, docs/error_analysis_v2.md, H_mn04 동일 MACs 단계, 큐 재시작(S2부터).
- 결과:
  - S1 ft-v2 test: 담당 F1 bicycle 0.923 / baby_cry 0.946 / gunshot 0.916 / glass_break 0.965 (naive 0.89/0.88/0.88/0.91), bg 거절 0.913(naive 0.813). vs 범용 리매핑 Δ val +0.008 / test +0.003.
  - 운영점(test, val strict FA≤0.005): F_generalist_hard 비용 0.178 (긴급 recall 0.960, 일상 precision 0.914), soft/weighted 0.182, E0m_v2 0.187, stacking 0.193 (strict FA 0.0066), stacking_mlp 0.196 (strict FA 0.0026 최저). E2k_v2 0.633·E1_v2 0.869 — strict FA 맞추려 긴급 tau가 크게 올라 recall 0.80/0.71로 붕괴.
  - MLP 스태커 과적합(CV 0.957 vs fit 0.975), test 0.902 < 로지스틱 0.922 → oracle_any 갭은 메타분류기 용량 문제 아님.
  - E1k_v2 val→test −0.040 중 car_horn −0.444가 대부분; car_horn 제외 시 −0.009.
  - 첫 운영점 구현(전역 스케일)은 단일 모델 긴급 recall을 0.05로 붕괴시켜 greedy 클래스별 인상으로 교체.
- 다음 할 일: 큐 진행(S2 → S3 → 융합 → SB → A2 → 동질 → 요약).

## [2026-10-29 23:56] queue: S3_mnv4_daily
- 작업: `{PY} -u -W ignore src/train.py --config configs/S3_mnv4_daily.yaml`
- 결과: test macro-F1 0.9133, SNR10 0.840, reject non-target 0.999 bg 0.957
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 23:56] queue: F_semantic_rule
- 작업: `{PY} -u -W ignore src/fuse.py --name F_semantic_rule --method rule --exps S1_efficientat_caution S2_yamnet_emergency S3_mnv4_daily`
- 결과: test macro-F1 0.8898, emerg recall 0.946, group 0.972, bg FA 0.159, SNR10 0.815
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 23:56] queue: F_semantic_gated
- 작업: `{PY} -u -W ignore src/fuse.py --name F_semantic_gated --method gated --exps S1_efficientat_caution S2_yamnet_emergency S3_mnv4_daily`
- 결과: test macro-F1 0.8864, emerg recall 0.938, group 0.962, bg FA 0.133, SNR10 0.811
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 23:57] queue: F_semantic_stacked
- 작업: `{PY} -u -W ignore src/fuse.py --name F_semantic_stacked --method stacked --exps S1_efficientat_caution S2_yamnet_emergency S3_mnv4_daily`
- 결과: test macro-F1 0.8877, emerg recall 0.945, group 0.968, bg FA 0.134, SNR10 0.810
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-29 23:57] queue: oracle_semantic
- 작업: `{PY} -u -W ignore src/fuse.py --name oracle_semantic --method oracle --exps S1_efficientat_caution S2_yamnet_emergency S3_mnv4_daily`
- 결과: test macro-F1 0.8955, emerg recall 0.948, group 0.972, bg FA 0.159, SNR10 0.825
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-30 00:04] queue: F_semantic_rule
- 작업: `{PY} -u -W ignore src/fuse.py --name F_semantic_rule --method rule --exps S1_efficientat_caution S2_yamnet_emergency S3_mnv4_daily`
- 결과: test macro-F1 0.8898, emerg recall 0.946, group 0.972, bg FA 0.159, SNR10 0.815
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-30 00:04] queue: F_semantic_gated
- 작업: `{PY} -u -W ignore src/fuse.py --name F_semantic_gated --method gated --exps S1_efficientat_caution S2_yamnet_emergency S3_mnv4_daily`
- 결과: test macro-F1 0.8864, emerg recall 0.938, group 0.962, bg FA 0.133, SNR10 0.811
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-30 00:04] queue: F_semantic_stacked
- 작업: `{PY} -u -W ignore src/fuse.py --name F_semantic_stacked --method stacked --exps S1_efficientat_caution S2_yamnet_emergency S3_mnv4_daily`
- 결과: test macro-F1 0.8877, emerg recall 0.945, group 0.968, bg FA 0.134, SNR10 0.810
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-30 00:04] queue: oracle_semantic
- 작업: `{PY} -u -W ignore src/fuse.py --name oracle_semantic --method oracle --exps S1_efficientat_caution S2_yamnet_emergency S3_mnv4_daily`
- 결과: test macro-F1 0.8955, emerg recall 0.948, group 0.972, bg FA 0.159, SNR10 0.825
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-30 00:18] queue: SB_yamnet_best
- 작업: `{PY} -u -W ignore src/train.py --config configs/SB_yamnet_best.yaml`
- 결과: test macro-F1 0.9203, SNR10 0.829, reject non-target 0.992 bg 0.977
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-30 00:25] queue: SB_efficientat_best
- 작업: `{PY} -u -W ignore src/train.py --config configs/SB_efficientat_best.yaml`
- 결과: test macro-F1 0.9448, SNR10 0.919, reject non-target 0.990 bg 0.898
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-30 00:33] queue: SB_mnv4_best
- 작업: `{PY} -u -W ignore src/train.py --config configs/SB_mnv4_best.yaml`
- 결과: test macro-F1 0.8340, SNR10 0.722, reject non-target 0.999 bg 0.977
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)

## [2026-10-30 00:34] queue: A1_efficientat_scratch
- 작업: `{PY} -u -W ignore src/train.py --config configs/A1_efficientat_scratch.yaml`
- 결과: test macro-F1 0.9143, emerg recall 0.971, group 0.978, bg FA 0.164, SNR10 0.838
- 다음 할 일: 큐 계속 (`python src/run_queue.py --status`)
