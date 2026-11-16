# btc-cent-forecast-01

Entry for make.fun bounty `btc-cent-forecast-01`: forecast the BTC/USDC close
240 minutes after each checkpoint from the 72 hours of 1-minute closes up to it.

## Model

Damped short-window momentum:

    guess = last + 0.25 * (last - last[-30]) / 30 * 240

i.e. the checkpoint close plus 25% of the drift measured over the last 30
minutes, extrapolated to the 240-minute horizon. The damping keeps the
extrapolation from overshooting on a pool price that mean-reverts after large
single trades.

## Practice validation

Scored on the kit's practice cases against the actual close at each case's
target (the next checkpoint's close; p05's target lies beyond the kit data and
is not scoreable locally):

| case | model err | persistence err |
|------|-----------|-----------------|
| p00  | 377.34    | 317.11          |
| p01  | 884.55    | 766.97          |
| p02  | 689.03    | 470.33          |
| p03  | 107.43    | 566.85          |
| p04  | 12.56     | 231.47          |
| mean | 414.18    | 470.55          |

Model mean 41,417.978 cents vs persistence baseline 47,054.662 cents on the
five scoreable practice cases (dollars shown in the table). The house baseline
over all six practice cases is 44,521.577 cents.

Selected by sweep over momentum windows (10-60 min), damping factors (0.1-0.5)
and linear-fit/EMA blends; the simple damped momentum won on held-out-style
practice error and is the least overfitted of the candidates.

## Run

    mkdir -p out && MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py

Python 3.13, standard library only, offline, deterministic.
