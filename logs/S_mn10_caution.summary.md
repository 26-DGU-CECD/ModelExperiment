# S_mn10_caution

model=efficientat mode=specialist classes=5 train=48060 val=5762 batch=64 lr=2e-05 cap=3000 teacher=-

| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |
|---|---|---|---|---|---|---|---|
| init | - | - | 0.0878 | 0.0793 | - | - | |
| 0 | 0.7791 | 0.2413 | 0.9564 | 0.9689 | 1.99e-05 | 70 | * |
| 1 | 0.7671 | 0.2379 | 0.9584 | 0.9731 | 1.95e-05 | 55 | * |
| 2 | 0.7641 | 0.1911 | 0.9633 | 0.9767 | 1.89e-05 | 55 | * |
| 3 | 0.7601 | 0.1946 | 0.9638 | 0.9759 | 1.81e-05 | 55 | * |
| 4 | 0.7601 | 0.2196 | 0.9615 | 0.9755 | 1.71e-05 | 55 |  |
| 5 | 0.7603 | 0.2387 | 0.9651 | 0.9776 | 1.59e-05 | 55 | * |
| 6 | 0.7532 | 0.2370 | 0.9644 | 0.9776 | 1.45e-05 | 55 |  |
| 7 | 0.7540 | 0.2284 | 0.9634 | 0.9755 | 1.31e-05 | 55 |  |
| 8 | 0.7519 | 0.2066 | 0.9664 | 0.9773 | 1.16e-05 | 55 | * |
| 9 | 0.7522 | 0.2432 | 0.9659 | 0.9783 | 1.00e-05 | 55 |  |
| 10 | 0.7448 | 0.2180 | 0.9632 | 0.9757 | 8.44e-06 | 55 |  |
| 11 | 0.7456 | 0.2292 | 0.9653 | 0.9771 | 6.91e-06 | 55 |  |
| 12 | 0.7388 | 0.2150 | 0.9654 | 0.9780 | 5.46e-06 | 55 |  |
| 13 | 0.7353 | 0.2024 | 0.9669 | 0.9792 | 4.12e-06 | 55 | * |
| 14 | 0.7440 | 0.2057 | 0.9656 | 0.9785 | 2.93e-06 | 55 |  |
| 15 | 0.7399 | 0.2032 | 0.9659 | 0.9783 | 1.91e-06 | 55 |  |
| 16 | 0.7442 | 0.2029 | 0.9670 | 0.9793 | 1.09e-06 | 55 | * |
| 17 | 0.7397 | 0.2029 | 0.9680 | 0.9797 | 4.90e-07 | 54 | * |
| 18 | 0.7436 | 0.2056 | 0.9674 | 0.9795 | 1.23e-07 | 31 |  |
| 19 | 0.7406 | 0.2060 | 0.9672 | 0.9795 | 0.00e+00 | 33 |  |

best val macro-F1 = 0.9680

### specialisation gain (val per-class F1: init = warm start before fine-tune, best = selected epoch)

| class | init F1 | best F1 | delta |
|---|---|---|---|
| bicycle | 0.1098 | 0.9540 | +0.8442 |
| baby_cry | 0.0438 | 0.9872 | +0.9434 |
| gunshot | 0.0038 | 0.9538 | +0.9501 |
| glass_break | 0.2158 | 0.9580 | +0.7422 |
| other | 0.0658 | 0.9869 | +0.9211 |

mean delta over own classes = +0.8700


## evaluate (2026-10-30) best epoch 17

#### vs generalist E0m_v2 (remapped to own+other), val: mean delta own +0.0076

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| bicycle | 0.9408 | 0.9540 | +0.0132 |
| baby_cry | 0.9847 | 0.9872 | +0.0025 |
| gunshot | 0.9442 | 0.9538 | +0.0097 |
| glass_break | 0.9532 | 0.9580 | +0.0049 |
| other | 0.9849 | 0.9869 | +0.0021 |

### val: acc 0.9797 macro-F1 0.9633 reject(non-target events) 0.9988942130482861 reject(bg) 0.9492753623188406

| true \ pred | bicycle | baby_cry | gunshot | glass_break | other |
|---|---|---|---|---|---|
| bicycle | 280 | 0 | 0 | 2 | 8 |
| baby_cry | 0 | 193 | 0 | 0 | 0 |
| gunshot | 0 | 0 | 279 | 2 | 1 |
| glass_break | 0 | 0 | 3 | 742 | 21 |
| other | 17 | 5 | 21 | 37 | 4151 |

