# S_mn10_emergency

model=efficientat mode=specialist classes=6 train=48060 val=5762 batch=64 lr=2e-05 cap=3000 teacher=-

| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |
|---|---|---|---|---|---|---|---|
| init | - | - | 0.1417 | 0.2575 | - | - | |
| 0 | 0.7977 | 0.2265 | 0.9237 | 0.9552 | 1.99e-05 | 69 | * |
| 1 | 0.7770 | 0.2654 | 0.9251 | 0.9603 | 1.95e-05 | 55 | * |
| 2 | 0.7739 | 0.2749 | 0.9243 | 0.9610 | 1.89e-05 | 55 |  |
| 3 | 0.7661 | 0.2502 | 0.9209 | 0.9597 | 1.81e-05 | 55 |  |
| 4 | 0.7672 | 0.3159 | 0.9112 | 0.9544 | 1.71e-05 | 55 |  |
| 5 | 0.7645 | 0.2541 | 0.9267 | 0.9634 | 1.59e-05 | 55 | * |
| 6 | 0.7598 | 0.2692 | 0.9360 | 0.9695 | 1.45e-05 | 55 | * |
| 7 | 0.7597 | 0.2453 | 0.9304 | 0.9641 | 1.31e-05 | 55 |  |
| 8 | 0.7613 | 0.2140 | 0.9383 | 0.9691 | 1.16e-05 | 55 | * |
| 9 | 0.7562 | 0.2050 | 0.9431 | 0.9728 | 1.00e-05 | 55 | * |
| 10 | 0.7456 | 0.2232 | 0.9331 | 0.9693 | 8.44e-06 | 55 |  |
| 11 | 0.7490 | 0.2260 | 0.9325 | 0.9653 | 6.91e-06 | 55 |  |
| 12 | 0.7357 | 0.2326 | 0.9337 | 0.9670 | 5.46e-06 | 55 |  |
| 13 | 0.7350 | 0.2057 | 0.9403 | 0.9714 | 4.12e-06 | 55 |  |
| 14 | 0.7392 | 0.2153 | 0.9368 | 0.9693 | 2.93e-06 | 55 |  |
| 15 | 0.7368 | 0.2170 | 0.9340 | 0.9674 | 1.91e-06 | 55 |  |
| 16 | 0.7452 | 0.2221 | 0.9316 | 0.9660 | 1.09e-06 | 55 |  |
| 17 | 0.7361 | 0.2237 | 0.9324 | 0.9667 | 4.90e-07 | 55 |  |

best val macro-F1 = 0.9431

### specialisation gain (val per-class F1: init = warm start before fine-tune, best = selected epoch)

| class | init F1 | best F1 | delta |
|---|---|---|---|
| alarm | 0.0678 | 0.9488 | +0.8810 |
| fire_alarm | 0.2595 | 0.9687 | +0.7092 |
| scream | 0.0303 | 0.9466 | +0.9163 |
| cry | 0.0000 | 0.9249 | +0.9249 |
| car_horn | 0.0593 | 0.8837 | +0.8244 |
| other | 0.4334 | 0.9857 | +0.5523 |

mean delta over own classes = +0.8512


## evaluate (2026-10-30) best epoch 9

#### vs generalist E0m_v2 (remapped to own+other), val: mean delta own +0.0013

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.9419 | 0.9488 | +0.0069 |
| fire_alarm | 0.9611 | 0.9687 | +0.0076 |
| scream | 0.9394 | 0.9466 | +0.0072 |
| cry | 0.9316 | 0.9249 | -0.0067 |
| car_horn | 0.8923 | 0.8837 | -0.0086 |
| other | 0.9861 | 0.9857 | -0.0004 |

### val: acc 0.9728 macro-F1 0.9345 reject(non-target events) 0.993886462882096 reject(bg) 0.950592885375494

| true \ pred | alarm | fire_alarm | scream | cry | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 556 | 6 | 0 | 0 | 0 | 7 |
| fire_alarm | 36 | 712 | 0 | 0 | 0 | 4 |
| scream | 1 | 0 | 124 | 4 | 1 | 3 |
| cry | 0 | 0 | 1 | 437 | 0 | 3 |
| car_horn | 0 | 0 | 0 | 0 | 57 | 2 |
| other | 10 | 0 | 4 | 63 | 12 | 3719 |

