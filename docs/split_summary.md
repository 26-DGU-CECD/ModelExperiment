# Split summary

`python src/make_splits.py`. group = `source_file`, StratifiedGroupKFold(5, shuffle, seed 42), stratify = event label + source_origin. fold 0 = test, 1 = val, 2-4 = train. val/test = orig clips only. Tables use `label_fine` (baby_cry/aihub -> cry).

## 클립 수 (split × label_fine)

| label_fine  | train | val  | test | total |
|-------------|-------|------|------|-------|
| alarm       | 9666  | 950  | 1098 | 11714 |
| fire_alarm  | 3762  | 371  | 425  | 4558  |
| water       | 3855  | 422  | 531  | 4808  |
| scream      | 1617  | 133  | 147  | 1897  |
| glass_break | 7623  | 766  | 794  | 9183  |
| bicycle     | 2136  | 290  | 247  | 2673  |
| gunshot     | 2526  | 282  | 295  | 3103  |
| baby_cry    | 1641  | 193  | 196  | 2030  |
| cry         | 3840  | 441  | 411  | 4692  |
| car_horn    | 516   | 59   | 26   | 601   |
| cat_meow    | 1551  | 222  | 185  | 1958  |
| dog_bark    | 798   | 88   | 81   | 967   |
| knock       | 243   | 27   | 31   | 301   |
| background  | 8286  | 1518 | 1410 | 11214 |
| TOTAL       | 48060 | 5762 | 5877 | 59699 |

## source_file 수 (split × label_fine)

| label_fine  | train | val | test | total |
|-------------|-------|-----|------|-------|
| alarm       | 238   | 79  | 78   | 395   |
| fire_alarm  | 103   | 32  | 32   | 167   |
| water       | 118   | 39  | 38   | 195   |
| scream      | 54    | 18  | 18   | 90    |
| glass_break | 152   | 52  | 51   | 255   |
| bicycle     | 47    | 16  | 15   | 78    |
| gunshot     | 156   | 48  | 50   | 254   |
| baby_cry    | 108   | 37  | 39   | 184   |
| cry         | 87    | 29  | 25   | 141   |
| car_horn    | 34    | 11  | 12   | 57    |
| cat_meow    | 74    | 27  | 26   | 127   |
| dog_bark    | 64    | 21  | 21   | 106   |
| knock       | 52    | 16  | 17   | 85    |
| background  | 644   | 204 | 210  | 1058  |
| TOTAL       | 1243  | 415 | 415  | 2073  |

## source_file 수 (label_fine × source_origin)

| label_fine  | aihub | donateacry | esc50 | other |
|-------------|-------|------------|-------|-------|
| alarm       | 395   | 0          | 0     | 0     |
| fire_alarm  | 167   | 0          | 0     | 0     |
| water       | 195   | 0          | 0     | 0     |
| scream      | 90    | 0          | 0     | 0     |
| glass_break | 255   | 0          | 0     | 0     |
| bicycle     | 78    | 0          | 0     | 0     |
| gunshot     | 254   | 0          | 0     | 0     |
| baby_cry    | 0     | 182        | 2     | 0     |
| cry         | 141   | 0          | 0     | 0     |
| car_horn    | 0     | 0          | 34    | 23    |
| cat_meow    | 0     | 0          | 3     | 124   |
| dog_bark    | 0     | 0          | 5     | 101   |
| knock       | 0     | 0          | 36    | 49    |
| background  | 912   | 40         | 46    | 60    |
