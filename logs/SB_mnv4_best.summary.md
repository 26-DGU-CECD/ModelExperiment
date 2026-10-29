# SB_mnv4_best

model=mnv4 mode=specialist classes=5 train=48060 val=5762 batch=64 lr=2e-05 cap=3000 teacher=-

| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |
|---|---|---|---|---|---|---|---|
| init | - | - | 0.0641 | 0.0783 | - | - | |
| 0 | 0.7066 | 0.2161 | 0.9449 | 0.9807 | 1.99e-05 | 41 | * |
| 1 | 0.6509 | 0.2094 | 0.9475 | 0.9816 | 1.95e-05 | 25 | * |
| 2 | 0.6464 | 0.2140 | 0.9391 | 0.9826 | 1.89e-05 | 24 |  |
| 3 | 0.6413 | 0.2134 | 0.9474 | 0.9832 | 1.81e-05 | 23 |  |
| 4 | 0.6434 | 0.2087 | 0.9393 | 0.9806 | 1.71e-05 | 23 |  |
| 5 | 0.6405 | 0.2063 | 0.9502 | 0.9858 | 1.59e-05 | 23 | * |
| 6 | 0.6380 | 0.1940 | 0.9442 | 0.9821 | 1.45e-05 | 23 |  |
| 7 | 0.6367 | 0.2098 | 0.9456 | 0.9816 | 1.31e-05 | 22 |  |
| 8 | 0.6385 | 0.2083 | 0.9452 | 0.9828 | 1.16e-05 | 23 |  |
| 9 | 0.6350 | 0.1986 | 0.9451 | 0.9830 | 1.00e-05 | 22 |  |
| 10 | 0.6314 | 0.1952 | 0.9485 | 0.9840 | 8.44e-06 | 24 |  |
| 11 | 0.6342 | 0.2056 | 0.9393 | 0.9804 | 6.91e-06 | 23 |  |
| 12 | 0.6245 | 0.2040 | 0.9474 | 0.9835 | 5.46e-06 | 23 |  |
| 13 | 0.6245 | 0.1993 | 0.9429 | 0.9821 | 4.12e-06 | 22 |  |

best val macro-F1 = 0.9502

### specialisation gain (val per-class F1: init = warm start before fine-tune, best = selected epoch)

| class | init F1 | best F1 | delta |
|---|---|---|---|
| fire_alarm | 0.0332 | 0.9960 | +0.9628 |
| bicycle | 0.2113 | 0.9466 | +0.7353 |
| car_horn | 0.0027 | 0.8991 | +0.8964 |
| cat_meow | 0.0175 | 0.9182 | +0.9006 |
| other | 0.0556 | 0.9910 | +0.9354 |

mean delta over own classes = +0.8738


## evaluate (2026-10-30) best epoch 5

#### vs generalist E2k_v2 (remapped to own+other), val: mean delta own -0.0080

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| fire_alarm | 0.9874 | 0.9960 | +0.0086 |
| bicycle | 0.9540 | 0.9466 | -0.0074 |
| car_horn | 0.9286 | 0.8991 | -0.0295 |
| cat_meow | 0.9221 | 0.9182 | -0.0039 |
| other | 0.9903 | 0.9910 | +0.0007 |

### val: acc 0.9858 macro-F1 0.9400 reject(non-target events) 0.998630605956864 reject(bg) 0.9795783926218709

| true \ pred | fire_alarm | bicycle | car_horn | cat_meow | other |
|---|---|---|---|---|---|
| fire_alarm | 750 | 0 | 0 | 0 | 2 |
| bicycle | 0 | 275 | 0 | 0 | 15 |
| car_horn | 0 | 2 | 49 | 0 | 8 |
| cat_meow | 0 | 0 | 0 | 202 | 20 |
| other | 4 | 14 | 1 | 16 | 4404 |

#### vs generalist E2k_v2 (remapped to own+other), test: mean delta own -0.0463

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| fire_alarm | 0.9885 | 0.9855 | -0.0031 |
| bicycle | 0.9119 | 0.9037 | -0.0081 |
| car_horn | 0.7391 | 0.6000 | -0.1391 |
| cat_meow | 0.8814 | 0.8466 | -0.0347 |
| other | 0.9872 | 0.9849 | -0.0023 |

