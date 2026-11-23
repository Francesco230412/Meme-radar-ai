import os
import html
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def format_number(value):
    try:
        return f"{float(value):,.8f}".rstrip("0").rstrip(".")
    except (TypeError, ValueError):
        return "N/D"


def format_money(value):
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return "N/D"


def safe_text(value):
    return html.escape(str(value))


def send_message(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram credentials missing")
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
            print(f"Telegram API error: {data}")
            return False

        print("Telegram alert sent")
        return True

    except Exception as error:
        print(f"Telegram error: {error}")
        return False


def send_token_alert(token):

    score = token.get("score", 0)
    category = safe_text(token.get("category", "WATCHLIST"))
    risk = safe_text(token.get("risk", "NON VERIFICATO"))
    confidence = safe_text(token.get("confidence", "NON VERIFICATA"))

    signals = token.get("signals", [])
    negative_signals = token.get("negative_signals", [])

    if not isinstance(signals, list):
        signals = []

    if not isinstance(negative_signals, list):
        negative_signals = []

    positive_text = (
        "\n".join(
            f"✅ {safe_text(item)}"
            for item in signals[:5]
        )
        if signals
        else "Nessun segnale disponibile"
    )

    negative_text = (
        "\n".join(
            f"⚠️ {safe_text(item)}"
            for item in negative_signals[:5]
        )
        if negative_signals
        else "Nessun segnale negativo rilevato"
    )

    message = f"""
<b>MEME RADAR AI - PRO ANALYSIS</b>

{category}

🪙 <b>{safe_text(token.get('name', 'Unknown'))}</b>
<b>Token:</b> {safe_text(token.get('symbol', '?'))}
🌐 <b>Blockchain:</b> {safe_text(token.get('chain', '?'))}

━━━━━━━━━━━━━━━━━━

🎯 <b>SCORE: {score}/100</b>
🧠 <b>Valutazione:</b> {safe_text(token.get('verdict', 'N/A'))}
⚠️ <b>Rischio:</b> {risk}
📊 <b>Affidabilità dati:</b> {confidence}

━━━━━━━━━━━━━━━━━━

💰 <b>MERCATO</b>

Prezzo: ${format_number(token.get('price'))}
Liquidità: {format_money(token.get('liquidity'))}
Volume 24h: {format_money(token.get('volume'))}
Market Cap: {format_money(token.get('market_cap'))}
FDV: {format_money(token.get('fdv'))}

━━━━━━━━━━━━━━━━━━

📈 <b>MOMENTUM</b>

5m: {format_number(token.get('price_change_5m'))}%
1h: {format_number(token.get('price_change_1h'))}%
6h: {format_number(token.get('price_change_6h'))}%
24h: {format_number(token.get('price_change_24h'))}%

━━━━━━━━━━━━━━━━━━

📦 <b>VOLUMI</b>

5m: {format_money(token.get('volume_5m'))}
1h: {format_money(token.get('volume_1h'))}
6h: {format_money(token.get('volume_6h'))}
24h: {format_money(token.get('volume_24h', token.get('volume')))}

━━━━━━━━━━━━━━━━━━

🟢 <b>SEGNALI POSITIVI</b>

{positive_text}

━━━━━━━━━━━━━━━━━━

🔴 <b>SEGNALI NEGATIVI</b>

{negative_text}

━━━━━━━━━━━━━━━━━━

📍 <b>CONTRACT ADDRESS</b>

<code>{safe_text(token.get('address', ''))}</code>

<i>Analisi automatica - Non costituisce consiglio finanziario.</i>
"""

    return send_message(message)
