# main.py
from db import create_tables
from db import create_tables
from pipeline import load_sec_data, load_and_store_stock_returns, load_interest_rate_data
from analysis import run_analysis

# ======================================================
# ===================== MAIN FLOW ======================
# ======================================================
def main():
    print("🔧 Initializing database...")
    create_tables()

    # A) Fetch SEC convertible bond filings
    load_sec_data(limit=50)

    # B) Fetch stock prices for companies already in DB
    load_and_store_stock_returns()

    # C) Fetch interest-rate history (only 10Y)
    load_interest_rate_data(start_years_back=5, max_rows=99999)

    # D) Run analysis
    run_analysis()

    print("main.py finished. Uncomment steps to run specific loads.")

if __name__ == "__main__":
    main()