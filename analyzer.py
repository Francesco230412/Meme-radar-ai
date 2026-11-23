import time


def safe_float(value, default=0.0):
    try:
        result = float(value)
        if result != result or result in (float("inf"), float("-inf")):
            return default
        return result
    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return default


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def analyze_token(pair):
    """
    MEME RADAR AI
    Advanced market analysis engine.
    Score: 0-100
    """

    liquidity_data = pair.get("liquidity") or {}
    volume_data = pair.get("volume") or {}
    price_data = pair.get("priceChange") or {}
    txns_data = pair.get("txns") or {}

    liquidity = safe_float(liquidity_data.get("usd"))
    volume_5m = safe_float(volume_data.get("m5"))
    volume_1h = safe_float(volume_data.get("h1"))
    volume_6h = safe_float(volume_data.get("h6"))
    volume_24h = safe_float(volume_data.get("h24"))

    change_5m = safe_float(price_data.get("m5"))
    change_1h = safe_float(price_data.get("h1"))
    change_6h = safe_float(price_data.get("h6"))
    change_24h = safe_float(price_data.get("h24"))

    tx_5m = txns_data.get("m5") or {}
    tx_1h = txns_data.get("h1") or {}
    tx_6h = txns_data.get("h6") or {}

    buys_5m = safe_int(tx_5m.get("buys"))
    sells_5m = safe_int(tx_5m.get("sells"))

    buys_1h = safe_int(tx_1h.get("buys"))
    sells_1h = safe_int(tx_1h.get("sells"))

    buys_6h = safe_int(tx_6h.get("buys"))
    sells_6h = safe_int(tx_6h.get("sells"))

    pair_created = safe_int(pair.get("pairCreatedAt"))

    fdv = safe_float(pair.get("fdv"))
    market_cap = safe_float(pair.get("marketCap"))

    score = 0
    penalties = 0

    positive_signals = []
    negative_signals = []
    missing_data = []

    # --------------------------------
    # 1. LIQUIDITY - MAX 20 POINTS
    # --------------------------------

    if liquidity >= 250000:
        score += 20
        positive_signals.append("Liquidità eccellente")
    elif liquidity >= 100000:
        score += 17
        positive_signals.append("Liquidità molto alta")
    elif liquidity >= 50000:
        score += 14
        positive_signals.append("Buona liquidità")
    elif liquidity >= 20000:
        score += 10
        positive_signals.append("Liquidità discreta")
    elif liquidity >= 10000:
        score += 6
        negative_signals.append("Liquidità limitata")
    elif liquidity > 0:
        score += 2
        penalties += 10
        negative_signals.append("Liquidità molto bassa")
    else:
        missing_data.append("Liquidità non disponibile")
        penalties += 10

    # --------------------------------
    # 2. VOLUME - MAX 20 POINTS
    # --------------------------------

    if volume_24h >= 1000000:
        score += 20
        positive_signals.append("Volume giornaliero eccezionale")
    elif volume_24h >= 500000:
        score += 17
        positive_signals.append("Volume giornaliero molto alto")
    elif volume_24h >= 100000:
        score += 14
        positive_signals.append("Volume elevato")
    elif volume_24h >= 50000:
        score += 10
        positive_signals.append("Volume interessante")
    elif volume_24h >= 10000:
        score += 6
    elif volume_24h > 0:
        score += 2
        negative_signals.append("Volume molto basso")
    else:
        missing_data.append("Volume non disponibile")

    # Rapporto volume / liquidità
    if liquidity > 0 and volume_24h > 0:
        volume_ratio = volume_24h / liquidity

        if volume_ratio > 100:
            penalties += 8
            negative_signals.append(
                "Volume estremamente alto rispetto alla liquidità"
            )
        elif volume_ratio > 50:
            penalties += 4
            negative_signals.append(
                "Rapporto volume/liquidità elevato"
            )
        elif 1 <= volume_ratio <= 20:
            positive_signals.append(
                "Buon rapporto volume/liquidità"
            )
    else:
        volume_ratio = 0

    # --------------------------------
    # 3. MOMENTUM - MAX 20 POINTS
    # --------------------------------

    if change_1h >= 30:
        score += 20
        positive_signals.append("Momentum orario molto forte")
    elif change_1h >= 15:
        score += 16
        positive_signals.append("Momentum orario forte")
    elif change_1h >= 5:
        score += 12
        positive_signals.append("Momentum positivo")
    elif change_1h >= 0:
        score += 6
    elif change_1h <= -20:
        penalties += 12
        negative_signals.append("Forte perdita di momentum")
    elif change_1h <= -10:
        penalties += 8
        negative_signals.append("Momentum negativo")
    elif change_1h < -5:
        penalties += 4
        negative_signals.append("Prezzo in calo")

    if change_5m >= 20:
        penalties += 5
        negative_signals.append(
            "Movimento molto rapido: possibile volatilità eccessiva"
        )

    if change_1h > 0 and change_6h < -20:
        negative_signals.append(
            "Rimbalzo orario dopo un forte calo"
        )

    if change_24h < -30:
        penalties += 5
        negative_signals.append(
            "Forte perdita nelle ultime 24 ore"
        )

    # --------------------------------
    # 4. BUY / SELL PRESSURE - MAX 15
    # --------------------------------

    if buys_1h + sells_1h > 0:
        buy_ratio = buys_1h / (buys_1h + sells_1h)

        if buy_ratio >= 0.80:
            score += 15
            positive_signals.append("Pressione acquisti molto forte")
        elif buy_ratio >= 0.70:
            score += 12
            positive_signals.append("Prevalenza netta degli acquisti")
        elif buy_ratio >= 0.60:
            score += 9
            positive_signals.append("Acquisti superiori alle vendite")
        elif buy_ratio >= 0.50:
            score += 5
        else:
            penalties += 8
            negative_signals.append("Vendite superiori agli acquisti")
    else:
        buy_ratio = 0
        missing_data.append("Transazioni orarie non disponibili")

    # Conferma della pressione nel breve periodo
    if buys_5m + sells_5m > 0:
        short_buy_ratio = buys_5m / (buys_5m + sells_5m)

        if short_buy_ratio < 0.35:
            penalties += 5
            negative_signals.append(
                "Pressione di vendita nel breve periodo"
            )
        elif short_buy_ratio >= 0.70:
            positive_signals.append(
                "Acquisti dominanti negli ultimi 5 minuti"
            )

    # --------------------------------
    # 5. ACTIVITY - MAX 10
    # --------------------------------

    total_tx_1h = buys_1h + sells_1h

    if total_tx_1h >= 1000:
        score += 10
        positive_signals.append("Attività di mercato molto elevata")
    elif total_tx_1h >= 500:
        score += 8
        positive_signals.append("Attività di mercato elevata")
    elif total_tx_1h >= 100:
        score += 6
    elif total_tx_1h >= 30:
        score += 3
    elif total_tx_1h == 0:
        missing_data.append("Attività di trading non disponibile")

    # --------------------------------
    # 6. PAIR AGE - MAX 5
    # --------------------------------

    if pair_created > 0:
        age_hours = max(
            0,
            (int(time.time() * 1000) - pair_created) / 3600000
        )

        if 1 <= age_hours <= 72:
            score += 5
            positive_signals.append("Coppia relativamente recente")
        elif age_hours < 1:
            score += 2
            positive_signals.append("Coppia appena creata")
        elif age_hours <= 168:
            score += 4
        else:
            score += 3
    else:
        age_hours = None
        missing_data.append("Età della coppia non disponibile")

    # --------------------------------
    # 7. MARKET DATA QUALITY - MAX 10
    # --------------------------------

    if market_cap > 0:
        score += 5

        if fdv > 0 and market_cap > 0:
            fdv_ratio = fdv / market_cap

            if fdv_ratio > 5:
                penalties += 5
                negative_signals.append(
                    "FDV molto superiore alla capitalizzazione"
                )
            elif fdv_ratio <= 1.5:
                score += 5
                positive_signals.append(
                    "Rapporto FDV/capitalizzazione contenuto"
                )
    else:
        missing_data.append("Market cap non disponibile")

    # --------------------------------
    # 8. FINAL SCORE
    # --------------------------------

    final_score = clamp(score - penalties, 0, 100)

    # --------------------------------
    # 9. RISK CLASSIFICATION
    # --------------------------------

    if liquidity < 10000 or liquidity == 0:
        risk = "ALTO"
    elif penalties >= 15:
        risk = "ALTO"
    elif penalties >= 8:
        risk = "MEDIO"
    else:
        risk = "CONTENUTO"

    # --------------------------------
    # 10. VERDICT
    # --------------------------------

    if final_score >= 80 and risk == "CONTENUTO":
        verdict = "🚀 TOP CANDIDATE"
    elif final_score >= 70 and risk != "ALTO":
        verdict = "🔥 INTERESSANTE"
    elif final_score >= 50:
        verdict = "👀 DA MONITORARE"
    else:
        verdict = "⚠️ DEBOLE"

    # --------------------------------
    # 11. DATA CONFIDENCE
    # --------------------------------

    available_checks = 8 - min(len(missing_data), 8)
    confidence = round((available_checks / 8) * 100)

    return {
        "score": final_score,
        "raw_score": score,
        "penalties": penalties,
        "verdict": verdict,
        "risk": risk,
        "confidence": confidence,

        "signals": positive_signals,
        "positive_signals": positive_signals,
        "negative_signals": negative_signals,
        "missing_data": missing_data,

        "liquidity": liquidity,
        "volume_24h": volume_24h,
        "volume_1h": volume_1h,
        "volume_5m": volume_5m,

        "price_change_5m": change_5m,
        "price_change_1h": change_1h,
        "price_change_6h": change_6h,
        "price_change_24h": change_24h,

        "buys_1h": buys_1h,
        "sells_1h": sells_1h,
        "buy_ratio": round(buy_ratio * 100, 2),

        "total_tx_1h": total_tx_1h,
        "volume_liquidity_ratio": round(volume_ratio, 2),

        "market_cap": market_cap,
        "fdv": fdv,
        "age_hours": age_hours
    }
