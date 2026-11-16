#!/usr/bin/env python3
"""btc-cent-forecast-01 entry: damped short-window momentum forecast.

Reads every <id>.in in the input directory (the grader supplies one case per
run), forecasts the BTC/USDC close 240 minutes after each checkpoint, and
writes {"forecasts":[{"case":<id>,"price":<number>}]} to <id>.out.

Model: the checkpoint close plus 25% of the drift seen over the last 30
minutes, extrapolated to the 240-minute horizon:

    guess = last + 0.25 * (last - last[-30]) / 30 * 240

A pure extrapolation overshoots on a pool price that mean-reverts after
large trades, so the drift is damped; the damping was chosen so the model
beats the persistence baseline on the kit's practice cases. Deterministic,
stdlib only, no network.
"""

import json
import os
import re

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

MIN_PRICE = 0.00001
MAX_PRICE = 9_999_999.99999

HORIZON = 240          # minutes ahead to forecast
MOMENTUM_WINDOW = 30   # minutes of recent drift to measure
DRIFT_DAMPING = 0.25   # fraction of the extrapolated drift to keep


def clamp_price(x):
    """Keep the guess on the grid's 5 decimals and inside (0, 10,000,000)."""
    return round(min(MAX_PRICE, max(MIN_PRICE, x)) * 1e5) / 1e5


def forecast(prices):
    if not prices:
        raise ValueError("market has no prices")
    last = prices[-1]
    k = min(MOMENTUM_WINDOW, len(prices) - 1)
    if k <= 0:
        return clamp_price(last)
    drift_per_min = (last - prices[-1 - k]) / k
    return clamp_price(last + DRIFT_DAMPING * drift_per_min * HORIZON)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    names = sorted(n for n in os.listdir(INPUT_DIR) if n.endswith(".in"))
    for name in names:
        case_id = re.sub(r"\.in$", "", name)
        with open(os.path.join(INPUT_DIR, name), "r", encoding="utf-8") as f:
            case = json.load(f)
        markets = case["markets"]
        if len(markets) != 1:
            raise ValueError(f"{name}: expected exactly one market")
        price = forecast(markets[0]["prices"])
        out = {"forecasts": [{"case": case_id, "price": price}]}
        with open(os.path.join(OUTPUT_DIR, case_id + ".out"), "w", encoding="utf-8") as f:
            f.write(json.dumps(out) + "\n")


if __name__ == "__main__":
    main()
