"""Variant C (simpler): same semantics as baseline, tighter code."""

import sys


def parse_liquidity(filepath):
    try:
        with open(filepath, "r") as f:
            bids = [float(ln.split('"')[3]) for ln in f if "bid" in ln]
    except Exception as e:
        print(f"SIGNAL: ERROR_{e}")
        return
    if not bids:
        print("SIGNAL: NULL_LIQUIDITY")
        return
    print(f"SIGNAL: STRIKE_READY | AVG_BID: {sum(bids) / len(bids):.4f}")


if __name__ == "__main__":
    parse_liquidity(sys.argv[1])
