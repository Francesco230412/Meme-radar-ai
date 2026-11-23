from scanner import scan_tokens
from analyzer import analyze_token
from telegram_alerts import send_token_alert

MIN_SCORE = 65
MAX_RESULTS = 10


def get_category(score):
    if score >= 90:
        return "ELITE SIGNAL"
    elif score >= 80:
        return "HIGH CONVICTION"
    elif score >= 65:
        return "WATCHLIST"
    else:
        return "NO SIGNAL"


def process_tokens():
    print("MEME RADAR AI - SCANSIONE")

    tokens = scan_tokens()
    results = []
    analyzed_addresses = set()

    for pair in tokens:
        try:
            analysis = analyze_token(pair)
            token_data = pair.get("baseToken", {})

            address = token_data.get("address", "")
            chain = pair.get("chainId", "?")

            token_id = f"{chain}:{address.lower()}"

            if not address or token_id in analyzed_addresses:
                continue

            analyzed_addresses.add(token_id)

            result = dict(analysis)

            result.update({
                "name": token_data.get("name", "Unknown"),
                "symbol": token_data.get("symbol", "?"),
                "chain": chain,
                "address": address,
                "price": float(pair.get("priceUsd") or 0),
                "score": analysis.get("score", 0),
                "verdict": analysis.get("verdict", "N/A"),
                "signals": analysis.get("signals", []),
                "negative_signals": analysis.get("negative_signals", []),
                "risk": analysis.get("risk", "NON VERIFICATO"),
                "confidence": analysis.get("confidence", "NON VERIFICATA"),
                "liquidity": analysis.get("liquidity", 0),
                "volume": analysis.get("volume_24h", 0),
                "change": analysis.get("price_change_1h", 0),
            })

            result["category"] = get_category(result["score"])
            results.append(result)

        except Exception as error:
            print(f"Errore analisi token: {error}")

    results.sort(key=lambda x: x["score"], reverse=True)

    print(f"Token analizzati: {len(results)}")
    print("MIGLIORI RISULTATI")

    for token in results[:MAX_RESULTS]:
        print(
            f"{token['symbol']} | "
            f"Score: {token['score']}/100 | "
            f"{token['category']} | "
            f"Risk: {token['risk']}"
        )

    alerts_sent = 0

    print("CONTROLLO TELEGRAM")

    for token in results:
        if token["score"] < MIN_SCORE:
            continue

        if str(token.get("risk", "")).upper() == "ALTO":
            print(f"ESCLUSO PER RISCHIO ALTO: {token['symbol']}")
            continue

        try:
            if send_token_alert(token):
                alerts_sent += 1
                print(f"Alert inviato: {token['symbol']}")

        except Exception as error:
            print(f"Errore Telegram: {error}")

    print(f"Alert inviati: {alerts_sent}")

    return results


def main():
    print("MEME RADAR AI - AVVIO")
    print("Modalita GitHub Actions: scansione singola")
    print(f"Soglia minima alert: {MIN_SCORE}/100")

    try:
        process_tokens()
        print("Scansione completata")

    except Exception as error:
        print(f"Errore scansione: {error}")


if __name__ == "__main__":
    main()
