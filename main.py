import time
from scanner import scan_tokens
from analyzer import analyze_token

MIN_SCORE = 60
MAX_RESULTS = 10
SCAN_INTERVAL = 300  # 5 minuti


def process_tokens():
    print("\n" + "=" * 40)
    print("🛰️ MEME RADAR AI - SCANSIONE")
    print("=" * 40)

    tokens = scan_tokens()
    results = []

    for pair in tokens:
        try:
            analysis = analyze_token(pair)

            token = pair.get("baseToken", {})
            symbol = token.get("symbol", "UNKNOWN")
            name = token.get("name", "Unknown")
            chain = pair.get("chainId", "unknown")
            address = token.get("baseToken", {}).get("address", "")
            price = pair.get("priceUsd", 0)

            result = {
                "name": name,
                "symbol": symbol,
                "chain": chain,
                "address": address,
                "price": price,
                "score": analysis["score"],
                "verdict": analysis["verdict"],
                "signals": analysis["signals"],
                "liquidity": analysis["liquidity"],
                "volume": analysis["volume_24h"],
                "change": analysis["price_change_1h"],
            }

            results.append(result)

        except Exception as error:
            print(f"Errore analisi token: {error}")

    results.sort(key=lambda x: x["score"], reverse=True)

    print(f"\nToken analizzati: {len(results)}")

    print("\n🏆 TOP TOKEN")
    print("-" * 40)

    for token in results[:MAX_RESULTS]:
        print(
            f"{token['symbol']} | "
            f"Score: {token['score']}/100 | "
            f"{token['verdict']}"
        )

    print("\n🔥 TOKEN INTERESSANTI")
    print("-" * 40)

    for token in results:
        if token["score"] >= MIN_SCORE:
            print(f"""
🚀 {token['name']} ({token['symbol']})
🌐 Network: {token['chain']}
💰 Prezzo: ${token['price']}
💧 Liquidità: ${token['liquidity']:,.0f}
📊 Volume 24h: ${token['volume']:,.0f}
📈 Variazione 1h: {token['change']}%
🧠 Score: {token['score']}/100
🔎 Segnali: {', '.join(token['signals'])}
📍 Address: {token['address']}
""")

    return results


def main():
    print("MEME RADAR AI ONLINE")
    print("Scansione ogni 5 minuti")

    while True:
        try:
            process_tokens()
        except Exception as error:
            print("Errore generale:", error)

        print(f"\n⏳ Prossima scansione tra {SCAN_INTERVAL} secondi...")
        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    main()
