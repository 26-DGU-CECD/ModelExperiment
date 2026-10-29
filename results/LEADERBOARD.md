# LEADERBOARD

`python src/make_leaderboard.py`. test split. smoke_* excluded.

## A. generalist per-class F1

| experiment | model | labels | alarm | fire_alarm | water | scream | glass_break | bicycle | gunshot | baby_cry | cry | car_horn | cat_meow | dog_bark | knock | background | macro-F1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E0_efficientat_generalist | efficientat | v1 | 0.7523 | 0.6561 | 0.9274 | 0.9639 | 0.9605 | 0.9283 | 0.9357 | 0.9505 | 0.9438 | 0.5952 | 0.9418 | 0.9814 | 0.9538 | 0.8907 | 0.8844 |
| E0m_efficientat_generalist_musan | efficientat | v1 | 0.7359 | 0.6640 | 0.9362 | 0.9419 | 0.9634 | 0.9148 | 0.9168 | 0.9458 | 0.9285 | 0.5393 | 0.9377 | 0.9877 | 0.8732 | 0.8933 | 0.8699 |
| E0m_v2 | efficientat | v2 | 0.9702 | 0.9892 | 0.9287 | 0.9450 | 0.9616 | 0.9182 | 0.9171 | 0.9412 | 0.9330 | 0.6410 | 0.9293 | 0.9877 | 0.8857 | 0.8901 | 0.9170 |
| E1_v2 | yamnet_frozen | v2 | 0.9495 | 0.9629 | 0.8539 | 0.8754 | 0.9151 | 0.9087 | 0.8135 | 0.8558 | 0.8798 | 0.5063 | 0.8235 | 0.9250 | 0.9206 | 0.8187 | 0.8578 |
| E1_yamnet_generalist | yamnet_frozen | v1 | 0.7442 | 0.6303 | 0.8571 | 0.9028 | 0.9144 | 0.8910 | 0.8263 | 0.8544 | 0.8691 | 0.4634 | 0.7683 | 0.9241 | 0.8750 | 0.8132 | 0.8095 |
| E1k_v2 | yamnet_ft | v2 | 0.9461 | 0.9964 | 0.9100 | 0.9574 | 0.9581 | 0.9142 | 0.9259 | 0.8993 | 0.9271 | 0.4000 | 0.8333 | 0.8931 | 0.9180 | 0.8880 | 0.8833 |
| E1k_yamnet_kd | yamnet_ft | v1 | 0.7435 | 0.6485 | 0.9202 | 0.9536 | 0.9572 | 0.9280 | 0.9386 | 0.9187 | 0.9212 | 0.4651 | 0.8547 | 0.8521 | 0.9375 | 0.8850 | 0.8517 |
| E2_mnv4_generalist | mnv4 | v1 | 0.7530 | 0.6360 | 0.8657 | 0.9600 | 0.9655 | 0.9294 | 0.9188 | 0.9366 | 0.9176 | 0.6786 | 0.8953 | 0.9294 | 0.9524 | 0.8499 | 0.8706 |
| E2k_mnv4_kd | mnv4 | v1 | 0.7457 | 0.6417 | 0.8615 | 0.9639 | 0.9549 | 0.9318 | 0.9140 | 0.9078 | 0.9344 | 0.7273 | 0.8671 | 0.9249 | 0.9538 | 0.8367 | 0.8690 |
| E2k_v2 | mnv4 | v2 | 0.9635 | 0.9885 | 0.8464 | 0.9389 | 0.9485 | 0.9119 | 0.9038 | 0.9035 | 0.9371 | 0.7391 | 0.8814 | 0.9753 | 0.9688 | 0.8330 | 0.9100 |

## B. specialist vs generalist (same model)