### test: acc 0.9763 macro-F1 0.8340 reject(non-target events) 0.9987389659520807 reject(bg) 0.9765957446808511

| true \ pred | fire_alarm | bicycle | car_horn | cat_meow | other |
|---|---|---|---|---|---|
| fire_alarm | 813 | 0 | 0 | 0 | 24 |
| bicycle | 0 | 230 | 0 | 0 | 17 |
| car_horn | 0 | 0 | 12 | 0 | 14 |
| cat_meow | 0 | 0 | 0 | 138 | 47 |
| other | 0 | 32 | 2 | 3 | 4545 |

#### vs generalist E2k_v2 (remapped to own+other), noisy_snr20: mean delta own -0.0173

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| fire_alarm | 0.6672 | 0.6656 | -0.0016 |
| bicycle | 0.9067 | 0.9074 | +0.0007 |
| car_horn | 0.6667 | 0.6512 | -0.0155 |
| cat_meow | 0.8701 | 0.8173 | -0.0527 |
| other | 0.9449 | 0.9441 | -0.0009 |

### noisy_snr20: acc 0.9085 macro-F1 0.7604 reject(non-target events) 0.8872767857142857 reject(bg) 0.9645390070921985

| true \ pred | fire_alarm | bicycle | car_horn | cat_meow | other |
|---|---|---|---|---|---|
| fire_alarm | 413 | 0 | 0 | 0 | 12 |
| bicycle | 0 | 240 | 0 | 0 | 7 |
| car_horn | 0 | 0 | 14 | 0 | 12 |
| cat_meow | 0 | 0 | 0 | 132 | 53 |
| other | 403 | 42 | 3 | 6 | 4540 |

#### vs generalist E2k_v2 (remapped to own+other), noisy_snr15: mean delta own -0.0197

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| fire_alarm | 0.6688 | 0.6661 | -0.0027 |
| bicycle | 0.8974 | 0.9013 | +0.0039 |
| car_horn | 0.6800 | 0.6500 | -0.0300 |
| cat_meow | 0.8845 | 0.8344 | -0.0502 |
| other | 0.9451 | 0.9441 | -0.0010 |

### noisy_snr15: acc 0.9086 macro-F1 0.7629 reject(non-target events) 0.8864397321428571 reject(bg) 0.9624113475177305

| true \ pred | fire_alarm | bicycle | car_horn | cat_meow | other |
|---|---|---|---|---|---|
| fire_alarm | 415 | 0 | 0 | 0 | 10 |
| bicycle | 0 | 242 | 0 | 0 | 5 |
| car_horn | 0 | 0 | 13 | 0 | 13 |
| cat_meow | 0 | 0 | 0 | 136 | 49 |
| other | 406 | 48 | 1 | 5 | 4534 |

#### vs generalist E2k_v2 (remapped to own+other), noisy_snr10: mean delta own -0.0327

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| fire_alarm | 0.6677 | 0.6688 | +0.0011 |
| bicycle | 0.8710 | 0.8771 | +0.0061 |
| car_horn | 0.6538 | 0.5854 | -0.0685 |
| cat_meow | 0.8266 | 0.7573 | -0.0693 |
| other | 0.9422 | 0.9411 | -0.0012 |

### noisy_snr10: acc 0.9034 macro-F1 0.7221 reject(non-target events) 0.8861607142857143 reject(bg) 0.9581560283687943

| true \ pred | fire_alarm | bicycle | car_horn | cat_meow | other |
|---|---|---|---|---|---|
| fire_alarm | 414 | 0 | 0 | 0 | 11 |
| bicycle | 0 | 239 | 0 | 0 | 8 |
| car_horn | 0 | 0 | 12 | 0 | 14 |
| cat_meow | 0 | 1 | 0 | 117 | 67 |
| other | 399 | 58 | 3 | 7 | 4527 |

