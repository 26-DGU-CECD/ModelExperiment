# third_party (git-ignored)

| 경로 | 저장소 | 커밋 | 날짜 | 용도 |
|---|---|---|---|---|
| `third_party/EfficientAT` | https://github.com/fschmid56/EfficientAT | `a425fdce92572e602a1d5634799bd9f1f2efa806` | 2024-11-20 | mn10_as 백본 (`models.mn.model.get_model`), `AugmentMelSTFT` |

| `third_party/torch_audioset` | https://github.com/w-hc/torch_audioset | `daed697ddcd1d2f7304cc3c2b1b4295ac7e304e4` | 2025-04-16 | YAMNet PyTorch 포트 (`torch_audioset.yamnet.model.YAMNet`), 변환 가중치 `yamnet.pth` (release v0.1, 14.4MB) |

재현: `git clone https://github.com/fschmid56/EfficientAT third_party/EfficientAT && git -C third_party/EfficientAT checkout a425fdce`

## EfficientAT mn10_as 메모
- 프리트레인 체크포인트: `https://github.com/fschmid56/EfficientAT/releases/download/v0.0.1/mn10_as.pt`.
  `get_model(pretrained_name="mn10_as")`가 `torch.hub.load_state_dict_from_url`로 받아 `models.mn.model.model_dir`(기본 `resources/`, cwd 상대)에 캐시.
  이 프로젝트는 `checkpoints/pretrained/`로 바꿔 저장 (`src/models/efficientat.py`).
- 입력: 32 kHz mono. `AugmentMelSTFT(n_mels=128, sr=32000, win_length=800, hopsize=320, n_fft=1024, freqm=48, timem=192)`.
  2초 → 64,000 샘플 → mel [128, 201]. 모델 입력 `[B, 1, 128, T]`. train 모드에서 freqm/timem SpecAugment 내장.
- `get_model(num_classes=N, pretrained_name="mn10_as", width_mult=1.0, head_type="mlp")`: N ≠ 527이면 `classifier.5` 드롭 후 로드.
- forward 반환 `(logits, features)` 튜플. logits는 `.squeeze()`돼 있어 batch 1에서 차원 주의.
- mn04_as 등 다른 폭: `NAME_TO_WIDTH("mn04")` = 0.4, pretrained `mn04_as`.

## YAMNet 메모
- **frozen** (`yamnet_frozen`, E1): TF-Hub `google/yamnet/1` 임베딩(1024, 2초 → 4프레임 평균)을 `src/cache_yamnet_emb.py`로
  `data/cache/yamnet_emb/<split>.npy`에 캐시 (CPU 약 100 clips/s, 전체 약 10분). torch MLP(1024→512→n) 헤드만 학습.
  파형 입력이 아니라 KD 학생으로는 못 씀.
- **ft** (`yamnet_ft`, E1k/S2): torch_audioset 포트 + release `yamnet.pth`(TF `yamnet.h5` 변환본) → `checkpoints/pretrained/yamnet.pth`.
  분류기를 `Linear(1024, n)`으로 교체, 전체 fine-tune. 프론트엔드는 YAMNet params 그대로
  (16 kHz, STFT 25 ms/10 ms, 64 mel 125–7500 Hz, magnitude mel, log offset 1e-3), 2초 클립 전체를 패치 1개 [B,1,201,64]로 입력
  (fully-conv + GAP라 길이 자유). TF-Hub와의 일치 검증 결과는 PROGRESS.md 참고.