| experiment | model | labels | recipe | class | spec F1 | gen F1 (same model) | delta | reject non-target | reject bg |
|---|---|---|---|---|---|---|---|---|---|
| S1_efficientat_caution | efficientat | v2 | naive | bicycle | 0.8917 | 0.9182 | -0.0265 | 0.9816 | 0.8128 |
| S1_efficientat_caution | efficientat | v2 | naive | baby_cry | 0.8787 | 0.9412 | -0.0625 | 0.9816 | 0.8128 |
| S1_efficientat_caution | efficientat | v2 | naive | gunshot | 0.8806 | 0.9171 | -0.0365 | 0.9816 | 0.8128 |
| S1_efficientat_caution | efficientat | v2 | naive | glass_break | 0.9075 | 0.9616 | -0.0541 | 0.9816 | 0.8128 |
| S2_yamnet_emergency | yamnet_ft | v2 | naive | alarm | 0.9452 | 0.7435 | 0.2016 | 0.9945 | 0.9553 |
| S2_yamnet_emergency | yamnet_ft | v2 | naive | fire_alarm | 0.9879 | 0.6485 | 0.3394 | 0.9945 | 0.9553 |
| S2_yamnet_emergency | yamnet_ft | v2 | naive | scream | 0.9435 | 0.9536 | -0.0101 | 0.9945 | 0.9553 |
| S2_yamnet_emergency | yamnet_ft | v2 | naive | cry | 0.9124 | 0.9212 | -0.0088 | 0.9945 | 0.9553 |
| S2_yamnet_emergency | yamnet_ft | v2 | naive | car_horn | 0.4691 | 0.4651 | 0.0040 | 0.9945 | 0.9553 |
| SB_yamnet_best | yamnet_ft | v2 | naive | alarm | 0.9492 | 0.7435 | 0.2056 | 0.9819 | 0.9738 |
| SB_yamnet_best | yamnet_ft | v2 | naive | gunshot | 0.8735 | 0.9386 | -0.0652 | 0.9819 | 0.9738 |
| SB_yamnet_best | yamnet_ft | v2 | naive | dog_bark | 0.8974 | 0.8521 | 0.0454 | 0.9819 | 0.9738 |
| SB_yamnet_best | yamnet_ft | v2 | naive | knock | 0.8308 | 0.9375 | -0.1067 | 0.9819 | 0.9738 |
| S1_efficientat_caution | efficientat | v2 | ft-v2 | bicycle | 0.9234 | 0.9182 | 0.0051 | 0.9969 | 0.9135 |
| S1_efficientat_caution | efficientat | v2 | ft-v2 | baby_cry | 0.9458 | 0.9412 | 0.0046 | 0.9969 | 0.9135 |
| S1_efficientat_caution | efficientat | v2 | ft-v2 | gunshot | 0.9159 | 0.9171 | -0.0012 | 0.9969 | 0.9135 |
| S1_efficientat_caution | efficientat | v2 | ft-v2 | glass_break | 0.9646 | 0.9616 | 0.0030 | 0.9969 | 0.9135 |

## C. condition summary (macro-F1 desc)

| experiment | condition | model | macro-F1 | macro-F1 w/o car_horn | accuracy | emergency recall | emergency group recall | bg FA rate | bg FA strict | noisy SNR10 macro-F1 | labels | recipe | tag | date |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| overlap_hetero | analysis | - | 0.9598 | - | 0.9684 | 0.9887 | 0.9937 | 0.0929 | 0.0026 | - | v2 | - | - | 2026-10-29 |
| F_generalist_stacking | ensemble | v2 | 0.9217 | 0.9433 | 0.9433 | 0.9684 | 0.9781 | 0.1142 | 0.0039 | 0.8555 | v2 | - | - | 2026-10-29 |
| E0m_v2 | generalist | efficientat | 0.9170 | 0.9382 | 0.9367 | 0.9703 | 0.9859 | 0.1759 | 0.0118 | 0.8248 | v2 | - | - | 2026-10-29 |
| F_generalist_soft | ensemble | v2 | 0.9129 | 0.9425 | 0.9396 | 0.9687 | 0.9812 | 0.1411 | 0.0066 | 0.8377 | v2 | - | - | 2026-10-29 |
| F_generalist_weighted | ensemble | v2 | 0.9129 | 0.9425 | 0.9396 | 0.9687 | 0.9812 | 0.1411 | 0.0066 | 0.8371 | v2 | - | - | 2026-10-29 |
| F_generalist_hard | ensemble | v2 | 0.9103 | 0.9424 | 0.9381 | 0.9693 | 0.9837 | 0.1475 | 0.0066 | 0.8340 | v2 | - | - | 2026-10-29 |
| E2k_v2 | generalist | mnv4 | 0.9100 | 0.9231 | 0.9103 | 0.9546 | 0.9609 | 0.1759 | 0.0237 | 0.8181 | v2 | - | - | 2026-10-29 |
| F_generalist_stacking_mlp | ensemble | v2 | 0.9022 | 0.9381 | 0.9386 | 0.9593 | 0.9837 | 0.1028 | 0.0013 | 0.8226 | v2 | - | - | 2026-10-29 |
| F_generalist_weighted_premusan | ensemble | efficientat+mnv4+yamnet | 0.8898 | - | 0.8748 | 0.8470 | 0.9797 | 0.1454 | 0.0039 | 0.7818 | v1 | - | premusan | 2026-10-29 |
| F_generalist_soft_premusan | ensemble | efficientat+mnv4+yamnet | 0.8895 | - | 0.8744 | 0.8467 | 0.9793 | 0.1454 | 0.0039 | 0.7805 | v1 | - | premusan | 2026-10-29 |
| F_generalist_stacking_premusan | ensemble | efficientat+mnv4+yamnet | 0.8862 | - | 0.8788 | 0.8448 | 0.9790 | 0.1213 | 0.0013 | 0.7838 | v1 | - | premusan | 2026-10-29 |
| E0_efficientat_generalist | generalist | efficientat | 0.8844 | - | 0.8717 | 0.8545 | 0.9944 | 0.1851 | 0.0105 | 0.7780 | v1 | - | - | 2026-10-29 |
| F_best_single_premusan | ensemble | efficientat+mnv4+yamnet | 0.8844 | - | 0.8717 | 0.8545 | 0.9944 | 0.1851 | 0.0105 | 0.7780 | v1 | - | premusan | 2026-10-29 |
| F_generalist_hard_premusan | ensemble | efficientat+mnv4+yamnet | 0.8842 | - | 0.8726 | 0.8492 | 0.9850 | 0.1567 | 0.0039 | 0.7771 | v1 | - | premusan | 2026-10-29 |
| E1k_v2 | generalist | yamnet_ft | 0.8833 | 0.9205 | 0.9245 | 0.9553 | 0.9753 | 0.1284 | 0.0105 | 0.7955 | v2 | - | - | 2026-10-29 |
| F_best_single | ensemble | v2 | 0.8833 | 0.9205 | 0.9245 | 0.9553 | 0.9753 | 0.1284 | 0.0105 | 0.7955 | v2 | - | - | 2026-10-29 |
| E2_mnv4_generalist | generalist | mnv4 | 0.8706 | - | 0.8509 | 0.8273 | 0.9540 | 0.1369 | 0.0105 | 0.6955 | v1 | - | - | 2026-10-29 |
| E0m_efficientat_generalist_musan | generalist | efficientat | 0.8699 | - | 0.8671 | 0.8385 | 0.9847 | 0.1688 | 0.0132 | 0.8210 | v1 | - | - | 2026-10-29 |
| E2k_mnv4_kd | generalist | mnv4 | 0.8690 | - | 0.8452 | 0.8342 | 0.9653 | 0.1858 | 0.0303 | 0.8070 | v1 | - | - | 2026-10-29 |
| E1_v2 | generalist | yamnet_frozen | 0.8578 | 0.8848 | 0.8812 | 0.9205 | 0.9571 | 0.2234 | 0.0342 | 0.5300 | v2 | - | - | 2026-10-29 |
| E1k_yamnet_kd | generalist | yamnet_ft | 0.8517 | - | 0.8584 | 0.8257 | 0.9684 | 0.1319 | 0.0118 | 0.7797 | v1 | - | - | 2026-10-29 |
| E1_yamnet_generalist | generalist | yamnet_frozen | 0.8095 | - | 0.8128 | 0.7982 | 0.9503 | 0.2113 | 0.0329 | 0.5327 | v1 | - | - | 2026-10-29 |

