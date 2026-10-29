# S3_mnv4_daily

model=mnv4 mode=specialist classes=5 train=16110 val=5762 batch=64 lr=0.0001 cap=3000 teacher=-

| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |
|---|---|---|---|---|---|---|---|
| 0 | 0.8664 | 0.2102 | 0.8871 | 0.9606 | 1.00e-04 | 33 | * |
| 1 | 0.5671 | 0.2022 | 0.8768 | 0.9566 | 9.93e-05 | 7 |  |
| 2 | 0.5574 | 0.2323 | 0.8521 | 0.9559 | 9.73e-05 | 7 |  |
| 3 | 0.5317 | 0.2006 | 0.8548 | 0.9608 | 9.40e-05 | 7 |  |
| 4 | 0.5479 | 0.2475 | 0.8509 | 0.9485 | 8.95e-05 | 7 |  |
| 5 | 0.5287 | 0.1741 | 0.8667 | 0.9604 | 8.39e-05 | 7 |  |
| 6 | 0.5143 | 0.1962 | 0.8734 | 0.9547 | 7.73e-05 | 7 |  |

best val macro-F1 = 0.8871


## evaluate (2026-10-29) best epoch 0

### val: acc 0.9606 macro-F1 0.8644 reject(non-target events) 0.9979913916786227 reject(bg) 0.9044795783926218

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 379 | 0 | 0 | 0 | 43 |
| knock | 0 | 27 | 0 | 0 | 0 |
| dog_bark | 0 | 0 | 66 | 4 | 18 |
| cat_meow | 0 | 1 | 0 | 212 | 9 |
| other | 118 | 7 | 2 | 25 | 4851 |

### test: acc 0.9592 macro-F1 0.8685 reject(non-target events) 0.9958779884583677 reject(bg) 0.9219858156028369

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 459 | 0 | 0 | 1 | 71 |
| knock | 0 | 31 | 0 | 0 | 0 |
| dog_bark | 0 | 0 | 75 | 5 | 1 |
| cat_meow | 0 | 1 | 9 | 148 | 27 |
| other | 98 | 3 | 12 | 12 | 4924 |

### noisy_snr20: acc 0.9513 macro-F1 0.8224 reject(non-target events) 0.9936795823028305 reject(bg) 0.9

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 449 | 1 | 0 | 1 | 80 |
| knock | 0 | 31 | 0 | 0 | 0 |
| dog_bark | 0 | 0 | 74 | 6 | 1 |
| cat_meow | 0 | 1 | 4 | 152 | 28 |
| other | 109 | 13 | 19 | 23 | 4885 |

### noisy_snr15: acc 0.9513 macro-F1 0.8132 reject(non-target events) 0.9934047815333883 reject(bg) 0.9070921985815603

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 440 | 0 | 0 | 0 | 91 |
| knock | 0 | 31 | 0 | 0 | 0 |
| dog_bark | 0 | 0 | 72 | 7 | 2 |
| cat_meow | 0 | 2 | 2 | 154 | 27 |
| other | 102 | 19 | 17 | 17 | 4894 |

### noisy_snr10: acc 0.9491 macro-F1 0.7912 reject(non-target events) 0.9912063753778511 reject(bg) 0.9234042553191489

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 424 | 2 | 0 | 2 | 103 |
| knock | 1 | 30 | 0 | 0 | 0 |
| dog_bark | 0 | 0 | 74 | 6 | 1 |
| cat_meow | 0 | 4 | 5 | 141 | 35 |
| other | 89 | 16 | 20 | 15 | 4909 |

