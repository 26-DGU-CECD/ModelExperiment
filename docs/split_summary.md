# Split summary (after `src/relabel.py --mode relabel_s103`)

split/fold unchanged from manifest_v1.csv; only `label_fine` changed. Tables use `label_fine`.

## 클립 수 (split × label_fine)

| label_fine  | train | val  | test | total |
|-------------|-------|------|------|-------|
| alarm       | 5889  | 569  | 686  | 7144  |
| fire_alarm  | 7539  | 752  | 837  | 9128  |
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

## source_file 수 (split × label_fine)

| label_fine  | train | val | test | total |
|-------------|-------|-----|------|-------|
| alarm       | 135   | 47  | 47   | 229   |
| fire_alarm  | 104   | 33  | 32   | 169   |
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
