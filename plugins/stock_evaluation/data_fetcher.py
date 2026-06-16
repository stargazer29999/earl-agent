import yfinance as yf
import feedparser
import urllib.parse
from typing import Dict, Any

def fetch_all_data(ticker: str) -> Dict[str, Any]:
    """Fetches market, financial, and news data for the given ticker."""
    result = {"valid": False, "ticker": ticker}
    
    try:
        stock = yf.Ticker(ticker)
        
        # Fast check if valid
        info = stock.info
        if "regularMarketPrice" not in info and "currentPrice" not in info and "previousClose" not in info:
            # Maybe invalid ticker, or network issue
            return result
            
        result["valid"] = True
        result["info"] = info
        
        # 1. Historical data for technicals (6 months)
        hist = stock.history(period="6mo")
        result["history"] = hist
        
        # 2. Fundamentals
        result["fundamentals"] = {
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "pb_ratio": info.get("priceToBook"),
            "debt_to_equity": info.get("debtToEquity"),
            "roe": info.get("returnOnEquity"),
            "revenue_growth": info.get("revenueGrowth"),
            "profit_margins": info.get("profitMargins"),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice", 0.0),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        }
        
        # 3. News (Yahoo Finance RSS)
        encoded_ticker = urllib.parse.quote(ticker)
        rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={encoded_ticker}&region=US&lang=en-US"
        feed = feedparser.parse(rss_url)
        
        news_items = []
        for entry in feed.entries[:10]: # Get top 10 news
            news_items.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.get("published", "")
            })
        result["news"] = news_items
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        
    return result
