# A2_efficientat_random

model=efficientat mode=specialist classes=6 train=48060 val=5762 batch=64 lr=2e-05 cap=3000 teacher=-

| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |
|---|---|---|---|---|---|---|---|
| init | - | - | 0.0885 | 0.1925 | - | - | |
| 0 | 0.8041 | 0.1932 | 0.9263 | 0.9748 | 1.99e-05 | 71 | * |
| 1 | 0.7837 | 0.2423 | 0.9208 | 0.9733 | 1.95e-05 | 55 |  |
| 2 | 0.7832 | 0.2357 | 0.9276 | 0.9747 | 1.89e-05 | 55 | * |
| 3 | 0.7800 | 0.2386 | 0.9196 | 0.9769 | 1.81e-05 | 55 |  |
| 4 | 0.7833 | 0.2492 | 0.9229 | 0.9755 | 1.71e-05 | 55 |  |
| 5 | 0.7782 | 0.2759 | 0.9297 | 0.9780 | 1.59e-05 | 40 | * |
| 6 | 0.7749 | 0.2307 | 0.9260 | 0.9778 | 1.45e-05 | 30 |  |
| 7 | 0.7734 | 0.2629 | 0.9271 | 0.9781 | 1.31e-05 | 32 |  |
| 8 | 0.7687 | 0.2258 | 0.9232 | 0.9747 | 1.16e-05 | 29 |  |
| 9 | 0.7715 | 0.2193 | 0.9273 | 0.9787 | 1.00e-05 | 28 |  |
| 10 | 0.7625 | 0.2464 | 0.9186 | 0.9724 | 8.44e-06 | 28 |  |
| 11 | 0.7630 | 0.2266 | 0.9258 | 0.9787 | 6.91e-06 | 28 |  |
| 12 | 0.7547 | 0.2412 | 0.9247 | 0.9759 | 5.46e-06 | 28 |  |
| 13 | 0.7510 | 0.2066 | 0.9251 | 0.9750 | 4.12e-06 | 28 |  |

best val macro-F1 = 0.9297

### specialisation gain (val per-class F1: init = warm start before fine-tune, best = selected epoch)

| class | init F1 | best F1 | delta |
|---|---|---|---|
| alarm | 0.0678 | 0.9488 | +0.8810 |
| knock | 0.0000 | 0.8571 | +0.8571 |
| baby_cry | 0.0727 | 0.9845 | +0.9118 |
| cat_meow | 0.0044 | 0.9106 | +0.9063 |
| car_horn | 0.0593 | 0.8906 | +0.8313 |
| other | 0.3266 | 0.9865 | +0.6600 |

mean delta over own classes = +0.8775


## evaluate (2026-10-30) best epoch 5

#### vs generalist E0m_v2 (remapped to own+other), val: mean delta own +0.0053

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.9419 | 0.9488 | +0.0069 |
| knock | 0.8308 | 0.8571 | +0.0264 |
| baby_cry | 0.9847 | 0.9845 | -0.0002 |
| cat_meow | 0.9158 | 0.9106 | -0.0051 |
| car_horn | 0.8923 | 0.8906 | -0.0017 |
| other | 0.9861 | 0.9865 | +0.0004 |

### val: acc 0.9780 macro-F1 0.9183 reject(non-target events) 0.9880277252678009 reject(bg) 0.9762845849802372

| true \ pred | alarm | knock | baby_cry | cat_meow | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 528 | 0 | 0 | 0 | 0 | 41 |
| knock | 0 | 27 | 0 | 0 | 0 | 0 |
| baby_cry | 0 | 0 | 191 | 0 | 0 | 2 |
| cat_meow | 0 | 1 | 0 | 214 | 0 | 7 |
| car_horn | 0 | 0 | 0 | 0 | 57 | 2 |
| other | 16 | 8 | 4 | 34 | 12 | 4618 |

#### vs generalist E0m_v2 (remapped to own+other), test: mean delta own +0.0068

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.9702 | 0.9687 | -0.0015 |
| knock | 0.8857 | 0.9394 | +0.0537 |
| baby_cry | 0.9412 | 0.9545 | +0.0134 |
| cat_meow | 0.9293 | 0.9365 | +0.0072 |
| car_horn | 0.6410 | 0.6024 | -0.0386 |
| other | 0.9935 | 0.9936 | +0.0001 |

