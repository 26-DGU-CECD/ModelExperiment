# E0 test: *→water 오분류 조사

`results/E0_efficientat_generalist/predictions_test.csv` 기준. 요청은 alarm→water 64개였으나 E0 confusion matrix에서 64건은 **background→water**. 둘 다 기록.

## alarm → water: 0 / 1098 (0.0%)

## background → water: 64 / 1410 (4.5%)

소스 21개에 분포 (해당 라벨 test 소스 210개 중). 상위 소스:

| source_file | 오분류 수 | 해당 소스 test 클립 수 | origin |
|---|---|---|---|
| S-211106_L_306_C_009_0001 | 9 | 14 | aihub |
| S-211113_L_306_C_008_0001 | 9 | 18 | aihub |
| S-211029_L_306_C_011_0001 | 6 | 16 | aihub |
| S-211031_L_306_C_004_0001 | 4 | 15 | aihub |
| S-211104_L_306_C_017_0001 | 3 | 13 | aihub |
| S-211124_L_307_L_001_0001 | 3 | 7 | aihub |
| S-211113_L_306_C_007_0001 | 3 | 14 | aihub |
| S-211106_S_102_C_022_0001 | 3 | 4 | aihub |
| S-211103_L_306_C_003_0001 | 3 | 3 | aihub |
| S-211106_L_307_C_004_0001 | 3 | 9 | aihub |
| S-211110_L_307_C_001_0001 | 3 | 10 | aihub |
| S-210822_L_306_L_007_0001 | 2 | 2 | aihub |
| S-211029_L_306_C_007_0001 | 2 | 17 | aihub |
| S-211113_L_307_C_011_0001 | 2 | 9 | aihub |
| S-211106_L_306_C_012_0001 | 2 | 2 | aihub |

상위 3개 소스가 24/64 (38%).

<details><summary>전체 파일 목록</summary>

