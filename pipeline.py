from db import create_tables, get_connection
from sec_api import fetch_sec_filings, store_sec_filings_to_db
from stock_api import fetch_stock_prices_for_11days
from fred_api import fetch_treasury_10y, store_treasury_10y_to_db
from datetime import datetime, timedelta

# ========== SEC ==========
def load_sec_data(limit: int = 3):
    print(f"\nFetching up to {limit} SEC filings...")
    filings = fetch_sec_filings(limit=limit)
    store_sec_filings_to_db(filings)
    print(f"Inserted {len(filings)} SEC filings.\n")

# ========== STOCK PRICES ==========
def load_and_store_stock_returns():
    """
    For each company with a filing, fetch ~11 days of EOD prices around the earliest filing date,
    compute:
      - return_day0_to_day5 = (close_at_day5 - close_at_day0) / close_at_day0 * 100
      - return_day5_to_day10 = (close_at_day10 - close_at_day5) / close_at_day5 * 100
    Store into stock_returns table. If a required price is missing, we skip that company.
    """

    conn = get_connection()
    cur = conn.cursor()

    # Get each company's earliest filing_date
    cur.execute("""
        SELECT c.id, c.ticker, MIN(f.filing_date) AS filing_date
        FROM companies c
        JOIN filings f ON c.id = f.company_id
        WHERE c.ticker IS NOT NULL
        GROUP BY c.id, c.ticker
    """)
    rows = cur.fetchall()

    inserted = 0
    for company_id, ticker, filing_date in rows:
        if not filing_date:
            continue

        # Fetch up to ~11 days of prices (day 0..10)
        prices = fetch_stock_prices_for_11days(ticker, filing_date)
        if not prices:
            continue

        # Helper: find the close price on-or-after target_date_str
        # SORT FIRST!
        prices = sorted(prices, key=lambda x: x["date"])

        # target date strings
        day0 = filing_date
        # day5 and day10 as calendar offsets
        try:
            fd = datetime.fromisoformat(filing_date).date()
        except Exception:
            continue
        day5 = (fd + timedelta(days=5)).isoformat()
        day10 = (fd + timedelta(days=10)).isoformat()

        # NEW: find close by index, not by exact calendar date
        def find_closest_after(target):
            for p in prices:
                if p["date"] >= target:
                    return p["close"]
            return None

        day0 = filing_date
        fd = datetime.fromisoformat(filing_date).date()
        day5 = (fd + timedelta(days=5)).isoformat()
        day10 = (fd + timedelta(days=10)).isoformat()

        p0  = find_closest_after(day0)
        p5  = find_closest_after(day5)
        p10 = find_closest_after(day10)

        # Require at least Day0→Day5
        if (p0 is None) or (p5 is None):
            continue

        ret0_5 = (p5 - p0) / p0 * 100

        ret5_10 = None
        if p10 is not None and p5 != 0:
            ret5_10 = (p10 - p5) / p5 * 100


        # Insert or replace to keep the table idempotent
        cur.execute("""
            INSERT INTO stock_returns (company_id, filing_date, return_day0_to_day5, return_day5_to_day10)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(company_id, filing_date) DO UPDATE SET
                return_day0_to_day5 = excluded.return_day0_to_day5,
                return_day5_to_day10 = excluded.return_day5_to_day10
        """, (company_id, filing_date, ret0_5, ret5_10))

        inserted += 1

    conn.commit()
    conn.close()
    print(f"Inserted/updated {inserted} compact stock return rows.")

# ========== FRED ==========
def load_interest_rate_data(start_years_back: int = 10, max_rows: int = 50):
    print(f"\nFetching Treasury 10Y data...")
    rates = fetch_treasury_10y(start_years_back=start_years_back, max_rows=max_rows)
    store_treasury_10y_to_db(rates)
    print(f"Inserted {len(rates)} interest-rate rows.\n")