## D. operating points

| experiment | labels | recipe | scale | emerg recall | daily precision | caution F1 | macro-F1 | macro-F1 w/o car_horn | bg FA | bg FA strict | cost | emerg group recall | PR-AUC emerg | PR-AUC daily | PR-AUC caution |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F_generalist_stacking | v2 | - | 1.00 | 0.9481 | 0.8995 | 0.9330 | 0.9126 | 0.9377 | 0.1113 | 0.0066 | 0.193 | 0.9599 | 0.9959 | 0.9767 | 0.9559 |
| F_generalist_stacking_mlp | v2 | - | 1.00 | 0.9465 | 0.9033 | 0.9134 | 0.9100 | 0.9393 | 0.1050 | 0.0026 | 0.196 | 0.9587 | 0.9913 | 0.9824 | 0.9550 |
| E0m_v2 | v2 | - | 2.80 | 0.2369 | 0.8848 | 0.3205 | 0.2902 | 0.3125 | 0.0227 | 0.0132 | 2.255 | 0.2525 | 0.9941 | 0.9731 | 0.9689 |
| F_generalist_hard | v2 | - | 17.19 | 0.0460 | 0.8533 | 0.3089 | 0.2294 | 0.2471 | 0.0397 | 0.0066 | 2.751 | 0.0472 | 0.9773 | 0.9221 | 0.9062 |
| E2k_v2 | v2 | - | 6.44 | 0.0504 | 0.8610 | 0.0000 | 0.2060 | 0.1717 | 0.0177 | 0.0105 | 2.775 | 0.0544 | 0.9872 | 0.9424 | 0.9457 |
| E1k_v2 | v2 | - | 14.78 | 0.0457 | 0.9811 | 0.0000 | 0.1591 | 0.1713 | 0.0043 | 0.0039 | 2.786 | 0.0476 | 0.9915 | 0.9618 | 0.9342 |
| F_best_single | v2 | - | 14.78 | 0.0457 | 0.9811 | 0.0000 | 0.1591 | 0.1713 | 0.0043 | 0.0039 | 2.786 | 0.0476 | 0.9915 | 0.9618 | 0.9342 |
| F_generalist_soft | v2 | - | 6.94 | 0.0460 | 0.8496 | 0.0000 | 0.1588 | 0.1710 | 0.0156 | 0.0092 | 2.787 | 0.0507 | 0.9957 | 0.9738 | 0.9647 |
| F_generalist_weighted | v2 | - | 6.94 | 0.0460 | 0.8496 | 0.0000 | 0.1588 | 0.1710 | 0.0156 | 0.0092 | 2.787 | 0.0507 | 0.9957 | 0.9738 | 0.9647 |
| E1_v2 | v2 | - | 9.39 | 0.0435 | - | 0.0000 | 0.0887 | 0.0955 | 0.0071 | 0.0079 | 2.819 | 0.0494 | 0.9782 | 0.9300 | 0.9210 |
