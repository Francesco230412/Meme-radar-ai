import requests
import time

DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/search?q=PEPE"

def scan_market():
    try:
        response = requests.get(DEXSCREENER_API, timeout=15)
        data = response.json()

        pairs = data.get("pairs", [])

        for pair in pairs:
            name = pair.get("baseToken", {}).get("name", "Unknown")
            symbol = pair.get("baseToken", {}).get("symbol", "???")
            price = pair.get("priceUsd", "0")
            volume = pair.get("volume", {}).get("h24", 0)
            liquidity = pair.get("liquidity", {}).get("usd", 0)
            chain = pair.get("chainId", "unknown")

            print(f"""
            TOKEN: {name} ({symbol})
            CHAIN: {chain}
            PRICE: ${price}
            VOLUME 24H: ${volume}
            LIQUIDITY: ${liquidity}
            --------------------------
            """)

    except Exception as e:
        print("Radar error:", e)

if __name__ == "__main__":
    print("MEME RADAR AI - SCANNER ONLINE")
    scan_market()