#### vs generalist E0m_v2 (remapped to own+other), test: mean delta own -0.0125

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.9702 | 0.9681 | -0.0022 |
| fire_alarm | 0.9892 | 0.9903 | +0.0012 |
| scream | 0.9450 | 0.9453 | +0.0004 |
| cry | 0.9330 | 0.9099 | -0.0231 |
| car_horn | 0.6410 | 0.6024 | -0.0386 |
| other | 0.9877 | 0.9837 | -0.0041 |

### test: acc 0.9736 macro-F1 0.8832 reject(non-target events) 0.9957627118644068 reject(bg) 0.9418439716312057

| true \ pred | alarm | fire_alarm | scream | cry | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 652 | 0 | 3 | 0 | 22 | 9 |
| fire_alarm | 2 | 821 | 2 | 0 | 0 | 12 |
| scream | 0 | 0 | 147 | 0 | 0 | 0 |
| cry | 0 | 0 | 4 | 399 | 0 | 8 |
| car_horn | 0 | 0 | 0 | 0 | 25 | 1 |
| other | 7 | 0 | 8 | 67 | 10 | 3678 |

#### vs generalist E0m_v2 (remapped to own+other), noisy_snr20: mean delta own -0.0030

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.7370 | 0.7389 | +0.0020 |
| fire_alarm | 0.6677 | 0.6677 | +0.0000 |
| scream | 0.9577 | 0.9542 | -0.0034 |
| cry | 0.9139 | 0.9032 | -0.0107 |
| car_horn | 0.6000 | 0.5974 | -0.0026 |
| other | 0.9842 | 0.9817 | -0.0026 |

### noisy_snr20: acc 0.9028 macro-F1 0.7723 reject(non-target events) 0.9944915254237288 reject(bg) 0.9375886524822695

| true \ pred | alarm | fire_alarm | scream | cry | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 651 | 405 | 3 | 0 | 23 | 16 |
| fire_alarm | 0 | 416 | 1 | 0 | 0 | 8 |
| scream | 0 | 0 | 146 | 0 | 0 | 1 |
| cry | 0 | 0 | 1 | 401 | 0 | 9 |
| car_horn | 1 | 0 | 0 | 0 | 23 | 2 |
| other | 12 | 0 | 8 | 76 | 5 | 3669 |

#### vs generalist E0m_v2 (remapped to own+other), noisy_snr15: mean delta own -0.0038

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.7309 | 0.7310 | +0.0001 |
| fire_alarm | 0.6672 | 0.6683 | +0.0011 |
| scream | 0.9484 | 0.9419 | -0.0065 |
| cry | 0.9141 | 0.8969 | -0.0171 |
| car_horn | 0.5714 | 0.5750 | +0.0036 |
| other | 0.9817 | 0.9791 | -0.0025 |

### noisy_snr15: acc 0.8991 macro-F1 0.7626 reject(non-target events) 0.9936440677966102 reject(bg) 0.9319148936170213

| true \ pred | alarm | fire_alarm | scream | cry | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 644 | 404 | 5 | 0 | 24 | 21 |
| fire_alarm | 0 | 416 | 1 | 0 | 0 | 8 |
| scream | 0 | 0 | 146 | 0 | 0 | 1 |
| cry | 0 | 0 | 3 | 396 | 0 | 12 |
| car_horn | 0 | 0 | 0 | 0 | 23 | 3 |
| other | 20 | 0 | 8 | 76 | 7 | 3659 |

#### vs generalist E0m_v2 (remapped to own+other), noisy_snr10: mean delta own +0.0010

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.7272 | 0.7259 | -0.0012 |
| fire_alarm | 0.6699 | 0.6667 | -0.0032 |
| scream | 0.9355 | 0.9385 | +0.0030 |
| cry | 0.8958 | 0.8897 | -0.0061 |
| car_horn | 0.5393 | 0.5517 | +0.0124 |
| other | 0.9778 | 0.9770 | -0.0007 |

### noisy_snr10: acc 0.8960 macro-F1 0.7545 reject(non-target events) 0.9927966101694915 reject(bg) 0.9319148936170213

| true \ pred | alarm | fire_alarm | scream | cry | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 641 | 396 | 2 | 0 | 32 | 27 |
| fire_alarm | 3 | 412 | 1 | 1 | 0 | 8 |
| scream | 1 | 0 | 145 | 0 | 0 | 1 |
| cry | 0 | 0 | 3 | 387 | 0 | 21 |
| car_horn | 0 | 0 | 0 | 0 | 24 | 2 |
| other | 23 | 3 | 11 | 71 | 5 | 3657 |

