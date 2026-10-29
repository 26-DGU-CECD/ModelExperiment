# H_mn04_daily

model=efficientat mode=specialist classes=5 train=48060 val=5762 batch=64 lr=2e-05 cap=3000 teacher=-

| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |
|---|---|---|---|---|---|---|---|
| init | - | - | 0.1108 | 0.2312 | - | - | |
| 0 | 0.7678 | 0.2119 | 0.8933 | 0.9684 | 1.99e-05 | 67 | * |
| 1 | 0.7511 | 0.2315 | 0.8937 | 0.9653 | 1.95e-05 | 49 | * |
| 2 | 0.7487 | 0.2542 | 0.8941 | 0.9660 | 1.89e-05 | 50 | * |
| 3 | 0.7466 | 0.2276 | 0.8927 | 0.9625 | 1.81e-05 | 48 |  |
| 4 | 0.7477 | 0.2258 | 0.8908 | 0.9682 | 1.71e-05 | 51 |  |
| 5 | 0.7465 | 0.2428 | 0.8912 | 0.9674 | 1.59e-05 | 51 |  |
| 6 | 0.7427 | 0.2191 | 0.8963 | 0.9682 | 1.45e-05 | 50 | * |
| 7 | 0.7414 | 0.2500 | 0.8941 | 0.9688 | 1.31e-05 | 48 |  |
| 8 | 0.7410 | 0.2482 | 0.8910 | 0.9669 | 1.16e-05 | 50 |  |
| 9 | 0.7422 | 0.2515 | 0.8894 | 0.9660 | 1.00e-05 | 48 |  |
| 10 | 0.7398 | 0.2401 | 0.8930 | 0.9670 | 8.44e-06 | 47 |  |
| 11 | 0.7387 | 0.2349 | 0.8865 | 0.9679 | 6.91e-06 | 47 |  |
| 12 | 0.7319 | 0.2433 | 0.8938 | 0.9682 | 5.46e-06 | 48 |  |
| 13 | 0.7310 | 0.2379 | 0.8927 | 0.9675 | 4.12e-06 | 47 |  |
| 14 | 0.7339 | 0.2367 | 0.8864 | 0.9663 | 2.93e-06 | 49 |  |

best val macro-F1 = 0.8963

### specialisation gain (val per-class F1: init = warm start before fine-tune, best = selected epoch)

| class | init F1 | best F1 | delta |
|---|---|---|---|
| water | 0.0000 | 0.8657 | +0.8657 |
| knock | 0.0000 | 0.8710 | +0.8710 |
| dog_bark | 0.1242 | 0.8571 | +0.7329 |
| cat_meow | 0.0328 | 0.9055 | +0.8727 |
| other | 0.3969 | 0.9824 | +0.5855 |

mean delta over own classes = +0.8356


## evaluate (2026-10-30) best epoch 6

#### vs generalist G_mn04 (remapped to own+other), val: mean delta own +0.0193

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.8221 | 0.8657 | +0.0436 |
| knock | 0.8438 | 0.8710 | +0.0272 |
| dog_bark | 0.8606 | 0.8571 | -0.0035 |
| cat_meow | 0.8957 | 0.9055 | +0.0098 |
| other | 0.9756 | 0.9824 | +0.0068 |

### val: acc 0.9682 macro-F1 0.8748 reject(non-target events) 0.9977044476327116 reject(bg) 0.9393939393939394

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 374 | 0 | 1 | 0 | 47 |
| knock | 0 | 27 | 0 | 0 | 0 |
| dog_bark | 1 | 0 | 69 | 4 | 14 |
| cat_meow | 0 | 1 | 0 | 206 | 15 |
| other | 67 | 7 | 3 | 23 | 4903 |

#### vs generalist G_mn04 (remapped to own+other), test: mean delta own +0.0155

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.8667 | 0.8920 | +0.0253 |
| knock | 0.9254 | 0.9394 | +0.0140 |
| dog_bark | 0.9512 | 0.9689 | +0.0177 |
| cat_meow | 0.8822 | 0.8870 | +0.0048 |
| other | 0.9784 | 0.9837 | +0.0052 |

### test: acc 0.9719 macro-F1 0.9218 reject(non-target events) 0.9986259961527892 reject(bg) 0.9453900709219858

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 479 | 0 | 0 | 0 | 52 |
| knock | 0 | 31 | 0 | 0 | 0 |
| dog_bark | 0 | 0 | 78 | 0 | 3 |
| cat_meow | 0 | 0 | 0 | 157 | 28 |
| other | 64 | 4 | 2 | 12 | 4967 |

#### vs generalist G_mn04 (remapped to own+other), noisy_snr20: mean delta own +0.0368

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.8684 | 0.8831 | +0.0147 |
| knock | 0.8267 | 0.8986 | +0.0719 |
| dog_bark | 0.9277 | 0.9686 | +0.0408 |
| cat_meow | 0.8540 | 0.8736 | +0.0196 |
| other | 0.9776 | 0.9826 | +0.0050 |

### noisy_snr20: acc 0.9695 macro-F1 0.9059 reject(non-target events) 0.9975267930750206 reject(bg) 0.9446808510638298

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 476 | 0 | 0 | 0 | 55 |
| knock | 0 | 31 | 0 | 0 | 0 |
| dog_bark | 0 | 0 | 77 | 1 | 3 |
| cat_meow | 1 | 1 | 0 | 152 | 31 |
| other | 70 | 6 | 1 | 10 | 4962 |

#### vs generalist G_mn04 (remapped to own+other), noisy_snr15: mean delta own +0.0425

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.8543 | 0.8752 | +0.0209 |
| knock | 0.7848 | 0.8986 | +0.1137 |
| dog_bark | 0.9341 | 0.9494 | +0.0152 |
| cat_meow | 0.8486 | 0.8686 | +0.0199 |
| other | 0.9743 | 0.9813 | +0.0070 |

### noisy_snr15: acc 0.9673 macro-F1 0.8979 reject(non-target events) 0.9969771915361363 reject(bg) 0.9425531914893617

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 470 | 0 | 0 | 0 | 61 |
| knock | 0 | 31 | 0 | 0 | 0 |
| dog_bark | 0 | 0 | 75 | 1 | 5 |
| cat_meow | 0 | 0 | 2 | 152 | 31 |
| other | 73 | 7 | 0 | 12 | 4957 |

#### vs generalist G_mn04 (remapped to own+other), noisy_snr10: mean delta own +0.0553

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.8285 | 0.8762 | +0.0477 |
| knock | 0.5977 | 0.7123 | +0.1146 |
| dog_bark | 0.8824 | 0.9221 | +0.0397 |
| cat_meow | 0.8209 | 0.8402 | +0.0193 |
| other | 0.9687 | 0.9791 | +0.0104 |

### noisy_snr10: acc 0.9632 macro-F1 0.8377 reject(non-target events) 0.9967023907666942 reject(bg) 0.9368794326241134

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 474 | 0 | 1 | 0 | 56 |
| knock | 3 | 26 | 0 | 0 | 2 |
| dog_bark | 0 | 0 | 71 | 1 | 9 |
| cat_meow | 0 | 0 | 0 | 142 | 43 |
| other | 74 | 16 | 1 | 10 | 4948 |

