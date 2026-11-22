import os
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


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
            },
            timeout=15,
        )

        response.raise_for_status()
        print("Telegram alert sent")
        return True

    except Exception as error:
        print("Telegram error:", error)
        return False


def send_token_alert(token):
    message = f"""
🚨 <b>MEME RADAR AI</b>

🪙 <b>{token.get('name', 'Unknown')} ({token.get('symbol', '?')})</b>
🌐 Network: {token.get('chain', '?')}
💰 Prezzo: ${token.get('price', 0)}
📊 Score: {token.get('score', 0)}/100
📈 Momentum: {token.get('change', 0)}%
💧 Liquidità: ${token.get('liquidity', 0):,.0f}
📦 Volume 24h: ${token.get('volume', 0):,.0f}

🧠 Valutazione: {token.get('verdict', 'N/A')}

📍 <code>{token.get('address', '')}</code>
"""
    return send_message(message)
