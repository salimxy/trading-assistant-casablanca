# Casablanca Stock Exchange API

FastAPI-powered REST API for accessing real-time and historical stock data from the Casablanca Stock Exchange (Bourse de Casablanca).

## Quick Start

### Start the Server

```bash
uvicorn api:app --reload --port 8000
```

Or with production settings:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Documentation

- **Swagger UI (Interactive)**: http://localhost:8000/docs
- **ReDoc (Alternative)**: http://localhost:8000/redoc

## Base URL

```
http://localhost:8000
```

## Response Format

All successful responses follow this format:

```json
{
  "success": true,
  "data": { /* endpoint-specific data */ },
  "timestamp": "2025-10-20T21:34:50.847589+00:00",
  "ticker": "VCN"  // only for stock-specific endpoints
}
```

Error responses:

```json
{
  "success": false,
  "error": "Error message",
  "timestamp": "2025-10-20T21:34:50.847589+00:00"
}
```

## Endpoints

### 1. Health Check

Check API status and database connectivity.

**Request:**
```bash
GET /health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "uptime_seconds": 123.45,
    "stocks_in_database": 60,
    "version": "1.0.0"
  },
  "timestamp": "2025-10-20T21:34:50.847589+00:00"
}
```

**Status Codes:**
- `200` - API is healthy
- `500` - Database error

---

### 2. Get Single Stock

Get the latest data for a specific stock.

**Request:**
```bash
GET /stocks/{ticker}
```

**Parameters:**
- `ticker` (path, required) - Stock ticker symbol (e.g., VCN, ATW, BCP)

**Response:**
```json
{
  "success": true,
  "data": {
    "ticker": "VCN",
    "name": "VICENNE",
    "price": 471.0,
    "change_pct": 7.2892938497,
    "volume": 19286358.0,
    "timestamp": "2025-10-20T21:28:33.945890"
  },
  "timestamp": "2025-10-20T21:34:55.423880+00:00",
  "ticker": "VCN"
}
```

**Status Codes:**
- `200` - Success
- `404` - Ticker not found
- `500` - Database error

**Examples:**
```bash
curl http://localhost:8000/stocks/VCN
curl http://localhost:8000/stocks/ATW
curl http://localhost:8000/stocks/BCP
```

---

### 3. Get Stock History

Get historical daily data for a stock.

**Request:**
```bash
GET /stocks/{ticker}/history
```

**Parameters:**
- `ticker` (path, required) - Stock ticker symbol
- `days` (query, optional) - Number of days to retrieve (1-365, default: 30)

**Response:**
```json
{
  "success": true,
  "data": {
    "ticker": "ATW",
    "days": 30,
    "records": 2,
    "history": [
      {
        "date": "2025-10-20T00:00:00",
        "open": 742.0,
        "high": 744.0,
        "low": 730.0,
        "close": 744.0,
        "volume": 44065978.6
      }
    ]
  },
  "timestamp": "2025-10-20T21:35:01.717136+00:00",
  "ticker": "ATW"
}
```

**Status Codes:**
- `200` - Success
- `404` - Ticker not found
- `500` - Database error

**Examples:**
```bash
# Last 30 days (default)
curl http://localhost:8000/stocks/VCN/history

# Last 7 days
curl http://localhost:8000/stocks/VCN/history?days=7

# Last 90 days
curl "http://localhost:8000/stocks/VCN/history?days=90"
```

---

### 4. List All Stocks

Get all available stocks with their current prices.

**Request:**
```bash
GET /stocks/list
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 60,
    "stocks": [
      {
        "ticker": "VCN",
        "name": "VICENNE",
        "price": 471.0,
        "change_pct": 7.2892938497,
        "volume": 19286358.0,
        "timestamp": "2025-10-20T21:28:33.945890"
      },
      // ... more stocks
    ]
  },
  "timestamp": "2025-10-20T21:35:05.929165+00:00"
}
```

**Status Codes:**
- `200` - Success
- `500` - Database error

**Example:**
```bash
curl http://localhost:8000/stocks/list
```

---

### 5. Market Statistics

Get top gainers and losers.

**Request:**
```bash
GET /stats
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_stocks": 60,
    "top_gainers": [
      {
        "ticker": "STR",
        "name": "STRATHMORE",
        "price": 123.45,
        "change_pct": 7.34
      },
      // ... more gainers
    ],
    "top_losers": [
      {
        "ticker": "MIC",
        "name": "MICRO COMPANY",
        "price": 98.76,
        "change_pct": -2.88
      },
      // ... more losers
    ]
  },
  "timestamp": "2025-10-20T21:35:05.929165+00:00"
}
```

**Status Codes:**
- `200` - Success
- `500` - Database error

**Example:**
```bash
curl http://localhost:8000/stats
```

---

### 6. Search Stocks

Search stocks by ticker or company name.

**Request:**
```bash
GET /stocks/search/{query}
```

**Parameters:**
- `query` (path, required) - Search term (ticker or company name)

**Response:**
```json
{
  "success": true,
  "data": {
    "query": "BANK",
    "results": 2,
    "stocks": [
      {
        "ticker": "ATW",
        "name": "ATTIJARIWAFA BANK",
        "price": 744.0,
        "change_pct": 2.2,
        "volume": 44065978.6,
        "timestamp": "2025-10-20T21:28:33.945890"
      },
      {
        "ticker": "BOA",
        "name": "BANK OF AFRICA",
        "price": 456.0,
        "change_pct": 1.5,
        "volume": 12345678.0,
        "timestamp": "2025-10-20T21:28:33.945890"
      }
    ]
  },
  "timestamp": "2025-10-20T21:35:05.929165+00:00"
}
```

