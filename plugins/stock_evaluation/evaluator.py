from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def evaluate_stock(data: dict) -> dict:
    """Evaluates the stock using pure algorithmic rules."""
    result = {
        "technical_score": 0,
        "fundamental_score": 0,
        "sentiment_score": 0,
        "overall_score": 0,
        "recommendation": "Hold",
        "notes": []
    }
    
    info = data.get("info", {})
    fundamentals = data.get("fundamentals", {})
    history = data.get("history")
    news = data.get("news", [])
    
    # 1. Technical Evaluation (Basic momentum / moving averages)
    current_price = fundamentals.get("current_price", 0)
    high = fundamentals.get("fifty_two_week_high", 0)
    low = fundamentals.get("fifty_two_week_low", 0)
    
    if current_price and high and low and high != low:
        pos = (current_price - low) / (high - low)
        if pos > 0.8:
            result["technical_score"] += 1
            result["notes"].append("Price is near 52-week high (Bullish momentum).")
        elif pos < 0.2:
            result["technical_score"] -= 1
            result["notes"].append("Price is near 52-week low (Bearish or oversold).")
            
    # 2. Fundamental Evaluation
    pe = fundamentals.get("pe_ratio")
    if pe is not None:
        if 0 < pe < 15:
            result["fundamental_score"] += 2
            result["notes"].append("P/E ratio is attractive (< 15).")
        elif pe > 30:
            result["fundamental_score"] -= 1
            result["notes"].append("P/E ratio is high (> 30).")
            
    roe = fundamentals.get("roe")
    if roe is not None:
        if roe > 0.15:
            result["fundamental_score"] += 1
            result["notes"].append("Strong Return on Equity (> 15%).")
        elif roe < 0:
            result["fundamental_score"] -= 1
            result["notes"].append("Negative Return on Equity.")
            
    debt = fundamentals.get("debt_to_equity")
    if debt is not None:
        if debt < 50:
            result["fundamental_score"] += 1
            result["notes"].append("Low debt to equity ratio (< 50%).")
        elif debt > 100:
            result["fundamental_score"] -= 1
            result["notes"].append("High debt load (> 100%).")

    # 3. Sentiment Evaluation
    analyzer = SentimentIntensityAnalyzer()
    compound_scores = []
    for item in news:
        vs = analyzer.polarity_scores(item["title"])
        compound_scores.append(vs["compound"])
        
    if compound_scores:
        avg_sentiment = sum(compound_scores) / len(compound_scores)
        if avg_sentiment > 0.15:
            result["sentiment_score"] += 1
            result["notes"].append("Recent news sentiment is positive.")
        elif avg_sentiment < -0.15:
            result["sentiment_score"] -= 1
            result["notes"].append("Recent news sentiment is negative.")
            
    # Combine scores
    total = result["technical_score"] + result["fundamental_score"] + result["sentiment_score"]
    result["overall_score"] = total
    
    if total >= 3:
        result["recommendation"] = "Strong Buy"
    elif total == 2:
        result["recommendation"] = "Buy"
    elif total in [-1, -2]:
        result["recommendation"] = "Sell"
    elif total <= -3:
        result["recommendation"] = "Strong Sell"
    else:
        result["recommendation"] = "Hold"
        
    return result
