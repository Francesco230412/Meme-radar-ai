import os
import html
import requests

BOT_TOKEN = os.getenv(“TELEGRAM_BOT_TOKEN”)
CHAT_ID = os.getenv(“TELEGRAM_CHAT_ID”)

TELEGRAM_URL = (
f”https://api.telegram.org/bot{BOT_TOKEN}/sendMessage”
)

def format_number(value):
try:
return f”{float(value):,.2f}”
except (TypeError, ValueError):
return “N/D”

def format_money(value):
try:
return f”${float(value):,.0f}”
except (TypeError, ValueError):
return “N/D”

def safe_text(value):
return html.escape(str(value))

def send_message(message):
if not BOT_TOKEN or not CHAT_ID:
print(“Telegram credentials missing”)
return False

try:
    response = requests.post(
        TELEGRAM_URL,
        json={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        print("Telegram API error:", data)
        return False
    print("Telegram alert sent")
    return True
except Exception as error:
    print("Telegram error:", error)
    return False

def send_token_alert(token):

score = token.get("score", 0)
category = safe_text(token.get("category", "WATCHLIST"))
risk = safe_text(token.get("risk", "NON VERIFICATO"))
confidence = safe_text(
    token.get("confidence", "NON VERIFICATA")
)
signals = token.get("signals", [])
negative_signals = token.get("negative_signals", [])
if not isinstance(signals, list):
    signals = []
if not isinstance(negative_signals, list):
    negative_signals = []
positive_text = (
    "\n".join(f"  ✅ {safe_text(item)}" for item in signals[:5])
    if signals else "  Nessun segnale disponibile"
)
negative_text = (
    "\n".join(
        f"  ⚠️ {safe_text(item)}"
        for item in negative_signals[:5]
    )
    if negative_signals else "  Nessun segnale negativo rilevato"
)
message = f"""

🛰️ MEME RADAR AI — PRO ANALYSIS

{category}

🪙 {safe_text(token.get(‘name’, ‘Unknown’))}
Token: {safe_text(token.get(‘symbol’, ‘?’))}
🌐 Blockchain: {safe_text(token.get(‘chain’, ‘?’))}

━━━━━━━━━━━━━━━━━━

🎯 SCORE: {score}/100
🧠 Valutazione: {safe_text(token.get(‘verdict’, ‘N/A’))}
⚠️ Rischio: {risk}
📊 Affidabilità dati: {confidence}

━━━━━━━━━━━━━━━━━━

💰 PREZZO E MERCATO

Prezzo: ${format_number(token.get(‘price’))}
Liquidità: {format_money(token.get(‘liquidity’))}
Volume 24h: {format_money(token.get(‘volume’))}
Market Cap: {format_money(token.get(‘market_cap’))}
FDV: {format_money(token.get(‘fdv’))}

━━━━━━━━━━━━━━━━━━

📈 MOMENTUM

Variazione 5m: {format_number(token.get(‘price_change_5m’))}%
Variazione 1h: {format_number(token.get(‘price_change_1h’))}%
Variazione 6h: {format_number(token.get(‘price_change_6h’))}%
Variazione 24h: {format_number(token.get(‘price_change_24h’))}%

━━━━━━━━━━━━━━━━━━

📦 VOLUMI

Volume 5m: {format_money(token.get(‘volume_5m’))}
Volume 1h: {format_money(token.get(‘volume_1h’))}
Volume 6h: {format_money(token.get(‘volume_6h’))}
Volume 24h: {format_money(token.get(‘volume_24h’, token.get(‘volume’)))}

━━━━━━━━━━━━━━━━━━

🟢 SEGNALI POSITIVI

{positive_text}

🔴 SEGNALI NEGATIVI

{negative_text}

━━━━━━━━━━━━━━━━━━

📍 CONTRACT ADDRESS

{safe_text(token.get(‘address’, ‘’))}

Analisi automatica. Non costituisce consiglio finanziario.
“””

return send_message(message)