### test: acc 0.9845 macro-F1 0.8803 reject(non-target events) 0.9994017349685911 reject(bg) 0.973758865248227

| true \ pred | alarm | knock | baby_cry | cat_meow | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 650 | 0 | 0 | 1 | 24 | 11 |
| knock | 0 | 31 | 0 | 0 | 0 | 0 |
| baby_cry | 0 | 0 | 189 | 0 | 0 | 7 |
| cat_meow | 0 | 1 | 2 | 177 | 1 | 4 |
| car_horn | 0 | 0 | 0 | 1 | 25 | 0 |
| other | 6 | 3 | 9 | 14 | 7 | 4714 |

#### vs generalist E0m_v2 (remapped to own+other), noisy_snr20: mean delta own +0.0258

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.7370 | 0.7386 | +0.0016 |
| knock | 0.8158 | 0.9254 | +0.1096 |
| baby_cry | 0.9193 | 0.9330 | +0.0137 |
| cat_meow | 0.9030 | 0.8997 | -0.0033 |
| car_horn | 0.6000 | 0.6076 | +0.0076 |
| other | 0.9457 | 0.9465 | +0.0008 |

### noisy_snr20: acc 0.9112 macro-F1 0.8209 reject(non-target events) 0.9986352780620948 reject(bg) 0.9780141843971631

| true \ pred | alarm | knock | baby_cry | cat_meow | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 647 | 0 | 0 | 0 | 25 | 426 |
| knock | 0 | 31 | 0 | 0 | 0 | 0 |
| baby_cry | 0 | 0 | 181 | 0 | 0 | 15 |
| cat_meow | 0 | 2 | 6 | 166 | 1 | 10 |
| car_horn | 0 | 0 | 0 | 1 | 24 | 1 |
| other | 7 | 3 | 5 | 17 | 3 | 4306 |

#### vs generalist E0m_v2 (remapped to own+other), noisy_snr15: mean delta own +0.0287

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.7309 | 0.7317 | +0.0009 |
| knock | 0.7294 | 0.8611 | +0.1317 |
| baby_cry | 0.9059 | 0.9138 | +0.0079 |
| cat_meow | 0.9121 | 0.9218 | +0.0097 |
| car_horn | 0.5714 | 0.5647 | -0.0067 |
| other | 0.9434 | 0.9447 | +0.0012 |

### noisy_snr15: acc 0.9079 macro-F1 0.7986 reject(non-target events) 0.9989764585465711 reject(bg) 0.9687943262411347

| true \ pred | alarm | knock | baby_cry | cat_meow | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 641 | 0 | 0 | 0 | 27 | 430 |
| knock | 0 | 31 | 0 | 0 | 0 | 0 |
| baby_cry | 1 | 0 | 175 | 0 | 0 | 20 |
| cat_meow | 0 | 0 | 7 | 171 | 2 | 5 |
| car_horn | 0 | 0 | 0 | 1 | 24 | 1 |
| other | 12 | 10 | 5 | 14 | 6 | 4294 |

#### vs generalist E0m_v2 (remapped to own+other), noisy_snr10: mean delta own +0.0257

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.7272 | 0.7274 | +0.0002 |
| knock | 0.6517 | 0.7733 | +0.1216 |
| baby_cry | 0.8878 | 0.8794 | -0.0084 |
| cat_meow | 0.8747 | 0.9016 | +0.0270 |
| car_horn | 0.5393 | 0.5275 | -0.0119 |
| other | 0.9406 | 0.9421 | +0.0016 |

### noisy_snr10: acc 0.9025 macro-F1 0.7618 reject(non-target events) 0.9972705561241897 reject(bg) 0.9645390070921985

| true \ pred | alarm | knock | baby_cry | cat_meow | car_horn | other |
|---|---|---|---|---|---|---|
| alarm | 639 | 0 | 0 | 0 | 34 | 425 |
| knock | 0 | 29 | 0 | 0 | 0 | 2 |
| baby_cry | 0 | 0 | 164 | 2 | 0 | 30 |
| cat_meow | 1 | 1 | 6 | 165 | 3 | 9 |
| car_horn | 0 | 0 | 0 | 0 | 24 | 2 |
| other | 19 | 14 | 7 | 14 | 4 | 4283 |

