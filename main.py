from scanner import scan_tokens
from analyzer import analyze_token
from telegram_alerts import send_token_alert

MIN_SCORE = 60
MAX_RESULTS = 10


def process_tokens():
    print("\n🛰️ MEME RADAR AI - SCANSIONE")

    tokens = scan_tokens()
    results = []
    sent_tokens = set()

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

    for token in results:
        if token["score"] >= MIN_SCORE:
            try:
                if send_token_alert(token):
                    print(f"Alert inviato: {token['symbol']}")
            except Exception as error:
                print(f"Errore Telegram: {error}")

    return results


def main():
    print("🚀 MEME RADAR AI - AVVIO")
    print("Modalità GitHub Actions: scansione singola")

    try:
        process_tokens()
        print("✅ Scansione completata")

    except Exception as error:
        print(f"❌ Errore scansione: {error}")


if __name__ == "__main__":
    main()
