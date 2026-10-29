# overlap_effat: error overlap (test, n=5877)

members: E0m_v2, G_dymn10, G_mn04

## both-wrong counts (diagonal = wrong count)

| | E0m_v2 | G_dymn10 | G_mn04 |
|---|---|---|---|
| E0m_v2 | 372 | 307 | 303 |
| G_dymn10 | 307 | 507 | 406 |
| G_mn04 | 303 | 406 | 603 |

## error-set Jaccard

| | E0m_v2 | G_dymn10 | G_mn04 |
|---|---|---|---|
| E0m_v2 | 1.000 | 0.537 | 0.451 |
| G_dymn10 | 0.537 | 1.000 | 0.577 |
| G_mn04 | 0.451 | 0.577 | 1.000 |

all members wrong: 280 clips (4.764%). **oracle_any accuracy 0.9524, macro-F1 0.9371** (upper bound: pick any correct member). emergency group recall 0.9941.
