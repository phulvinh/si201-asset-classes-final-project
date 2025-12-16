import os

DB_NAME = "asset_classes.db"

# DO NOT REMOVE ENVIRONMENT VARIABLES :D
SEC_API_KEY = os.environ.get("SEC_API_KEY", "e60cbfade64527d4094aecba4db30423e3210e34cbe3e8be14601cee14ddd37d")
# Rob's Key: 9ac33dd00ac48350c86f810689a689c6206eaa53abeef44838ea9dafdb62d675
# Phu's Key: cd987be4425e8c3064ce4d602f913b3edc27a1af91be9396fbc377055fc2e0de
# Sophia's Key: 1e0bee76211ed335942de329a3d7546254e01cc9ba44c43d8a26aea2f3554ec5 
# Sophia's second key: "e60cbfade64527d4094aecba4db30423e3210e34cbe3e8be14601cee14ddd37d"


STOCKDATA_API_KEY = os.environ.get("STOCKDATA_API_KEY", "MRexJ4p6r1G4c0u1wpB2ESUlZUg0qAUp7x9hrHJB")
# Rob's Key: yK3BNhS1Mzce5lqaHCgNGHkSfkBch8i4yo4KBkPE
# Phu's Key: MRexJ4p6r1G4c0u1wpB2ESUlZUg0qAUp7x9hrHJB
# Phu's Second Key: lnXNwNFp0CTqC1XzL81IINaOqI2OaX7EI0gtsWZt
# Sophia's Key: ZDMd8ioxFdLAiLjStBW6YT8ViK6C7SOqt041ZG8v
# Sophia's 2nd Key: 8YchiSc69LMnBEufdyCFQMAJNFCE77SqroMXLIdQ
FRED_API_KEY = os.environ.get("FRED_API_KEY", "6471ba9502c9cad924b13c056bf84aae")

SEC_BASE_URL = "https://api.sec-api.io"
STOCKDATA_BASE_URL = "https://api.stockdata.org/v1"
FRED_BASE_URL = "https://api.stlouisfed.org/fred"