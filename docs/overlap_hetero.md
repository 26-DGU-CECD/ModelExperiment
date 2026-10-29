# overlap_hetero: error overlap (test, n=5877)

members: E0m_v2, E1k_v2, E2k_v2

## both-wrong counts (diagonal = wrong count)

| | E0m_v2 | E1k_v2 | E2k_v2 |
|---|---|---|---|
| E0m_v2 | 372 | 234 | 255 |
| E1k_v2 | 234 | 444 | 257 |
| E2k_v2 | 255 | 257 | 527 |

## error-set Jaccard

| | E0m_v2 | E1k_v2 | E2k_v2 |
|---|---|---|---|
| E0m_v2 | 1.000 | 0.402 | 0.396 |
| E1k_v2 | 0.402 | 1.000 | 0.360 |
| E2k_v2 | 0.396 | 0.360 | 1.000 |

all members wrong: 186 clips (3.165%). **oracle_any accuracy 0.9684, macro-F1 0.9598** (upper bound: pick any correct member). emergency group recall 0.9937.
