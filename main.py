from scanner import scan_tokens
from analyzer import analyze_token
from telegram_alerts import send_token_alert

MIN_SCORE = 65
MAX_RESULTS = 10

def get_category(score):
if score >= 90:
return “🔥 ELITE SIGNAL”
elif score >= 80:
return “🚀 HIGH CONVICTION”
elif score >= 65:
return “👀 WATCHLIST”
return “⚪ Nessun segnale”

def process_tokens():
print(”\n🛰️ MEME RADAR AI - SCANSIONE”)

tokens = scan_tokens()
results = []
analyzed_addresses = set()
for pair in tokens:
    try:
        analysis = analyze_token(pair)
        token_data = pair.get("baseToken", {})
        address = token_data.get("address", "")
        chain = pair.get("chainId", "?")
        # Evita di analizzare più volte lo stesso token
        # sulla stessa blockchain durante questa scansione.
        token_id = f"{chain}:{address.lower()}"
        if not address or token_id in analyzed_addresses:
            continue
        analyzed_addresses.add(token_id)
        # Conserva tutte le metriche prodotte dall'analizzatore.
        result = dict(analysis)
        # Dati identificativi e di mercato.
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
print("\n📊 MIGLIORI RISULTATI")
for token in results[:MAX_RESULTS]:
    print(
        f"{token['symbol']} | "
        f"Score: {token['score']}/100 | "
        f"{token['category']} | "
        f"Rischio: {token['risk']}"
    )
print("\n📨 CONTROLLO SEGNALI TELEGRAM")
alerts_sent = 0
for token in results:
    if token["score"] < MIN_SCORE:
        continue
    # Non inviare segnali promozionali per token ad alto rischio.
    if str(token.get("risk", "")).upper() == "ALTO":
        print(f"⛔ {token['symbol']}: escluso per rischio alto")
        continue
    try:
        if send_token_alert(token):
            alerts_sent += 1
            print(
                f"✅ Alert inviato: "
                f"{token['symbol']} - {token['category']}"
            )
    except Exception as error:
        print(f"Errore Telegram: {error}")
print(f"\n📬 Alert inviati: {alerts_sent}")
return results

def main():
print(“🚀 MEME RADAR AI - AVVIO”)
print(“Modalità GitHub Actions: scansione singola”)
print(f”Soglia minima alert: {MIN_SCORE}/100”)

try:
    process_tokens()
    print("✅ Scansione completata")
except Exception as error:
    print(f"❌ Errore scansione: {error}")

if name == “main”:
main()