#### vs generalist E0m_v2 (remapped to own+other), test: mean delta own +0.0029

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| bicycle | 0.9182 | 0.9234 | +0.0051 |
| baby_cry | 0.9412 | 0.9458 | +0.0046 |
| gunshot | 0.9171 | 0.9159 | -0.0012 |
| glass_break | 0.9616 | 0.9646 | +0.0030 |
| other | 0.9812 | 0.9816 | +0.0004 |

### test: acc 0.9719 macro-F1 0.9374 reject(non-target events) 0.9969335604770017 reject(bg) 0.9134751773049645

| true \ pred | bicycle | baby_cry | gunshot | glass_break | other |
|---|---|---|---|---|---|
| bicycle | 247 | 0 | 0 | 0 | 0 |
| baby_cry | 0 | 192 | 0 | 0 | 4 |
| gunshot | 0 | 0 | 283 | 4 | 8 |
| glass_break | 1 | 0 | 2 | 776 | 15 |
| other | 40 | 18 | 38 | 35 | 4214 |

#### vs generalist E0m_v2 (remapped to own+other), noisy_snr20: mean delta own +0.0092

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| bicycle | 0.9114 | 0.9111 | -0.0003 |
| baby_cry | 0.9193 | 0.9377 | +0.0183 |
| gunshot | 0.9006 | 0.9118 | +0.0111 |
| glass_break | 0.9533 | 0.9607 | +0.0075 |
| other | 0.9788 | 0.9805 | +0.0017 |

### noisy_snr20: acc 0.9695 macro-F1 0.9303 reject(non-target events) 0.9952299829642248 reject(bg) 0.9170212765957447

| true \ pred | bicycle | baby_cry | gunshot | glass_break | other |
|---|---|---|---|---|---|
| bicycle | 246 | 0 | 0 | 0 | 1 |
| baby_cry | 0 | 188 | 0 | 0 | 8 |
| gunshot | 0 | 0 | 279 | 5 | 11 |
| glass_break | 1 | 0 | 5 | 771 | 17 |
| other | 46 | 17 | 33 | 35 | 4214 |

#### vs generalist E0m_v2 (remapped to own+other), noisy_snr15: mean delta own +0.0092

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| bicycle | 0.8909 | 0.8934 | +0.0025 |
| baby_cry | 0.9059 | 0.9141 | +0.0082 |
| gunshot | 0.8956 | 0.9123 | +0.0168 |
| glass_break | 0.9458 | 0.9549 | +0.0092 |
| other | 0.9762 | 0.9774 | +0.0012 |

### noisy_snr15: acc 0.9649 macro-F1 0.9187 reject(non-target events) 0.9928449744463373 reject(bg) 0.9141843971631206

| true \ pred | bicycle | baby_cry | gunshot | glass_break | other |
|---|---|---|---|---|---|
| bicycle | 243 | 0 | 0 | 0 | 4 |
| baby_cry | 0 | 181 | 0 | 0 | 15 |
| gunshot | 0 | 0 | 281 | 2 | 12 |
| glass_break | 4 | 0 | 6 | 763 | 21 |
| other | 50 | 19 | 34 | 39 | 4203 |

#### vs generalist E0m_v2 (remapped to own+other), noisy_snr10: mean delta own +0.0211

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| bicycle | 0.8682 | 0.8869 | +0.0187 |
| baby_cry | 0.8878 | 0.9100 | +0.0222 |
| gunshot | 0.8616 | 0.8882 | +0.0266 |
| glass_break | 0.9270 | 0.9438 | +0.0169 |
| other | 0.9719 | 0.9764 | +0.0045 |

### noisy_snr10: acc 0.9609 macro-F1 0.9072 reject(non-target events) 0.9901192504258943 reject(bg) 0.9148936170212766

| true \ pred | bicycle | baby_cry | gunshot | glass_break | other |
|---|---|---|---|---|---|
| bicycle | 247 | 0 | 0 | 0 | 0 |
| baby_cry | 0 | 182 | 0 | 0 | 14 |
| gunshot | 1 | 0 | 274 | 6 | 14 |
| glass_break | 6 | 0 | 14 | 748 | 26 |
| other | 56 | 22 | 34 | 37 | 4196 |

