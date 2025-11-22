import requests
from typing import List, Dict
from datetime import datetime
from config import FRED_API_KEY, FRED_BASE_URL
from db import get_connection

# FRED series IDs we care about
FRED_SERIES = {
    "effr": "FEDFUNDS",      # Effective Federal Funds Rate
    "treasury_10y": "DGS10", # 10-year Treasury
    "baa_yield": "BAA"       # Moody's BAA Corporate Bond Yield
}

            


