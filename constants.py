"""
Casablanca Stock Exchange - Constants and Configuration
"""

# Working tickers (validated on 2025-10-20)
# Total: 60 tickers (82.2% success rate)
WORKING_TICKERS = [
    'ADH', 'ADI', 'AFM', 'AKT', 'ALM', 'ARD', 'ATL', 'ATW',
    'BAL', 'BCI', 'BCP', 'BOA', 'CDM', 'CIH', 'CMA', 'CMT',
    'COL', 'CRS', 'CSR', 'CTM', 'DHO', 'DIS', 'DLM', 'DWY',
    'EQD', 'FBR', 'GAZ', 'HPS', 'IAM', 'IBC', 'JET', 'LBV',
    'LES', 'M2M', 'MIC', 'MLE', 'MNG', 'MUT', 'NEJ', 'OUL',
    'PRO', 'RDS', 'REB', 'RIS', 'SAH', 'SBM', 'SID', 'SMI',
    'SNA', 'SNP', 'SOT', 'SRM', 'STR', 'TGC', 'TMA', 'TQM',
    'UMR', 'VCN', 'WAA', 'ZDJ'
]

# Casablanca Bourse API configuration
API_BASE_URL = "https://www.casablanca-bourse.com/_next/data/{build_id}/fr/live-market/instruments/{ticker}.json"
CURRENT_BUILD_ID = "uwlP8zo7fj-u9phPebGR5"  # Updated: 2025-10-20

# API rate limiting
REQUEST_DELAY_SECONDS = 2.0  # Delay between requests to avoid rate limiting
MAX_RETRIES = 3  # Maximum retry attempts
RETRY_BACKOFF_BASE = 1.0  # Base delay for exponential backoff (seconds)

# Request configuration
REQUEST_TIMEOUT = 10  # Timeout in seconds
VERIFY_SSL = False  # SSL verification (disabled for development)

# Database configuration
DATABASE_URL = "sqlite:///stocks.db"

# API version for monitoring
API_VERSION = "1.0.0"
LAST_API_VALIDATION = "2025-10-20"  # Last date API structure was validated
