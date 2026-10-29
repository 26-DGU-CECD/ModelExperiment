# H_mn04_emergency

model=efficientat mode=specialist classes=6 train=48060 val=5762 batch=64 lr=2e-05 cap=3000 teacher=-

| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |
|---|---|---|---|---|---|---|---|
| init | - | - | 0.0945 | 0.2242 | - | - | |
| 0 | 0.8326 | 0.2770 | 0.9172 | 0.9535 | 1.99e-05 | 63 | * |
| 1 | 0.8100 | 0.3052 | 0.9057 | 0.9476 | 1.95e-05 | 49 |  |
| 2 | 0.8106 | 0.2594 | 0.9147 | 0.9486 | 1.89e-05 | 48 |  |
| 3 | 0.8017 | 0.2638 | 0.9226 | 0.9575 | 1.81e-05 | 47 | * |
| 4 | 0.8029 | 0.2761 | 0.9202 | 0.9556 | 1.71e-05 | 48 |  |
| 5 | 0.7998 | 0.2646 | 0.9223 | 0.9561 | 1.59e-05 | 47 |  |
| 6 | 0.7929 | 0.2508 | 0.9242 | 0.9589 | 1.45e-05 | 48 | * |
| 7 | 0.7953 | 0.2430 | 0.9281 | 0.9603 | 1.31e-05 | 49 | * |
| 8 | 0.7968 | 0.2341 | 0.9285 | 0.9613 | 1.16e-05 | 50 | * |
| 9 | 0.7917 | 0.2446 | 0.9294 | 0.9620 | 1.00e-05 | 48 | * |
| 10 | 0.7842 | 0.2485 | 0.9268 | 0.9603 | 8.44e-06 | 50 |  |
| 11 | 0.7871 | 0.2581 | 0.9268 | 0.9596 | 6.91e-06 | 51 |  |
| 12 | 0.7733 | 0.2331 | 0.9280 | 0.9610 | 5.46e-06 | 49 |  |
| 13 | 0.7699 | 0.2301 | 0.9281 | 0.9615 | 4.12e-06 | 47 |  |
| 14 | 0.7794 | 0.2384 | 0.9268 | 0.9596 | 2.93e-06 | 47 |  |
| 15 | 0.7739 | 0.2341 | 0.9285 | 0.9611 | 1.91e-06 | 46 |  |
| 16 | 0.7828 | 0.2390 | 0.9269 | 0.9597 | 1.09e-06 | 46 |  |
| 17 | 0.7738 | 0.2362 | 0.9281 | 0.9610 | 4.90e-07 | 47 |  |

best val macro-F1 = 0.9294

### specialisation gain (val per-class F1: init = warm start before fine-tune, best = selected epoch)

| class | init F1 | best F1 | delta |
|---|---|---|---|
| alarm | 0.0026 | 0.9495 | +0.9469 |
| fire_alarm | 0.0564 | 0.9790 | +0.9226 |
| scream | 0.0238 | 0.9313 | +0.9075 |
| cry | 0.0326 | 0.8708 | +0.8381 |
| car_horn | 0.0000 | 0.8702 | +0.8702 |
| other | 0.4517 | 0.9756 | +0.5239 |

mean delta over own classes = +0.8971


## evaluate (2026-10-30) best epoch 9

#### vs generalist G_mn04 (remapped to own+other), val: mean delta own +0.0039

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.9422 | 0.9495 | +0.0073 |
| fire_alarm | 0.9693 | 0.9790 | +0.0097 |
| scream | 0.9104 | 0.9313 | +0.0208 |
| cry | 0.8826 | 0.8708 | -0.0118 |
| car_horn | 0.8769 | 0.8702 | -0.0067 |
| other | 0.9769 | 0.9756 | -0.0013 |

### val: acc 0.9620 macro-F1 0.9202 reject(non-target events) 0.9895196506550218 reject(bg) 0.9051383399209486

| true \ pred | alarm | fire_alarm | scream | cry | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 564 | 0 | 0 | 1 | 0 | 4 |
| fire_alarm | 28 | 722 | 0 | 0 | 0 | 2 |
| scream | 3 | 0 | 122 | 4 | 0 | 4 |
| cry | 0 | 0 | 1 | 438 | 0 | 2 |
| car_horn | 0 | 0 | 0 | 0 | 57 | 2 |
| other | 24 | 1 | 6 | 122 | 15 | 3640 |

