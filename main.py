import time
from scanner import scan_tokens
from analyzer import analyze_token
from telegram_alerts import send_token_alert

MIN_SCORE = 60
MAX_RESULTS = 10
SCAN_INTERVAL = 300

sent_tokens = set()


def process_tokens():
    print("\n🛰️ MEME RADAR AI - SCANSIONE")

    tokens = scan_tokens()
    results = []

    for pair in tokens:
        try:
            analysis = analyze_token(pair)
            token_data = pair.get("baseToken", {})

            result = {
                "name": token_data.get("name", "Unknown"),
                "symbol": token_data.get("symbol", "?"),
                "chain": pair.get("chainId", "?"),
                "address": token_data.get("address", ""),
                "price": float(pair.get("priceUsd") or 0),
                "score": analysis.get("score", 0),
                "verdict": analysis.get("verdict", "N/A"),
                "signals": analysis.get("signals", []),
                "liquidity": analysis.get("liquidity", 0),
                "volume": analysis.get("volume_24h", 0),
                "change": analysis.get("price_change_1h", 0),
            }

            results.append(result)

        except Exception as error:
            print(f"Errore analisi token: {error}")

    results.sort(key=lambda x: x["score"], reverse=True)

    print(f"Token analizzati: {len(results)}")

    for token in results[:MAX_RESULTS]:
        print(
            f"{token['symbol']} | "
            f"Score: {token['score']}/100 | "
            f"{token['verdict']}"
        )

    # Invio alert Telegram
    for token in results:
        if token["score"] >= MIN_SCORE:
            key = f"{token['chain']}:{token['address']}"

            if key not in sent_tokens:
                if send_token_alert(token):
                    sent_tokens.add(key)
                    print(f"Alert inviato: {token['symbol']}")

    return results


def main():
    print("🚀 MEME RADAR AI AVVIATO")
    print("Scansione ogni 5 minuti")

    while True:
        try:
            process_tokens()
        except Exception as error:
            print("Errore scansione:", error)

        print("⏳ Attesa prossima scansione...")
        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    main()
