# 데이터셋 노트: retrina0678/miimo-audio-dataset

출처: HF dataset `retrina0678/miimo-audio-dataset` (README 2026-10-29 기준). 로컬: `data/miimo/`.

## 규모 (HF 실제 파일 목록, 2026-10-29 조사)

| 폴더 | 파일 수 | GB |
|---|---:|---:|
| alarm | 16,213 | 2.43 |
| glass_break | 12,561 | 1.94 |
| background | 14,142 | 1.81 |
| baby_cry | 9,540 | 1.41 |
| water | 6,952 | 1.18 |
| fire_alarm | 6,319 | 0.95 |
| gunshot | 4,554 | 0.71 |
| bicycle | 3,828 | 0.59 |
| musan_mixed_2s | 3,583 | 0.46 |
| scream | 2,551 | 0.40 |
| cat_meow | 2,940 | 0.40 |
| dog_bark | 1,423 | 0.19 |
| knock | 953 | 0.14 |
| car_horn | 851 | 0.14 |
| (root csv/md/py) | 21 | 0.10 |
| esc50 (json sidecar) | 190 | 0.00 |
| data_augmented/src | 2 | 0.00 |
| **합계** | **86,623** | **12.84** |

- 클립 포맷: WAV float32 [-1,1], 16 kHz mono, 2.0초 = 32,000 샘플.
- 분할: 2초 슬라이딩 윈도우 hop 1초 (50% 오버랩). 2초 미만 잔여 버림.
- 무음 판정: 100ms×20 세그먼트 peak RMS < -30 dBFS → `background`.
- **musan_mixed_2s 주의**: README는 240,147개(약 29GB)라 하지만 HF에는 `musan_mixed_2s/fire_alarm` 3,583개만
  올라와 있음(업로드 미완). 필요하면 `generate_musan_mixes.py`(seed 42)로 로컬 생성. MUSAN 원본은 repo에 없음.

## 라벨 13개

`alarm, fire_alarm, water, scream, glass_break, bicycle, gunshot, baby_cry, car_horn, cat_meow, dog_bark, knock, background`

README 라벨별 수량 (verify_dataset.py 기준값):

| 라벨 | raw | clips_2s | 독립 소스 |
|---|---:|---:|---:|
| alarm | 403 | 15,810 | 395 |
| fire_alarm | 169 | 6,150 | 167 |
| water | 238 | 6,714 | 195 |
| scream | 94 | 2,457 | 90 |
| glass_break | 258 | 12,303 | 255 |
| bicycle | 81 | 3,747 | 78 |
| gunshot | 297 | 4,257 | 254 |
| baby_cry | 336 | 9,204 | 325 |
| car_horn | 80 | 771 | 57 |
| cat_meow | 168 | 2,772 | 127 |
| dog_bark | 118 | 1,305 | 106 |
| knock | 536 | 417 | 85 |
| background | — | 14,142 | 1,058 |
| 합계 | 2,778 | 80,049 | |

- `baby_cry` = AI Hub `울음`(146 raw / 6,396 clips) + ESC-50/donateacry `baby_cry`(190 raw / 2,808 clips). 구분은 `source_file`.
- `knock`은 raw 536 > clips 417: 원본 대부분 2초 미만.
- gunshot/glass_break/car_horn은 원본 누락 상태(CSV 4,756 vs 디스크 2,778).

## 폴더 구조

```
<label>/raw/          원본 (background는 raw 없음)
<label>/clips_2s/     2초 클립 (orig + aug)
```

**part_XX 분할**: HF 디렉터리당 10,000 파일 제한 때문에 `alarm`, `glass_break`, `background`는
`clips_2s/part_00/`, `part_01/`로 나뉨. 나머지는 평면. 분할 기준 = 파일명 정렬 후 균등 분배.
**경로를 직접 조합하지 말고 `clip_metadata.csv`의 `filepath`를 쓸 것** (part 경로 반영됨).
평면으로 되돌리기: `df.filepath.str.replace(r"/part_\d+/", "/", regex=True)`.

## 파일명 규칙

```
{원본파일명}_{시작초}_{orig|augN-태그[-태그]}.wav
예) ESC50_1-187207-A-20_0_aug1-shf-gan.wav
```
background 클립은 원래 라벨 접두어(한글 그대로): `{원본라벨}__{원본파일명}_{시작초}_{variant}.wav`.
영어 원래 라벨은 파일명이 아닌 `origin_label` 컬럼 사용.

## clip_metadata.csv 컬럼

| 컬럼 | 설명 |
|---|---|
| `filepath` | repo 루트 기준 상대 경로 |
| `label` | 학습 라벨 (폴더명, NFC) |
| `source_file` | 원본 음원 파일명 (확장자 제외). **GroupKFold 그룹 키** |
| `start_sec` | 잘라낸 시작 위치(초) |
| `variant` | `orig` / `aug1` / `aug2` |
| `aug_tags` | 증강 조합 `+` 구분 (예 `shf+gan`) |
| `is_augmented` | 0=원본, 1=증강 |
| `origin_label` | background만: 무음 판정 전 원래 라벨 |

## 증강 태그 (SEED=42, 변환 1~2개 무작위 조합)

원본:증강 = 이벤트 라벨 1:2, background 1:1.

| 태그 | 변환 | 파라미터 |
|---|---|---|
| `shf` | Time Shift | ±0.5초 rollover |
| `gan` | Gain | -6~+6 dB (background -6~+3) |
| `agn` | Gaussian Noise | amp 0.001~0.015 |
| `drc` | DRC 압축/확장 | thr -30~-15 dB, ratio 1.5~3.0 / 1.2~1.6 |
| `ngt` | Noise Gate | thr -45~-35 dB, 감쇠 12~24 dB |

background는 `shf`, `gan`만.

## 분할 주의 (프로젝트 규칙과 동일)

- 같은 `source_file` 클립은 50% 오버랩 + 증강으로 구간 공유. **반드시 `source_file` 단위 GroupKFold**. 클립 단위 분할 금지.
- val/test는 `is_augmented == 0`(orig)만.
- MUSAN 혼합본도 `group_id = aug_<source_file>` 동일, 같은 그룹으로 묶어야 함.

## 라이선스 (혼합, 단일 라이선스 아님)

| 라벨 | 출처 | 라이선스 |
|---|---|---|
| alarm, fire_alarm, water, scream, glass_break, bicycle, gunshot, baby_cry(울음) | AI Hub | **재배포 제한**. 파일명 `S-2110xx_*`, `S-2111xx_*`. 안전하게 쓰려면 AI Hub에서 직접 받고 약관 동의 |
| baby_cry(일부) | ESC-50 | **CC BY-NC 3.0**. 비상업 한정, 출처 표기. `baby_cry/**/ESC50_*` |
| baby_cry(일부) | donateacry-corpus | 원 저장소 확인 |
| knock | Knocking Sound Effects With Emotional Intentions | 원 배포처 확인 |
| cat_meow, dog_bark, car_horn | 수집처 혼재 | 확인 필요 |
| background | 위 전체 무음분 | 원 출처 따름 |
| musan_mixed_2s | 원 클립 + MUSAN noise | 원 클립 라이선스 + MUSAN CC BY 4.0 |

- ESC-50이 CC BY-NC라 **데이터셋 통째로 쓴 결과물은 상업 이용 불가**. 상업 용도면 `ESC50_*` 제외.
- 이 repo 데이터는 외부 재배포하지 않는다 (`data/`는 .gitignore).
- 인용: Piczak 2015 (ESC-50), Snyder et al. 2015 (MUSAN).