#### vs generalist G_mn04 (remapped to own+other), test: mean delta own +0.0201

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.9472 | 0.9513 | +0.0041 |
| fire_alarm | 0.9741 | 0.9639 | -0.0102 |
| scream | 0.9515 | 0.9545 | +0.0031 |
| cry | 0.8792 | 0.8697 | -0.0096 |
| car_horn | 0.4583 | 0.5714 | +0.1131 |
| other | 0.9776 | 0.9692 | -0.0084 |

### test: acc 0.9554 macro-F1 0.8622 reject(non-target events) 0.9923728813559322 reject(bg) 0.8617021276595744

| true \ pred | alarm | fire_alarm | scream | cry | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 655 | 0 | 3 | 0 | 24 | 4 |
| fire_alarm | 0 | 827 | 0 | 4 | 0 | 6 |
| scream | 0 | 0 | 147 | 0 | 0 | 0 |
| cry | 0 | 1 | 1 | 407 | 0 | 2 |
| car_horn | 3 | 0 | 0 | 0 | 22 | 1 |
| other | 33 | 51 | 10 | 114 | 5 | 3557 |

#### vs generalist G_mn04 (remapped to own+other), noisy_snr20: mean delta own +0.0160

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.7218 | 0.7320 | +0.0102 |
| fire_alarm | 0.6480 | 0.6430 | -0.0051 |
| scream | 0.9385 | 0.9412 | +0.0027 |
| cry | 0.8782 | 0.8682 | -0.0100 |
| car_horn | 0.4466 | 0.5287 | +0.0821 |
| other | 0.9742 | 0.9672 | -0.0071 |

### noisy_snr20: acc 0.8838 macro-F1 0.7426 reject(non-target events) 0.986864406779661 reject(bg) 0.8652482269503546

| true \ pred | alarm | fire_alarm | scream | cry | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 657 | 402 | 3 | 1 | 26 | 9 |
| fire_alarm | 2 | 416 | 0 | 2 | 0 | 5 |
| scream | 1 | 0 | 144 | 1 | 0 | 1 |
| cry | 0 | 0 | 2 | 405 | 0 | 4 |
| car_horn | 2 | 0 | 0 | 0 | 23 | 1 |
| other | 35 | 51 | 10 | 113 | 12 | 3549 |

#### vs generalist G_mn04 (remapped to own+other), noisy_snr15: mean delta own +0.0189

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.7119 | 0.7229 | +0.0110 |
| fire_alarm | 0.6512 | 0.6448 | -0.0064 |
| scream | 0.9016 | 0.9191 | +0.0175 |
| cry | 0.8615 | 0.8596 | -0.0019 |
| car_horn | 0.4364 | 0.5106 | +0.0743 |
| other | 0.9690 | 0.9653 | -0.0038 |

### noisy_snr15: acc 0.8802 macro-F1 0.7314 reject(non-target events) 0.986864406779661 reject(bg) 0.8631205673758865

| true \ pred | alarm | fire_alarm | scream | cry | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 647 | 398 | 4 | 3 | 32 | 14 |
| fire_alarm | 5 | 413 | 0 | 1 | 0 | 6 |
| scream | 1 | 0 | 142 | 1 | 0 | 3 |
| cry | 0 | 2 | 1 | 401 | 0 | 7 |
| car_horn | 1 | 0 | 0 | 0 | 24 | 1 |
| other | 38 | 43 | 15 | 116 | 12 | 3546 |

#### vs generalist G_mn04 (remapped to own+other), noisy_snr10: mean delta own +0.0099

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.7047 | 0.7161 | +0.0114 |
| fire_alarm | 0.6480 | 0.6484 | +0.0004 |
| scream | 0.9068 | 0.8981 | -0.0087 |
| cry | 0.8600 | 0.8497 | -0.0102 |
| car_horn | 0.3590 | 0.4158 | +0.0569 |
| other | 0.9654 | 0.9612 | -0.0042 |

### noisy_snr10: acc 0.8748 macro-F1 0.7056 reject(non-target events) 0.9822033898305085 reject(bg) 0.8602836879432624

| true \ pred | alarm | fire_alarm | scream | cry | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 642 | 396 | 3 | 3 | 36 | 18 |
| fire_alarm | 6 | 413 | 0 | 0 | 0 | 6 |
| scream | 1 | 0 | 141 | 1 | 0 | 4 |
| cry | 1 | 0 | 2 | 393 | 0 | 15 |
| car_horn | 1 | 0 | 1 | 0 | 21 | 3 |
| other | 44 | 40 | 20 | 117 | 18 | 3531 |

