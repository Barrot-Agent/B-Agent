import sys


def parse_liquidity(filepath):
    try:
        with open(filepath, "r") as f:
            bids = [float(line.split('"')[3]) for line in f if "bid" in line]

        if not bids:
            print("SIGNAL: NULL_LIQUIDITY")
            return

        avg_bid = sum(bids) / len(bids)
        print(f"SIGNAL: STRIKE_READY | AVG_BID: {avg_bid:.4f}")

    except Exception as e:
        print(f"SIGNAL: ERROR_{e}")


if __name__ == "__main__":
    parse_liquidity(sys.argv[1])
