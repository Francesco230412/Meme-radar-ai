def analyze_token(pair):
    liquidity = float(pair.get("liquidity", {}).get("usd", 0) or 0)
    volume = float(pair.get("volume", {}).get("h24", 0) or 0)
    price_change = float(pair.get("priceChange", {}).get("h1", 0) or 0)
    buys = int(pair.get("txns", {}).get("h1", {}).get("buys", 0) or 0)
    sells = int(pair.get("txns", {}).get("h1", {}).get("sells", 0) or 0)

    score = 0
    signals = []

    # Liquidità
    if liquidity >= 50000:
        score += 15
        signals.append("Liquidità elevata")
    elif liquidity >= 20000:
        score += 10
        signals.append("Liquidità buona")
    elif liquidity >= 10000:
        score += 5

    # Volume
    if volume >= 100000:
        score += 20
        signals.append("Volume molto elevato")
    elif volume >= 50000:
        score += 15
        signals.append("Volume elevato")
    elif volume >= 10000:
        score += 10

    # Momentum
    if price_change >= 20:
        score += 20
        signals.append("Momentum forte")
    elif price_change >= 10:
        score += 15
        signals.append("Momentum positivo")
    elif price_change >= 5:
        score += 10

    # Rapporto acquisti/vendite
    if buys + sells > 0:
        buy_ratio = buys / (buys + sells)

        if buy_ratio >= 0.70:
            score += 15
            signals.append("Pressione acquisti forte")
        elif buy_ratio >= 0.60:
            score += 10
            signals.append("Prevalenza acquisti")
        elif buy_ratio >= 0.50:
            score += 5

    score = min(score, 100)

    if score >= 70:
        verdict = "🚀 INTERESSANTE"
    elif score >= 50:
        verdict = "👀 DA MONITORARE"
    else:
        verdict = "⚠️ DEBOLE"

    return {
        "score": score,
        "verdict": verdict,
        "signals": signals,
        "liquidity": liquidity,
        "volume_24h": volume,
        "price_change_1h": price_change,
        "buys_1h": buys,
        "sells_1h": sells
    }
