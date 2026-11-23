import requests
from collections import defaultdict

CHAINS = {"solana", "ethereum", "base"}

BASE_URL = "https://api.dexscreener.com"

SEARCH_TERMS = [
    "PEPE", "DOGE", "BONK", "WIF",
    "BRETT", "FLOKI", "MEME", "PUMP",
    "AI", "INU"
]

MAX_TOKENS_PER_CHAIN = 30

session = requests.Session()
session.headers.update({
    "User-Agent": "MemeRadarAI/1.0"
})


def get_json(url, params=None):
    try:
        response = session.get(
            url,
            params=params,
            timeout=20
        )
        response.raise_for_status()
        return response.json()
    except Exception as error:
        print(f"API error: {error}")
        return None


def discover_latest(endpoint):
    data = get_json(f"{BASE_URL}/{endpoint}")

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        return [data]

    return []


def scan_tokens():
    candidates = defaultdict(set)
    sources = defaultdict(set)

    # 1. Ultimi profili pubblicati
    profiles = discover_latest("token-profiles/latest/v1")

    for item in profiles:
        chain = item.get("chainId")
        address = item.get("tokenAddress")

        if chain in CHAINS and address:
            candidates[chain].add(address)
            sources[(chain, address)].add("NEW_PROFILE")

    # 2. Token con boost recenti
    boosts = discover_latest("token-boosts/latest/v1")

    for item in boosts:
        chain = item.get("chainId")
        address = item.get("tokenAddress")

        if chain in CHAINS and address:
            candidates[chain].add(address)
            sources[(chain, address)].add("BOOSTED")

    # 3. Ricerca di mercato
    for term in SEARCH_TERMS:
        data = get_json(
            f"{BASE_URL}/latest/dex/search",
            params={"q": term}
        )

        if not isinstance(data, dict):
            continue

        for pair in data.get("pairs") or []:
            chain = pair.get("chainId")
            token = pair.get("baseToken") or {}
            address = token.get("address")

            if chain in CHAINS and address:
                candidates[chain].add(address)
                sources[(chain, address)].add("MARKET_SEARCH")

    # 4. Recupero dati completi dei token
    discovered = {}

    for chain, addresses in candidates.items():

        address_list = list(addresses)[:MAX_TOKENS_PER_CHAIN]

        for start in range(0, len(address_list), 30):
            batch = address_list[start:start + 30]

            if not batch:
                continue

            url = (
                f"{BASE_URL}/tokens/v1/"
                f"{chain}/{','.join(batch)}"
            )

            pairs = get_json(url)

            if not isinstance(pairs, list):
                continue

            for pair in pairs:
                token = pair.get("baseToken") or {}
                address = token.get("address")

                if not address:
                    continue

                key = f"{chain}:{address}"

                pair["discovery_sources"] = sorted(
                    sources.get((chain, address), set())
                )

                liquidity = (
                    pair.get("liquidity") or {}
                ).get("usd") or 0

                previous = discovered.get(key)

                previous_liquidity = (
                    (previous.get("liquidity") or {}).get("usd") or 0
                    if previous else -1
                )

                if previous is None or liquidity > previous_liquidity:
                    discovered[key] = pair

    results = list(discovered.values())

    print(f"RADAR: {len(results)} coppie trovate")
    print(f"Token candidati: {sum(len(v) for v in candidates.values())}")

    return results


if __name__ == "__main__":
    tokens = scan_tokens()

    for token in tokens[:20]:
        base = token.get("baseToken") or {}

        print(
            base.get("symbol"),
            token.get("chainId"),
            token.get("priceUsd"),
            token.get("discovery_sources")
        )
