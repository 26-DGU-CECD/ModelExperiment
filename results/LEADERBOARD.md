# LEADERBOARD

`python src/make_leaderboard.py`. test split. smoke_* excluded.

## A. generalist per-class F1

| experiment | model | alarm | fire_alarm | water | scream | glass_break | bicycle | gunshot | baby_cry | cry | car_horn | cat_meow | dog_bark | knock | background | macro-F1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E0_efficientat_generalist | efficientat | 0.7523 | 0.6561 | 0.9274 | 0.9639 | 0.9605 | 0.9283 | 0.9357 | 0.9505 | 0.9438 | 0.5952 | 0.9418 | 0.9814 | 0.9538 | 0.8907 | 0.8844 |
| E0m_efficientat_generalist_musan | efficientat | 0.7359 | 0.6640 | 0.9362 | 0.9419 | 0.9634 | 0.9148 | 0.9168 | 0.9458 | 0.9285 | 0.5393 | 0.9377 | 0.9877 | 0.8732 | 0.8933 | 0.8699 |
| E1_yamnet_generalist | yamnet_frozen | 0.7442 | 0.6303 | 0.8571 | 0.9028 | 0.9144 | 0.8910 | 0.8263 | 0.8544 | 0.8691 | 0.4634 | 0.7683 | 0.9241 | 0.8750 | 0.8132 | 0.8095 |
| E2_mnv4_generalist | mnv4 | 0.7530 | 0.6360 | 0.8657 | 0.9600 | 0.9655 | 0.9294 | 0.9188 | 0.9366 | 0.9176 | 0.6786 | 0.8953 | 0.9294 | 0.9524 | 0.8499 | 0.8706 |
| E2k_mnv4_kd | mnv4 | 0.7457 | 0.6417 | 0.8615 | 0.9639 | 0.9549 | 0.9318 | 0.9140 | 0.9078 | 0.9344 | 0.7273 | 0.8671 | 0.9249 | 0.9538 | 0.8367 | 0.8690 |

## B. specialist vs generalist (same model)

| experiment | model | class | spec F1 | gen F1 (same model) | delta | reject non-target | reject bg |
|---|---|---|---|---|---|---|---|

## C. condition summary (macro-F1 desc)

| experiment | condition | model | macro-F1 | accuracy | emergency recall | bg FA rate | bg FA strict | noisy SNR10 macro-F1 | tag | date |
|---|---|---|---|---|---|---|---|---|---|---|
| F_generalist_weighted_premusan | ensemble | efficientat+mnv4+yamnet | 0.8898 | 0.8748 | 0.8470 | 0.1454 | 0.0039 | 0.7818 | premusan | 2026-10-29 |
| F_generalist_soft_premusan | ensemble | efficientat+mnv4+yamnet | 0.8895 | 0.8744 | 0.8467 | 0.1454 | 0.0039 | 0.7805 | premusan | 2026-10-29 |
| F_generalist_stacking_premusan | ensemble | efficientat+mnv4+yamnet | 0.8862 | 0.8788 | 0.8448 | 0.1213 | 0.0013 | 0.7838 | premusan | 2026-10-29 |
| E0_efficientat_generalist | generalist | efficientat | 0.8844 | 0.8717 | 0.8545 | 0.1851 | 0.0105 | 0.7780 | - | 2026-10-29 |
| F_best_single_premusan | ensemble | efficientat+mnv4+yamnet | 0.8844 | 0.8717 | 0.8545 | 0.1851 | 0.0105 | 0.7780 | premusan | 2026-10-29 |
| F_generalist_hard_premusan | ensemble | efficientat+mnv4+yamnet | 0.8842 | 0.8726 | 0.8492 | 0.1567 | 0.0039 | 0.7771 | premusan | 2026-10-29 |
| E2_mnv4_generalist | generalist | mnv4 | 0.8706 | 0.8509 | 0.8273 | 0.1369 | 0.0105 | 0.6955 | - | 2026-10-29 |
| E0m_efficientat_generalist_musan | generalist | efficientat | 0.8699 | 0.8671 | 0.8385 | 0.1688 | 0.0132 | 0.8210 | - | 2026-10-29 |
| E2k_mnv4_kd | generalist | mnv4 | 0.8690 | 0.8452 | 0.8342 | 0.1858 | 0.0303 | 0.8070 | - | 2026-10-29 |
| E1_yamnet_generalist | generalist | yamnet_frozen | 0.8095 | 0.8128 | 0.7982 | 0.2113 | 0.0329 | 0.5327 | - | 2026-10-29 |

## D. operating points

| experiment | rule | mean threshold | emergency recall | emergency precision | bg FA | bg FA strict | FA/hour (proxy) |
|---|---|---|---|---|---|---|---|
| F_best_single_premusan | per-class tau on val: emergency recall>=0.95 / daily precision>=0.90 / others max F1 | 0.4385 | 0.8285 | 0.7779 | 0.2546 | 0.1842 | 458.3 |
| F_generalist_hard_premusan | per-class tau on val: emergency recall>=0.95 / daily precision>=0.90 / others max F1 | 0.4154 | 0.8529 | 0.8321 | 0.1298 | 0.0053 | 233.6 |
| F_generalist_soft_premusan | per-class tau on val: emergency recall>=0.95 / daily precision>=0.90 / others max F1 | 0.3954 | 0.8285 | 0.8163 | 0.1525 | 0.0329 | 274.5 |
| F_generalist_stacking_premusan | per-class tau on val: emergency recall>=0.95 / daily precision>=0.90 / others max F1 | 0.3646 | 0.8314 | 0.8395 | 0.1128 | 0.0053 | 203.0 |
| F_generalist_weighted_premusan | per-class tau on val: emergency recall>=0.95 / daily precision>=0.90 / others max F1 | 0.3954 | 0.8304 | 0.8169 | 0.1518 | 0.0329 | 273.2 |
