# LEADERBOARD

`python src/make_leaderboard.py`. test split. smoke_* excluded.

## A. generalist per-class F1

| experiment | model | alarm | fire_alarm | water | scream | glass_break | bicycle | gunshot | baby_cry | cry | car_horn | cat_meow | dog_bark | knock | background | macro-F1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## B. specialist vs generalist (same model)

| experiment | model | class | spec F1 | gen F1 (same model) | delta | reject non-target | reject bg |
|---|---|---|---|---|---|---|---|

## C. condition summary (macro-F1 desc)

| experiment | condition | model | macro-F1 | accuracy | emergency recall | bg FA rate | date |
|---|---|---|---|---|---|---|---|

## D. operating points

| experiment | rule | threshold | emergency recall | precision | FA/hour |
|---|---|---|---|---|---|
