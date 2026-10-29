# S2_yamnet_emergency

model=yamnet_ft mode=specialist classes=6 train=48060 val=5762 batch=64 lr=2e-05 cap=3000 teacher=-

| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |
|---|---|---|---|---|---|---|---|
| init | - | - | 0.3901 | 0.3492 | - | - | |
| 0 | 0.6813 | 0.2366 | 0.9288 | 0.9695 | 1.99e-05 | 26 | * |
| 1 | 0.6580 | 0.2614 | 0.9316 | 0.9734 | 1.95e-05 | 16 | * |
| 2 | 0.6562 | 0.2130 | 0.9340 | 0.9745 | 1.89e-05 | 16 | * |
| 3 | 0.6490 | 0.2605 | 0.9340 | 0.9738 | 1.81e-05 | 17 |  |
| 4 | 0.6542 | 0.2363 | 0.9324 | 0.9741 | 1.71e-05 | 17 |  |
| 5 | 0.6542 | 0.2601 | 0.9240 | 0.9721 | 1.59e-05 | 17 |  |
| 6 | 0.6485 | 0.2484 | 0.9374 | 0.9759 | 1.45e-05 | 17 | * |
| 7 | 0.6484 | 0.2483 | 0.9289 | 0.9726 | 1.31e-05 | 16 |  |
| 8 | 0.6473 | 0.2244 | 0.9384 | 0.9783 | 1.16e-05 | 16 | * |
| 9 | 0.6463 | 0.2244 | 0.9380 | 0.9778 | 1.00e-05 | 16 |  |
| 10 | 0.6373 | 0.2251 | 0.9306 | 0.9724 | 8.44e-06 | 17 |  |
| 11 | 0.6406 | 0.2321 | 0.9346 | 0.9748 | 6.91e-06 | 16 |  |
| 12 | 0.6290 | 0.2438 | 0.9275 | 0.9719 | 5.46e-06 | 16 |  |
| 13 | 0.6292 | 0.2265 | 0.9345 | 0.9747 | 4.12e-06 | 16 |  |
| 14 | 0.6362 | 0.2323 | 0.9292 | 0.9724 | 2.93e-06 | 16 |  |
| 15 | 0.6323 | 0.2262 | 0.9351 | 0.9757 | 1.91e-06 | 16 |  |
| 16 | 0.6377 | 0.2234 | 0.9331 | 0.9757 | 1.09e-06 | 16 |  |

best val macro-F1 = 0.9384

### specialisation gain (val per-class F1: init = warm start before fine-tune, best = selected epoch)

| class | init F1 | best F1 | delta |
|---|---|---|---|
| alarm | 0.8517 | 0.9816 | +0.1299 |
| fire_alarm | 0.9798 | 0.9926 | +0.0128 |
| scream | 0.0000 | 0.9057 | +0.9057 |
| cry | 0.2993 | 0.9290 | +0.6296 |
| car_horn | 0.0026 | 0.8358 | +0.8332 |
| other | 0.2070 | 0.9860 | +0.7790 |

mean delta over own classes = +0.5022


## evaluate (2026-10-29) best epoch 8

#### vs generalist E1k_v2 (remapped to own+other), val: mean delta own +0.0045

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.9658 | 0.9816 | +0.0158 |
| fire_alarm | 0.9805 | 0.9926 | +0.0121 |
| scream | 0.9057 | 0.9057 | +0.0000 |
| cry | 0.9255 | 0.9290 | +0.0035 |
| car_horn | 0.8444 | 0.8358 | -0.0086 |
| other | 0.9845 | 0.9860 | +0.0015 |

### val: acc 0.9783 macro-F1 0.9289 reject(non-target events) 0.9895196506550218 reject(bg) 0.9670619235836627

| true \ pred | alarm | fire_alarm | scream | cry | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 560 | 1 | 0 | 3 | 0 | 5 |
| fire_alarm | 6 | 742 | 0 | 0 | 0 | 4 |
| scream | 0 | 0 | 120 | 8 | 0 | 5 |
| cry | 0 | 0 | 1 | 425 | 0 | 15 |
| car_horn | 0 | 0 | 0 | 0 | 56 | 3 |
| other | 6 | 0 | 11 | 38 | 19 | 3734 |

