# val -> test gap (v2 generalists)

F1 per class on val vs test; support in parentheses. Large negative gaps on small-support classes (car_horn: val 59 / test 26 clips) are mostly sampling noise; gaps on large classes point at val-selection bias (early stopping picks the epoch that fits val) or a val/test source mismatch.

## E0m_v2: val macro-F1 0.9181 -> test 0.9170 (gap -0.0011); w/o car_horn: 0.9201 -> 0.9382

| class | val F1 (n) | test F1 (n) | gap | test recall | test precision |
|---|---|---|---|---|---|
| car_horn | 0.892 (59) | 0.641 (26) | -0.251 | 0.962 | 0.481 |
| baby_cry | 0.985 (193) | 0.941 (196) | -0.044 | 0.980 | 0.906 |
| gunshot | 0.944 (282) | 0.917 (295) | -0.027 | 0.956 | 0.881 |
| bicycle | 0.941 (290) | 0.918 (247) | -0.023 | 1.000 | 0.849 |
| background | 0.892 (1518) | 0.890 (1410) | -0.002 | 0.824 | 0.968 |
| cry | 0.932 (441) | 0.933 (411) | +0.001 | 0.966 | 0.902 |
| scream | 0.939 (133) | 0.945 (147) | +0.006 | 0.993 | 0.901 |
| glass_break | 0.953 (766) | 0.962 (794) | +0.008 | 0.977 | 0.946 |
| cat_meow | 0.916 (222) | 0.929 (185) | +0.014 | 0.924 | 0.934 |
| fire_alarm | 0.961 (752) | 0.989 (837) | +0.028 | 0.983 | 0.995 |
| alarm | 0.942 (569) | 0.970 (686) | +0.028 | 0.950 | 0.991 |
| water | 0.886 (422) | 0.929 (531) | +0.043 | 0.981 | 0.882 |
| knock | 0.831 (27) | 0.886 (31) | +0.055 | 1.000 | 0.795 |
| dog_bark | 0.840 (88) | 0.988 (81) | +0.148 | 0.988 | 0.988 |

largest drops: car_horn (-0.251), baby_cry (-0.044), gunshot (-0.027)

- car_horn test confusions (true -> pred): cat_meow 1
- baby_cry test confusions (true -> pred): cry 4

## E1k_v2: val macro-F1 0.9236 -> test 0.8833 (gap -0.0403); w/o car_horn: 0.9297 -> 0.9205

| class | val F1 (n) | test F1 (n) | gap | test recall | test precision |
|---|---|---|---|---|---|
| car_horn | 0.844 (59) | 0.400 (26) | -0.444 | 0.692 | 0.281 |
| baby_cry | 0.982 (193) | 0.899 (196) | -0.083 | 0.980 | 0.831 |
| cat_meow | 0.909 (222) | 0.833 (185) | -0.076 | 0.757 | 0.927 |
| bicycle | 0.951 (290) | 0.914 (247) | -0.037 | 0.992 | 0.848 |
| gunshot | 0.950 (282) | 0.926 (295) | -0.024 | 0.953 | 0.901 |
| alarm | 0.966 (569) | 0.946 (686) | -0.020 | 0.908 | 0.987 |
| knock | 0.931 (27) | 0.918 (31) | -0.013 | 0.903 | 0.933 |
| background | 0.896 (1518) | 0.888 (1410) | -0.008 | 0.872 | 0.905 |
| cry | 0.926 (441) | 0.927 (411) | +0.002 | 0.944 | 0.911 |
| glass_break | 0.951 (766) | 0.958 (794) | +0.007 | 0.965 | 0.952 |
| fire_alarm | 0.981 (752) | 0.996 (837) | +0.016 | 0.993 | 1.000 |
| water | 0.884 (422) | 0.910 (531) | +0.026 | 0.895 | 0.926 |
| dog_bark | 0.854 (88) | 0.893 (81) | +0.040 | 0.877 | 0.910 |
| scream | 0.906 (133) | 0.957 (147) | +0.052 | 0.993 | 0.924 |

largest drops: car_horn (-0.444), baby_cry (-0.083), cat_meow (-0.076)

- car_horn test confusions (true -> pred): background 6, alarm 2
- baby_cry test confusions (true -> pred): cry 4

## E2k_v2: val macro-F1 0.9138 -> test 0.9100 (gap -0.0038); w/o car_horn: 0.9126 -> 0.9231

| class | val F1 (n) | test F1 (n) | gap | test recall | test precision |
|---|---|---|---|---|---|
| car_horn | 0.929 (59) | 0.739 (26) | -0.189 | 0.654 | 0.850 |
| baby_cry | 0.977 (193) | 0.904 (196) | -0.074 | 0.980 | 0.838 |
| bicycle | 0.954 (290) | 0.912 (247) | -0.042 | 0.964 | 0.865 |
| cat_meow | 0.922 (222) | 0.881 (185) | -0.041 | 0.843 | 0.923 |
| gunshot | 0.922 (282) | 0.904 (295) | -0.018 | 0.956 | 0.857 |
| background | 0.845 (1518) | 0.833 (1410) | -0.012 | 0.824 | 0.842 |
| fire_alarm | 0.987 (752) | 0.989 (837) | +0.001 | 0.978 | 0.999 |
| glass_break | 0.942 (766) | 0.949 (794) | +0.006 | 0.940 | 0.958 |
| cry | 0.928 (441) | 0.937 (411) | +0.009 | 0.961 | 0.914 |
| scream | 0.921 (133) | 0.939 (147) | +0.018 | 0.993 | 0.890 |
| water | 0.822 (422) | 0.846 (531) | +0.024 | 0.831 | 0.863 |
| alarm | 0.932 (569) | 0.963 (686) | +0.032 | 0.942 | 0.986 |
| knock | 0.857 (27) | 0.969 (31) | +0.112 | 1.000 | 0.939 |
| dog_bark | 0.854 (88) | 0.975 (81) | +0.122 | 0.975 | 0.975 |

largest drops: car_horn (-0.189), baby_cry (-0.074), bicycle (-0.042)

- car_horn test confusions (true -> pred): background 4, alarm 3, fire_alarm 1
- baby_cry test confusions (true -> pred): cry 2, background 2

