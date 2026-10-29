# SB_efficientat_best

model=efficientat mode=specialist classes=6 train=48060 val=5762 batch=64 lr=2e-05 cap=3000 teacher=-

| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |
|---|---|---|---|---|---|---|---|
| init | - | - | 0.1311 | 0.2117 | - | - | |
| 0 | 0.8645 | 0.2940 | 0.9307 | 0.9405 | 1.99e-05 | 72 | * |
| 1 | 0.8493 | 0.2777 | 0.9433 | 0.9540 | 1.95e-05 | 56 | * |
| 2 | 0.8440 | 0.2646 | 0.9414 | 0.9519 | 1.89e-05 | 56 |  |
| 3 | 0.8400 | 0.2447 | 0.9372 | 0.9485 | 1.81e-05 | 56 |  |
| 4 | 0.8388 | 0.2793 | 0.9392 | 0.9549 | 1.71e-05 | 56 |  |
| 5 | 0.8399 | 0.2570 | 0.9451 | 0.9563 | 1.59e-05 | 56 | * |
| 6 | 0.8331 | 0.3177 | 0.9415 | 0.9537 | 1.45e-05 | 58 |  |
# SB_efficientat_best

model=efficientat mode=specialist classes=6 train=48060 val=5762 batch=64 lr=2e-05 cap=3000 teacher=-

| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |
|---|---|---|---|---|---|---|---|
| init | - | - | 0.1311 | 0.2117 | - | - | |
| 0 | 0.8645 | 0.2940 | 0.9307 | 0.9405 | 1.99e-05 | 72 | * |
| 1 | 0.8493 | 0.2777 | 0.9433 | 0.9540 | 1.95e-05 | 56 | * |
| 2 | 0.8440 | 0.2646 | 0.9414 | 0.9519 | 1.89e-05 | 56 |  |
| 3 | 0.8400 | 0.2447 | 0.9372 | 0.9485 | 1.81e-05 | 56 |  |
| 4 | 0.8388 | 0.2793 | 0.9392 | 0.9549 | 1.71e-05 | 56 |  |
| 5 | 0.8399 | 0.2570 | 0.9451 | 0.9563 | 1.59e-05 | 56 | * |
| 6 | 0.8331 | 0.3177 | 0.9415 | 0.9537 | 1.45e-05 | 56 |  |
| 7 | 0.8344 | 0.2730 | 0.9408 | 0.9514 | 1.31e-05 | 56 |  |
| 8 | 0.8340 | 0.2750 | 0.9425 | 0.9526 | 1.16e-05 | 56 |  |
| 9 | 0.8304 | 0.2725 | 0.9442 | 0.9545 | 1.00e-05 | 54 |  |
| 10 | 0.8191 | 0.2622 | 0.9414 | 0.9530 | 8.44e-06 | 31 |  |
| 11 | 0.8223 | 0.2809 | 0.9434 | 0.9542 | 6.91e-06 | 32 |  |
| 12 | 0.8145 | 0.2732 | 0.9453 | 0.9559 | 5.46e-06 | 32 | * |
| 13 | 0.8106 | 0.2535 | 0.9432 | 0.9542 | 4.12e-06 | 32 |  |
| 14 | 0.8162 | 0.2558 | 0.9445 | 0.9557 | 2.93e-06 | 31 |  |
| 15 | 0.8149 | 0.2614 | 0.9409 | 0.9531 | 1.91e-06 | 46 |  |
| 16 | 0.8235 | 0.2576 | 0.9440 | 0.9561 | 1.09e-06 | 45 |  |
| 17 | 0.8147 | 0.2589 | 0.9452 | 0.9563 | 4.90e-07 | 55 |  |
| 18 | 0.8222 | 0.2612 | 0.9427 | 0.9551 | 1.23e-07 | 56 |  |
| 19 | 0.8162 | 0.2609 | 0.9435 | 0.9554 | 0.00e+00 | 55 |  |

best val macro-F1 = 0.9453

### specialisation gain (val per-class F1: init = warm start before fine-tune, best = selected epoch)

| class | init F1 | best F1 | delta |
|---|---|---|---|
| water | 0.0598 | 0.8842 | +0.8244 |
| scream | 0.0917 | 0.9502 | +0.8585 |
| glass_break | 0.1139 | 0.9496 | +0.8358 |
| baby_cry | 0.0000 | 0.9847 | +0.9847 |
| cry | 0.2088 | 0.9362 | +0.7274 |
| other | 0.3125 | 0.9670 | +0.6545 |

mean delta over own classes = +0.8462


## evaluate (2026-10-30) best epoch 12

#### vs generalist E0m_v2 (remapped to own+other), val: mean delta own +0.0020

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.8862 | 0.8842 | -0.0020 |
| scream | 0.9394 | 0.9502 | +0.0108 |
| glass_break | 0.9532 | 0.9496 | -0.0035 |
| baby_cry | 0.9847 | 0.9847 | +0.0000 |
| cry | 0.9316 | 0.9362 | +0.0046 |
| other | 0.9670 | 0.9670 | -0.0000 |

### val: acc 0.9559 macro-F1 0.9410 reject(non-target events) 0.9947575360419397 reject(bg) 0.8820816864295126