#### vs generalist E1k_v2 (remapped to own+other), test: mean delta own +0.0007

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.9461 | 0.9233 | -0.0228 |
| fire_alarm | 0.9964 | 0.9755 | -0.0209 |
| scream | 0.9574 | 0.9505 | -0.0069 |
| cry | 0.9271 | 0.9176 | -0.0095 |
| car_horn | 0.4000 | 0.4634 | +0.0634 |
| other | 0.9858 | 0.9833 | -0.0025 |

### test: acc 0.9661 macro-F1 0.8461 reject(non-target events) 0.9915254237288136 reject(bg) 0.9702127659574468

| true \ pred | alarm | fire_alarm | scream | cry | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 620 | 0 | 3 | 0 | 34 | 29 |
| fire_alarm | 34 | 797 | 0 | 0 | 0 | 6 |
| scream | 0 | 0 | 144 | 0 | 0 | 3 |
| cry | 0 | 0 | 2 | 390 | 0 | 19 |
| car_horn | 0 | 0 | 0 | 0 | 19 | 7 |
| other | 3 | 0 | 7 | 49 | 3 | 3708 |

#### vs generalist E1k_v2 (remapped to own+other), noisy_snr20: mean delta own +0.0092

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.7192 | 0.7185 | -0.0007 |
| fire_alarm | 0.6720 | 0.6650 | -0.0069 |
| scream | 0.9316 | 0.9495 | +0.0179 |
| cry | 0.9171 | 0.8947 | -0.0223 |
| car_horn | 0.3913 | 0.4494 | +0.0581 |
| other | 0.9837 | 0.9799 | -0.0037 |

### noisy_snr20: acc 0.8971 macro-F1 0.7354 reject(non-target events) 0.9877118644067797 reject(bg) 0.9602836879432625

| true \ pred | alarm | fire_alarm | scream | cry | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 624 | 400 | 2 | 2 | 38 | 32 |
| fire_alarm | 11 | 411 | 0 | 0 | 0 | 3 |
| scream | 0 | 0 | 141 | 0 | 0 | 6 |
| cry | 0 | 0 | 1 | 391 | 0 | 19 |
| car_horn | 0 | 0 | 0 | 0 | 20 | 6 |
| other | 4 | 0 | 6 | 70 | 5 | 3685 |

#### vs generalist E1k_v2 (remapped to own+other), noisy_snr15: mean delta own +0.0107

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.7166 | 0.7166 | -0.0000 |
| fire_alarm | 0.6731 | 0.6650 | -0.0080 |
| scream | 0.9016 | 0.9329 | +0.0313 |
| cry | 0.9005 | 0.8947 | -0.0057 |
| car_horn | 0.3958 | 0.4318 | +0.0360 |
| other | 0.9793 | 0.9782 | -0.0011 |

### noisy_snr15: acc 0.8952 macro-F1 0.7282 reject(non-target events) 0.986864406779661 reject(bg) 0.9574468085106383

| true \ pred | alarm | fire_alarm | scream | cry | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 622 | 400 | 3 | 0 | 37 | 36 |
| fire_alarm | 9 | 411 | 0 | 0 | 0 | 5 |
| scream | 0 | 0 | 139 | 1 | 0 | 7 |
| cry | 0 | 0 | 2 | 391 | 0 | 18 |
| car_horn | 0 | 0 | 0 | 0 | 19 | 7 |
| other | 7 | 0 | 7 | 71 | 6 | 3679 |

#### vs generalist E1k_v2 (remapped to own+other), noisy_snr10: mean delta own +0.0067

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.7161 | 0.7168 | +0.0007 |
| fire_alarm | 0.6709 | 0.6661 | -0.0048 |
| scream | 0.9057 | 0.9200 | +0.0143 |
| cry | 0.9048 | 0.8851 | -0.0197 |
| car_horn | 0.3689 | 0.4118 | +0.0428 |
| other | 0.9787 | 0.9767 | -0.0020 |

### noisy_snr10: acc 0.8925 macro-F1 0.7199 reject(non-target events) 0.986864406779661 reject(bg) 0.948936170212766

| true \ pred | alarm | fire_alarm | scream | cry | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 620 | 397 | 3 | 0 | 48 | 30 |
| fire_alarm | 5 | 414 | 0 | 0 | 0 | 6 |
| scream | 0 | 0 | 138 | 2 | 0 | 7 |
| cry | 0 | 0 | 2 | 385 | 0 | 24 |
| car_horn | 0 | 0 | 0 | 0 | 21 | 5 |
| other | 7 | 7 | 10 | 72 | 7 | 3667 |

