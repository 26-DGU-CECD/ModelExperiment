# third_party (git-ignored)

| 경로 | 저장소 | 커밋 | 날짜 | 용도 |
|---|---|---|---|---|
| `third_party/EfficientAT` | https://github.com/fschmid56/EfficientAT | `a425fdce92572e602a1d5634799bd9f1f2efa806` | 2024-11-20 | mn10_as 백본 (`models.mn.model.get_model`), `AugmentMelSTFT` |

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
