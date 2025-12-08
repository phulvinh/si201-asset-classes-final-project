import os

DB_NAME = "asset_classes1.db"

# DO NOT REMOVE ENVIRONMENT VARIABLES :D
SEC_API_KEY = os.environ.get("SEC_API_KEY", "9ac33dd00ac48350c86f810689a689c6206eaa53abeef44838ea9dafdb62d675")
# Rob's Key: 9ac33dd00ac48350c86f810689a689c6206eaa53abeef44838ea9dafdb62d675
# Phu's Key: cd987be4425e8c3064ce4d602f913b3edc27a1af91be9396fbc377055fc2e0de
STOCKDATA_API_KEY = os.environ.get("STOCKDATA_API_KEY", "yK3BNhS1Mzce5lqaHCgNGHkSfkBch8i4yo4KBkPE")
# Rob's Key: yK3BNhS1Mzce5lqaHCgNGHkSfkBch8i4yo4KBkPE
# Phu's Key: MRexJ4p6r1G4c0u1wpB2ESUlZUg0qAUp7x9hrHJB
# Sophia's Key: ZDMd8ioxFdLAiLjStBW6YT8ViK6C7SOqt041ZG8v
FRED_API_KEY = os.environ.get("FRED_API_KEY", "6471ba9502c9cad924b13c056bf84aae")

SEC_BASE_URL = "https://api.sec-api.io"
STOCKDATA_BASE_URL = "https://api.stockdata.org/v1"
FRED_BASE_URL = "https://api.stlouisfed.org/fred"