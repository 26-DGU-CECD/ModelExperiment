# LEADERBOARD

`python src/make_leaderboard.py`. test split. smoke_* excluded.

## A. generalist per-class F1

| experiment | model | alarm | fire_alarm | water | scream | glass_break | bicycle | gunshot | baby_cry | cry | car_horn | cat_meow | dog_bark | knock | background | macro-F1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E0_efficientat_generalist | efficientat | 0.7523 | 0.6561 | 0.9274 | 0.9639 | 0.9605 | 0.9283 | 0.9357 | 0.9505 | 0.9438 | 0.5952 | 0.9418 | 0.9814 | 0.9538 | 0.8907 | 0.8844 |

## B. specialist vs generalist (same model)

| experiment | model | class | spec F1 | gen F1 (same model) | delta | reject non-target | reject bg |
|---|---|---|---|---|---|---|---|

## C. condition summary (macro-F1 desc)

| experiment | condition | model | macro-F1 | accuracy | emergency recall | bg FA rate | date |
|---|---|---|---|---|---|---|---|
| E0_efficientat_generalist | generalist | efficientat | 0.8844 | 0.8717 | 0.8545 | 0.1851 | 2026-10-29 |

## D. operating points

| experiment | rule | threshold | emergency recall | precision | FA/hour |
|---|---|---|---|---|---|