```
background/clips_2s/part_00/경보__S-211106_S_102_C_022_0001_0_orig.wav  (src=S-211106_S_102_C_022_0001)
background/clips_2s/part_00/경보__S-211106_S_102_C_022_0001_15_orig.wav  (src=S-211106_S_102_C_022_0001)
background/clips_2s/part_00/경보__S-211106_S_102_C_022_0001_1_orig.wav  (src=S-211106_S_102_C_022_0001)
background/clips_2s/part_00/물소리__S-210821_L_306_L_041_0001_5_orig.wav  (src=S-210821_L_306_L_041_0001)
background/clips_2s/part_00/물소리__S-210822_L_306_L_007_0001_0_orig.wav  (src=S-210822_L_306_L_007_0001)
background/clips_2s/part_00/물소리__S-210822_L_306_L_007_0001_1_orig.wav  (src=S-210822_L_306_L_007_0001)
background/clips_2s/part_00/물소리__S-211029_L_306_C_007_0001_16_orig.wav  (src=S-211029_L_306_C_007_0001)
background/clips_2s/part_00/물소리__S-211029_L_306_C_007_0001_6_orig.wav  (src=S-211029_L_306_C_007_0001)
background/clips_2s/part_00/물소리__S-211029_L_306_C_011_0001_11_orig.wav  (src=S-211029_L_306_C_011_0001)
background/clips_2s/part_00/물소리__S-211029_L_306_C_011_0001_12_orig.wav  (src=S-211029_L_306_C_011_0001)
background/clips_2s/part_00/물소리__S-211029_L_306_C_011_0001_13_orig.wav  (src=S-211029_L_306_C_011_0001)
background/clips_2s/part_00/물소리__S-211029_L_306_C_011_0001_15_orig.wav  (src=S-211029_L_306_C_011_0001)
background/clips_2s/part_00/물소리__S-211029_L_306_C_011_0001_16_orig.wav  (src=S-211029_L_306_C_011_0001)
background/clips_2s/part_00/물소리__S-211029_L_306_C_011_0001_17_orig.wav  (src=S-211029_L_306_C_011_0001)
background/clips_2s/part_00/물소리__S-211030_L_306_C_017_0001_29_orig.wav  (src=S-211030_L_306_C_017_0001)
background/clips_2s/part_00/물소리__S-211030_L_306_C_020_0001_18_orig.wav  (src=S-211030_L_306_C_020_0001)
background/clips_2s/part_00/물소리__S-211031_L_306_C_004_0001_15_orig.wav  (src=S-211031_L_306_C_004_0001)
background/clips_2s/part_00/물소리__S-211031_L_306_C_004_0001_22_orig.wav  (src=S-211031_L_306_C_004_0001)
background/clips_2s/part_00/물소리__S-211031_L_306_C_004_0001_24_orig.wav  (src=S-211031_L_306_C_004_0001)
background/clips_2s/part_00/물소리__S-211031_L_306_C_004_0001_25_orig.wav  (src=S-211031_L_306_C_004_0001)
background/clips_2s/part_00/물소리__S-211103_L_306_C_002_0001_0_orig.wav  (src=S-211103_L_306_C_002_0001)
background/clips_2s/part_00/물소리__S-211103_L_306_C_002_0001_1_orig.wav  (src=S-211103_L_306_C_002_0001)
background/clips_2s/part_00/물소리__S-211103_L_306_C_003_0001_0_orig.wav  (src=S-211103_L_306_C_003_0001)
background/clips_2s/part_00/물소리__S-211103_L_306_C_003_0001_1_orig.wav  (src=S-211103_L_306_C_003_0001)
background/clips_2s/part_00/물소리__S-211103_L_306_C_003_0001_2_orig.wav  (src=S-211103_L_306_C_003_0001)
background/clips_2s/part_00/물소리__S-211104_L_306_C_017_0001_10_orig.wav  (src=S-211104_L_306_C_017_0001)
background/clips_2s/part_00/물소리__S-211104_L_306_C_017_0001_11_orig.wav  (src=S-211104_L_306_C_017_0001)
background/clips_2s/part_00/물소리__S-211104_L_306_C_017_0001_1_orig.wav  (src=S-211104_L_306_C_017_0001)
background/clips_2s/part_00/물소리__S-211106_L_306_C_009_0001_0_orig.wav  (src=S-211106_L_306_C_009_0001)
background/clips_2s/part_00/물소리__S-211106_L_306_C_009_0001_18_orig.wav  (src=S-211106_L_306_C_009_0001)
background/clips_2s/part_00/물소리__S-211106_L_306_C_009_0001_19_orig.wav  (src=S-211106_L_306_C_009_0001)
background/clips_2s/part_00/물소리__S-211106_L_306_C_009_0001_23_orig.wav  (src=S-211106_L_306_C_009_0001)
background/clips_2s/part_00/물소리__S-211106_L_306_C_009_0001_24_orig.wav  (src=S-211106_L_306_C_009_0001)
background/clips_2s/part_00/물소리__S-211106_L_306_C_009_0001_25_orig.wav  (src=S-211106_L_306_C_009_0001)
background/clips_2s/part_00/물소리__S-211106_L_306_C_009_0001_26_orig.wav  (src=S-211106_L_306_C_009_0001)
background/clips_2s/part_00/물소리__S-211106_L_306_C_009_0001_27_orig.wav  (src=S-211106_L_306_C_009_0001)
background/clips_2s/part_00/물소리__S-211106_L_306_C_009_0001_4_orig.wav  (src=S-211106_L_306_C_009_0001)
background/clips_2s/part_00/물소리__S-211106_L_306_C_012_0001_2_orig.wav  (src=S-211106_L_306_C_012_0001)
background/clips_2s/part_00/물소리__S-211106_L_306_C_012_0001_3_orig.wav  (src=S-211106_L_306_C_012_0001)
background/clips_2s/part_00/물소리__S-211106_L_307_C_004_0001_11_orig.wav  (src=S-211106_L_307_C_004_0001)
background/clips_2s/part_00/물소리__S-211106_L_307_C_004_0001_22_orig.wav  (src=S-211106_L_307_C_004_0001)
background/clips_2s/part_00/물소리__S-211106_L_307_C_004_0001_2_orig.wav  (src=S-211106_L_307_C_004_0001)
background/clips_2s/part_00/물소리__S-211110_L_307_C_001_0001_10_orig.wav  (src=S-211110_L_307_C_001_0001)
background/clips_2s/part_00/물소리__S-211110_L_307_C_001_0001_16_orig.wav  (src=S-211110_L_307_C_001_0001)
background/clips_2s/part_00/물소리__S-211110_L_307_C_001_0001_2_orig.wav  (src=S-211110_L_307_C_001_0001)
background/clips_2s/part_00/물소리__S-211113_L_306_C_007_0001_5_orig.wav  (src=S-211113_L_306_C_007_0001)
background/clips_2s/part_00/물소리__S-211113_L_306_C_007_0001_6_orig.wav  (src=S-211113_L_306_C_007_0001)
background/clips_2s/part_00/물소리__S-211113_L_306_C_007_0001_7_orig.wav  (src=S-211113_L_306_C_007_0001)
background/clips_2s/part_00/물소리__S-211113_L_306_C_008_0001_11_orig.wav  (src=S-211113_L_306_C_008_0001)
background/clips_2s/part_00/물소리__S-211113_L_306_C_008_0001_12_orig.wav  (src=S-211113_L_306_C_008_0001)
background/clips_2s/part_00/물소리__S-211113_L_306_C_008_0001_14_orig.wav  (src=S-211113_L_306_C_008_0001)
background/clips_2s/part_00/물소리__S-211113_L_306_C_008_0001_15_orig.wav  (src=S-211113_L_306_C_008_0001)
background/clips_2s/part_00/물소리__S-211113_L_306_C_008_0001_16_orig.wav  (src=S-211113_L_306_C_008_0001)
background/clips_2s/part_00/물소리__S-211113_L_306_C_008_0001_18_orig.wav  (src=S-211113_L_306_C_008_0001)
background/clips_2s/part_00/물소리__S-211113_L_306_C_008_0001_19_orig.wav  (src=S-211113_L_306_C_008_0001)
background/clips_2s/part_00/물소리__S-211113_L_306_C_008_0001_21_orig.wav  (src=S-211113_L_306_C_008_0001)
background/clips_2s/part_00/물소리__S-211113_L_306_C_008_0001_2_orig.wav  (src=S-211113_L_306_C_008_0001)
background/clips_2s/part_00/물소리__S-211113_L_307_C_011_0001_0_orig.wav  (src=S-211113_L_307_C_011_0001)
background/clips_2s/part_00/물소리__S-211113_L_307_C_011_0001_1_orig.wav  (src=S-211113_L_307_C_011_0001)
background/clips_2s/part_00/물소리__S-211124_L_307_L_001_0001_17_orig.wav  (src=S-211124_L_307_L_001_0001)
background/clips_2s/part_00/물소리__S-211124_L_307_L_001_0001_18_orig.wav  (src=S-211124_L_307_L_001_0001)
background/clips_2s/part_00/물소리__S-211124_L_307_L_001_0001_4_orig.wav  (src=S-211124_L_307_L_001_0001)
background/clips_2s/part_00/물소리__S-211124_L_307_L_011_0001_17_orig.wav  (src=S-211124_L_307_L_011_0001)
background/clips_2s/part_00/물소리__S-211124_L_307_L_015_0001_1_orig.wav  (src=S-211124_L_307_L_015_0001)
```
</details>

background 클립의 원래 라벨(파일명 접두어) 분포: {'물소리': 61, '경보': 3}

(test background 전체 접두어 분포: {'물소리': 429, '유리깨지는소리': 217, '총': 178, '울음': 175, '경보': 133, '비명': 98, '자전거': 72, '화재경보': 35, 'knock': 8})
