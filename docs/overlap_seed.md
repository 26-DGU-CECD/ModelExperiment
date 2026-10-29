# overlap_seed: error overlap (test, n=5877)

members: E0m_v2, G_mn10_seed1, G_mn10_seed2

## both-wrong counts (diagonal = wrong count)

| | E0m_v2 | G_mn10_seed1 | G_mn10_seed2 |
|---|---|---|---|
| E0m_v2 | 372 | 302 | 323 |
| G_mn10_seed1 | 302 | 360 | 319 |
| G_mn10_seed2 | 323 | 319 | 404 |

## error-set Jaccard

| | E0m_v2 | G_mn10_seed1 | G_mn10_seed2 |
|---|---|---|---|
| E0m_v2 | 1.000 | 0.702 | 0.713 |
| G_mn10_seed1 | 0.702 | 1.000 | 0.717 |
| G_mn10_seed2 | 0.713 | 0.717 | 1.000 |

all members wrong: 288 clips (4.900%). **oracle_any accuracy 0.9510, macro-F1 0.9324** (upper bound: pick any correct member). emergency group recall 0.9909.