**Status Codes:**
- `200` - Success
- `500` - Database error

**Examples:**
```bash
curl http://localhost:8000/stocks/search/BANK
curl http://localhost:8000/stocks/search/VCN
curl http://localhost:8000/stocks/search/TELECOM
```

---

### 7. Root Endpoint

Get API information and available endpoints.

**Request:**
```bash
GET /
```

**Response:**
```json
{
  "message": "Casablanca Stock Exchange API",
  "documentation": {
    "swagger": "/docs",
    "redoc": "/redoc"
  },
  "endpoints": {
    "health": "/health",
    "stocks_list": "/stocks/list",
    "stock_latest": "/stocks/{ticker}",
    "stock_history": "/stocks/{ticker}/history?days=30",
    "stats": "/stats",
    "search": "/stocks/search/{query}"
  }
}
```

---

## Error Handling

### 404 Not Found

When a ticker doesn't exist:

```bash
curl http://localhost:8000/stocks/INVALID
```

Response:

```json
{
  "success": false,
  "error": "Ticker 'INVALID' not found",
  "timestamp": "2025-10-20T21:35:05.929165+00:00"
}
```

### 500 Internal Server Error

When there's a database error:

```json
{
  "success": false,
  "error": "Database error",
  "timestamp": "2025-10-20T21:35:05.929165+00:00"
}
```

---

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:3000` (React default)
- `http://localhost:5173` (Vite default)
- `http://localhost:8080` (Vue default)
- `*` (All origins)

To add more origins, modify the `CORS` middleware in `api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://your-domain.com",  # Add your domain
        "*"
    ],
    ...
)
```

---

## Usage Examples

### JavaScript/Fetch

```javascript
// Get latest stock data
fetch('http://localhost:8000/stocks/VCN')
  .then(response => response.json())
  .then(data => console.log(data.data));

// Get stock history
fetch('http://localhost:8000/stocks/VCN/history?days=7')
  .then(response => response.json())
  .then(data => console.log(data.data.history));

// List all stocks
fetch('http://localhost:8000/stocks/list')
  .then(response => response.json())
  .then(data => console.log(data.data.stocks));
```

### Python/Requests

```python
import requests

# Get latest stock data
response = requests.get('http://localhost:8000/stocks/VCN')
data = response.json()
print(data['data'])

# Get stock history
response = requests.get('http://localhost:8000/stocks/VCN/history?days=7')
history = response.json()['data']['history']

# List all stocks
response = requests.get('http://localhost:8000/stocks/list')
stocks = response.json()['data']['stocks']
```

### cURL

```bash
# Health check
curl http://localhost:8000/health

# Get stock
curl http://localhost:8000/stocks/VCN

# Get history
curl "http://localhost:8000/stocks/VCN/history?days=7"

# List all
curl http://localhost:8000/stocks/list

# Stats
curl http://localhost:8000/stats

# Search
curl http://localhost:8000/stocks/search/BANK
```

---

## Available Stocks (60 validated tickers)

### Validated Tickers
ADH, ADI, AFM, AKT, ALM, ARD, ATL, ATW, BAL, BCI, BCP, BOA, CDM, CIH, CMA, CMT, COL, CRS, CSR, CTM, DIS, DHO, DLM, DWY, EQD, FBR, GAZ, HPS, IAM, IBC, JET, LBV, LES, M2M, MIC, MLE, MNG, MUT, NEJ, OUL, PRO, RDS, REB, RIS, SAH, SBM, SID, SMI, SNA, SNP, SOT, SRM, STR, TGC, TMA, TQM, UMR, VCN, WAA, ZDJ

**Note**: Only validated tickers from `constants.py` are available to ensure optimal performance.

---

## Performance

- **Response time**: <100ms per request (local)
- **Database**: SQLite with indexed queries
- **Max request delay**: 2 seconds between scraper requests to avoid rate limiting
- **Caching**: Responses reflect latest database state

---

## Logging

API logs are sent to both console and can be viewed in the process output:

```bash
# With verbose logging
uvicorn api:app --log-level debug --port 8000
```

---

## Deployment

For production deployment:

```bash
# Using Gunicorn + Uvicorn
gunicorn api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --port 8000

# Using Docker
docker run -p 8000:8000 -v /path/to/stocks.db:/app/stocks.db \
  uvicorn api:app --host 0.0.0.0 --port 8000
```

---

## Files

- `constants.py` - Configuration and validated tickers
- `scraper.py` - Web scraper with API monitoring
- `api.py` - FastAPI application and endpoints
- `db.py` - SQLAlchemy database models and functions
- `stocks.db` - SQLite database
- `API_DOCUMENTATION.md` - This file

---

## API Monitoring

The scraper includes automatic monitoring for:
- **Build ID changes**: Detects when Next.js build ID changes
- **API structure changes**: Validates response structure
- **Critical alerts**: Logs warnings when updates needed

If API changes are detected, check logs for update instructions.

---

## Support

For issues or questions, check:
1. API logs for detailed error messages
2. Scraper logs for API monitoring alerts
3. Swagger UI at `/docs` for interactive testing
4. Database integrity with `test_db.py`
5. Update `CURRENT_BUILD_ID` in `constants.py` if build ID changes

---

**API Version**: 1.0.1
**Last Updated**: 2025-10-21
**Monitoring**: ✅ Active
