import requests

CHAINS = ["solana", "ethereum", "base"]

SEARCH_URL = "https://api.dexscreener.com/latest/dex/search?q={}"

SEARCH_TERMS = [
    "PEPE",
    "DOGE",
    "BONK",
    "WIF",
    "BRETT",
    "FLOKI",
    "MEME",
    "PUMP",
    "AI",
    "INU",
]

def scan_tokens():
    discovered = {}

    for term in SEARCH_TERMS:
        try:
            response = requests.get(
                SEARCH_URL.format(term),
                timeout=15
            )

            if response.status_code != 200:
                continue

            pairs = response.json().get("pairs", [])

            for pair in pairs:
                chain = pair.get("chainId", "")

                if chain not in CHAINS:
                    continue

                token = pair.get("baseToken", {})
                address = token.get("address", "")

                if not address:
                    continue

                key = f"{chain}:{address}"

                discovered[key] = pair

        except Exception as error:
            print(f"Scan error {term}: {error}")

    return list(discovered.values())


if __name__ == "__main__":
    tokens = scan_tokens()

    print(f"RADAR: {len(tokens)} token trovati")

    for token in tokens[:20]:
        base = token.get("baseToken", {})
        print(
            base.get("name"),
            base.get("symbol"),
            token.get("chainId"),
            token.get("priceUsd")
        )
