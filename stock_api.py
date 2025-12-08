import requests
from datetime import datetime, timedelta
from typing import List, Dict
from config import STOCKDATA_API_KEY, STOCKDATA_BASE_URL
from db import get_connection

def fetch_stock_prices_for_11days(ticker: str, filing_date_str: str) -> List[Dict]:
    start_dt = datetime.fromisoformat(filing_date_str)

    # Request a slightly larger range to handle weekends / missing days
    date_from = start_dt.strftime("%Y-%m-%d")
    date_to = (start_dt + timedelta(days=12)).strftime("%Y-%m-%d")

    url = f"{STOCKDATA_BASE_URL}/data/eod"
    params = {
        "api_token": STOCKDATA_API_KEY,
        "symbols": ticker,
        "date_from": date_from,
        "date_to": date_to,
    }

    resp = requests.get(url, params=params)

    data = resp.json()
    raw = data.get("data", []) if isinstance(data, dict) else []

    normalized = []
    
    for rec in raw:
        d = rec.get("date")
        close = rec.get("close")
    
        try:
            if d and close is not None:
                normalized.append({"date": d, "close": float(close)})
    
        except (TypeError, ValueError):
            continue

    if len(normalized) == 0:
        normalized.append({"date": date_from, "close": 0.0})
    normalized.sort(key=lambda r: r["date"])
    
    # Sort by date ascending
    return normalized

def store_stock_prices_to_db(company_id: int, prices: List[Dict]) -> None:
    conn = get_connection()
    cur = conn.cursor()

    for p in prices:
    
        cur.execute("""
            INSERT OR IGNORE INTO stock_prices (company_id, date, close, high, low, volume)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            company_id,
            p.get("date"),
            p.get("close", 0.0),
            p.get("high", 0.0),
            p.get("low", 0.0),
            p.get("volume", 0.0)
        ))


    conn.commit()
    conn.close()