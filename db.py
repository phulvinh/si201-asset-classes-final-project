'''
import sqlite3
from config import DB_NAME

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cik TEXT UNIQUE,
            name TEXT,
            ticker TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS filings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            filing_date TEXT,
            filing_type TEXT,
            filing_url TEXT,
            is_convertible INTEGER, -- 0 or 1
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            date TEXT,
            close REAL,
            high REAL,
            low REAL,
            volume INTEGER,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS interest_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            effr REAL,
            treasury_10y REAL,
            baa_yield REAL
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully.")
'''
import sqlite3
from config import DB_NAME

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")  # Enforce FK constraints
    return conn

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    # ------------------------
    # COMPANIES
    # ------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cik TEXT UNIQUE,
            name TEXT,
            ticker TEXT
        )
    """)

    # ------------------------
    # FILINGS (raw SEC data)
    # ------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS filings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            filing_date TEXT,
            filing_type TEXT,
            filing_url TEXT,
            is_convertible INTEGER,            -- 0 or 1
            description_excerpt TEXT,          -- snippet showing issuance
            amount_issued REAL,                -- parsed if available
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)

    # ------------------------
    # STOCK PRICES (raw OHLCV)
    # ------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            date TEXT,
            close REAL,
            high REAL,
            low REAL,
            volume INTEGER,
            return REAL,                       -- daily return
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)

    # ------------------------
    # INTEREST RATES (FRED)
    # ------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interest_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            effr REAL,              -- Effective Federal Funds Rate
            treasury_10y REAL,      -- 10-Year Treasury yield
            baa_yield REAL          -- BAA yield (optional)
        )
    """)

    # ------------------------
    # COMPUTED METRICS (derived analytics)
    # ------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS computed_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            filing_id INTEGER,
            volatility_12m REAL,              -- annualized vol
            interest_rate_on_date REAL,       -- EFFR at issuance date
            treasury_yield_on_date REAL,      -- 10Y at issuance date
            baa_yield_on_date REAL,           -- BAA at issuance date
            FOREIGN KEY (company_id) REFERENCES companies(id),
            FOREIGN KEY (filing_id) REFERENCES filings(id)
        )
    """)

    # ------------------------
    # INDEXES (for performance)
    # ------------------------
    cur.execute("CREATE INDEX IF NOT EXISTS idx_filings_company ON filings(company_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_prices_company ON stock_prices(company_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_prices_date ON stock_prices(date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_rates_date ON interest_rates(date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_metrics_company ON computed_metrics(company_id)")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully.")
