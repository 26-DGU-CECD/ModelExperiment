# 라벨 감사 (AI Hub 소스, 시나리오 코드별) — 모델 E0_efficientat_generalist, 라벨 manifest_v1.csv

시나리오 코드 = 파일명 `S-YYMMDD_<코드>_...`. recall = 해당 (라벨, 코드) test 클립 중 정답 예측 비율. F1* = 라벨 전체 FP를 모든 코드에 공통 적용. F1* < 0.6 → 플래그.

| label | scenario | sources (all) | test sources | test clips | recall | F1* | top wrong preds |
|---|---|---|---|---|---|---|---|
| alarm | S_101 | 83 | 22 | 347 | 0.928 | 0.919 | car_horn 20, bicycle 2 |
| alarm | S_102 | 67 | 25 | 339 | 0.988 | 0.949 | glass_break 2, background 2 |
| alarm | S_103 | 140 | 31 | 412 | 0.061 | 0.107 | fire_alarm 380, glass_break 5 |
| background | H_302 | 111 | 18 | 175 | 0.789 | 0.831 | cry 37 |
| background | H_303 | 81 | 18 | 98 | 0.980 | 0.901 | car_horn 1, scream 1 |
| background | L_306 | 122 | 24 | 306 | 0.840 | 0.883 | water 48, glass_break 1 |
| background | L_307 | 67 | 12 | 123 | 0.894 | 0.873 | water 13 |
| background | O_201 | 169 | 36 | 217 | 0.816 | 0.857 | glass_break 39, gunshot 1 |
| background | S_101 | 18 | 4 | 48 | 0.938 | 0.804 | alarm 2, scream 1 |
| background | S_102 | 67 | 16 | 50 | 0.700 | 0.673 | car_horn 6, alarm 5 |
| background | S_103 | 28 | 3 | 70 | 1.000 | 0.881 | - |
| background | S_202 | 61 | 12 | 72 | 0.514 | 0.578 | bicycle 35 |
| background | W_101 | 148 | 31 | 142 | 0.880 | 0.874 | gunshot 17 |
| background | W_102 | 40 | 12 | 36 | 0.528 | 0.514 | gunshot 17 |
| bicycle | S_202 | 20 | 15 | 247 | 0.996 | 0.928 | glass_break 1 |
| cry | H_302 | 35 | 25 | 411 | 0.981 | 0.947 | water 3, background 2 |
| fire_alarm | S_103 | 3 | 32 | 425 | 0.925 | 0.656 | alarm 25, glass_break 5 |
| glass_break | O_201 | 88 | 51 | 794 | 0.995 | 0.960 | background 3, gunshot 1 |
| gunshot | W_101 | 65 | 38 | 244 | 0.984 | 0.923 | glass_break 2, background 1 |
| gunshot | W_102 | 24 | 12 | 51 | 1.000 | 0.739 | - |
| scream | H_303 | 10 | 18 | 147 | 1.000 | 0.970 | - |
| water | L_306 | 6 | 17 | 258 | 0.969 | 0.870 | background 6, glass_break 1 |
| water | L_307 | 43 | 21 | 273 | 0.978 | 0.880 | background 3, glass_break 3 |

## 플래그 (F1* < 0.6)

- **alarm / S_103**: F1* 0.107 (test clips 412)
- **background / S_202**: F1* 0.578 (test clips 72)
- **background / W_102**: F1* 0.514 (test clips 36)
