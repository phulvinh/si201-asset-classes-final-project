import requests
from typing import List, Dict
from config import SEC_API_KEY, SEC_BASE_URL
from db import get_connection

def get_offset() -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT value FROM metadata WHERE key = 'offset'")
    row = cur.fetchone()
    conn.close()
    return int(row[0]) if row else 0

def save_offset(offset: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO metadata (key, value) VALUES ('offset', ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (str(offset),))
    conn.commit()
    conn.close()

def fetch_sec_filings(limit: int = 25) -> List[Dict]:
    if not SEC_API_KEY or SEC_API_KEY.startswith("YOUR_"):
        raise ValueError("SEC_API_KEY missing in config.py")

    # Get CIKs already in database
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT cik FROM companies")
    existing_ciks = set(row[0] for row in cur.fetchall())
    conn.close()
    
    print(f"Found {len(existing_ciks)} companies already in database.")

    # Read where we last left off
    offset = get_offset()
    
    url = f"{SEC_BASE_URL}?token={SEC_API_KEY}"
    
    # Track unique NEW CIKs and their most recent filing
    unique_ciks = {}
    page_size = 25
    total_fetched = 0
    max_pages = 100  # Safety limit to avoid infinite loops
    pages_fetched = 0
    
    # Keep fetching until we have enough unique NEW CIKs
    while len(unique_ciks) < limit and pages_fetched < max_pages:
        payload = {
            "query": (
                'formType:"8-K" AND ('
                '"convertible debt" OR '
                '"convertible note" OR '
                '"convertible notes" OR '
                '"convertible bond" OR '
                '"convertible bonds"'
                ")"
            ),
            "from": str(offset + total_fetched),
            "size": str(page_size),
            "sort": [{"filedAt": {"order": "desc"}}]
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        filings_in_page = data.get("filings", [])
        
        # If no more filings available, break
        if not filings_in_page:
            print(f"No more filings available. Got {len(unique_ciks)} new unique companies.")
            break
        
        for item in filings_in_page:
            description = item.get("formDescription", "").lower()
            
            if "convertible preferred" in description:
                continue

            cik = item.get("cik")
            
            # Skip if we already have this CIK in the database OR in current batch
            if cik in existing_ciks or cik in unique_ciks:
                continue
            
            raw_name = item.get("companyName", "") or ""
            clean_name = " ".join(w.capitalize() for w in raw_name.split())

            unique_ciks[cik] = {
                "cik": cik,
                "company_name": clean_name,
                "ticker": item.get("ticker"),
                "filing_date": item.get("filedAt", "")[:10],
                "filing_url": item.get("linkToHtml"),
                "is_convertible": 1
            }
            
            # Stop if we've reached our limit
            if len(unique_ciks) >= limit:
                break
        
        total_fetched += len(filings_in_page)
        pages_fetched += 1
        
        # If we got fewer results than page_size, we've reached the end
        if len(filings_in_page) < page_size:
            print(f"Reached end of available filings. Got {len(unique_ciks)} new unique companies.")
            break
    
    # Save next offset
    save_offset(offset + total_fetched)
    
    # Convert dict to list
    filings = list(unique_ciks.values())
    
    print(f"Returning {len(filings)} new companies.")
    
    return filings


def store_sec_filings_to_db(filings: List[Dict]) -> None:
    conn = get_connection()
    cur = conn.cursor()

    for f in filings:
        cik = f["cik"]
        name = f["company_name"]
        ticker = f.get("ticker")

        # Insert company (ignore if already exists)
        cur.execute("""
            INSERT OR IGNORE INTO companies (cik, name, ticker)
            VALUES (?, ?, ?)
        """, (cik, name, ticker))

        # Fetch company_id
        cur.execute("SELECT id FROM companies WHERE cik = ?", (cik,))
        row = cur.fetchone()
        if not row:
            print(f"Could not find company_id for CIK {cik}, skipping filing.")
            continue
        company_id = row[0]

        # Insert filing (ignore if accession_number already exists)
        cur.execute("""
            INSERT OR IGNORE INTO filings 
            (company_id, filing_date, filing_url, is_convertible)
            VALUES (?, ?, ?, ?)
        """, (
            company_id,
            f["filing_date"],
            f["filing_url"],
            f["is_convertible"]
        ))

    conn.commit()
    conn.close()