| true \ pred | water | scream | glass_break | baby_cry | cry | other |
|---|---|---|---|---|---|---|
| water | 397 | 1 | 1 | 0 | 0 | 23 |
| scream | 0 | 124 | 0 | 0 | 4 | 5 |
| glass_break | 0 | 0 | 745 | 0 | 0 | 21 |
| baby_cry | 0 | 0 | 0 | 193 | 0 | 0 |
| cry | 0 | 1 | 0 | 0 | 433 | 7 |
| other | 79 | 2 | 57 | 6 | 47 | 3616 |

#### vs generalist E0m_v2 (remapped to own+other), test: mean delta own +0.0029

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.9287 | 0.9309 | +0.0022 |
| scream | 0.9450 | 0.9450 | +0.0000 |
| glass_break | 0.9616 | 0.9647 | +0.0032 |
| baby_cry | 0.9412 | 0.9481 | +0.0070 |
| cry | 0.9330 | 0.9351 | +0.0020 |
| other | 0.9710 | 0.9728 | +0.0018 |

### test: acc 0.9634 macro-F1 0.9448 reject(non-target events) 0.9895309882747069 reject(bg) 0.8978723404255319

| true \ pred | water | scream | glass_break | baby_cry | cry | other |
|---|---|---|---|---|---|---|
| water | 519 | 1 | 0 | 0 | 0 | 11 |
| scream | 0 | 146 | 0 | 0 | 0 | 1 |
| glass_break | 0 | 0 | 780 | 0 | 0 | 14 |
| baby_cry | 0 | 0 | 0 | 192 | 3 | 1 |
| cry | 3 | 4 | 0 | 1 | 396 | 7 |
| other | 62 | 11 | 43 | 16 | 37 | 3629 |

#### vs generalist E0m_v2 (remapped to own+other), noisy_snr20: mean delta own -0.0003

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.9332 | 0.9249 | -0.0083 |
| scream | 0.9577 | 0.9477 | -0.0099 |
| glass_break | 0.9533 | 0.9586 | +0.0053 |
| baby_cry | 0.9193 | 0.9333 | +0.0140 |
| cry | 0.9139 | 0.9112 | -0.0027 |
| other | 0.9678 | 0.9673 | -0.0005 |

### noisy_snr20: acc 0.9563 macro-F1 0.9351 reject(non-target events) 0.9878559463986599 reject(bg) 0.8829787234042553

| true \ pred | water | scream | glass_break | baby_cry | cry | other |
|---|---|---|---|---|---|---|
| water | 511 | 0 | 0 | 0 | 0 | 20 |
| scream | 0 | 145 | 0 | 0 | 0 | 2 |
| glass_break | 0 | 0 | 776 | 0 | 0 | 18 |
| baby_cry | 0 | 1 | 0 | 189 | 4 | 2 |
| cry | 1 | 2 | 0 | 5 | 395 | 8 |
| other | 62 | 11 | 49 | 15 | 57 | 3604 |

#### vs generalist E0m_v2 (remapped to own+other), noisy_snr15: mean delta own +0.0018

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.9201 | 0.9202 | +0.0001 |
| scream | 0.9484 | 0.9515 | +0.0031 |
| glass_break | 0.9458 | 0.9587 | +0.0130 |
| baby_cry | 0.9059 | 0.9077 | +0.0018 |
| cry | 0.9141 | 0.9053 | -0.0088 |
| other | 0.9645 | 0.9666 | +0.0022 |

### noisy_snr15: acc 0.9542 macro-F1 0.9287 reject(non-target events) 0.990787269681742 reject(bg) 0.8801418439716312

| true \ pred | water | scream | glass_break | baby_cry | cry | other |
|---|---|---|---|---|---|---|
| water | 513 | 1 | 0 | 0 | 0 | 17 |
| scream | 0 | 147 | 0 | 0 | 0 | 0 |
| glass_break | 1 | 0 | 767 | 0 | 0 | 26 |
| baby_cry | 0 | 0 | 0 | 182 | 9 | 5 |
| cry | 1 | 2 | 0 | 6 | 392 | 10 |
| other | 69 | 12 | 39 | 17 | 54 | 3607 |

#### vs generalist E0m_v2 (remapped to own+other), noisy_snr10: mean delta own +0.0074

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.9099 | 0.9160 | +0.0061 |
| scream | 0.9355 | 0.9325 | -0.0030 |
| glass_break | 0.9270 | 0.9392 | +0.0122 |
| baby_cry | 0.8878 | 0.9082 | +0.0204 |
| cry | 0.8958 | 0.8969 | +0.0011 |
| other | 0.9576 | 0.9621 | +0.0045 |

### noisy_snr10: acc 0.9473 macro-F1 0.9185 reject(non-target events) 0.9845058626465661 reject(bg) 0.8886524822695036

| true \ pred | water | scream | glass_break | baby_cry | cry | other |
|---|---|---|---|---|---|---|
| water | 507 | 1 | 0 | 0 | 0 | 23 |
| scream | 1 | 145 | 0 | 0 | 0 | 1 |
| glass_break | 2 | 1 | 741 | 0 | 0 | 50 |
| baby_cry | 0 | 0 | 0 | 183 | 9 | 4 |
| cry | 2 | 4 | 1 | 5 | 387 | 12 |
| other | 64 | 13 | 42 | 19 | 56 | 3604 |

