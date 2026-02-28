import requests
import time
import random

def sceptor_market_scan():
    print("[vΩ.63] SCEPTOR WING: INITIATING MARKET SCAN...")
    stability_anchor = 0.707
    url = "https://api.dexscreener.com/latest/dex/search?q=solana"

    try:
        response = requests.get(url)
        data = response.json()
        for pair in data.get('pairs', [])[:5]:
            price = float(pair.get('priceUsd', 0))
            volume = float(pair.get('volume', {}).get('h24', 0))
            if volume > 1000000 and price < 1.0:
                print(f"[!] APEX YIELD DETECTED: {pair['baseToken']['symbol']} at ${price}")
                print(f"    Action: Monitor for Liquidity Gap. Resonance: {stability_anchor}")
    except Exception as e:
        print(f"[!] SCEPTOR ERROR: {e}")

if __name__ == "__main__":
    while True:
        sceptor_market_scan()
        time.sleep(random.uniform(5, 15) * 0.707)
