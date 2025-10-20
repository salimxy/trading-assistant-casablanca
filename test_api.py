#!/usr/bin/env python3
"""Test FastAPI endpoints"""

import subprocess
import time
import requests
import json
import sys

print("\n" + "=" * 80)
print("CASABLANCA STOCK EXCHANGE - API TEST")
print("=" * 80 + "\n")

# Start the API server
print("Starting FastAPI server on port 8000...")
proc = subprocess.Popen(
    ["uvicorn", "api:app", "--host", "127.0.0.1", "--port", "8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for server to start
time.sleep(6)

try:
    base_url = "http://localhost:8000"

    # Test 1: Health check
    print("\n1. Testing /health")
    print("-" * 80)
    response = requests.get(f"{base_url}/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"  Stocks in DB: {data['data']['stocks_in_database']}")
        print(f"  Uptime: {data['data']['uptime_seconds']:.1f}s")
    else:
        print(f"✗ Failed: {response.status_code}")

    # Test 2: Get single stock
    print("\n2. Testing /stocks/VCN")
    print("-" * 80)
    response = requests.get(f"{base_url}/stocks/VCN")
    if response.status_code == 200:
        data = response.json()
        stock = data['data']
        print(f"✓ Status: {response.status_code}")
        print(f"  Ticker: {stock['ticker']}")
        print(f"  Name: {stock['name']}")
        print(f"  Price: {stock['price']} MAD")
        print(f"  Change: {stock['change_pct']}%")
    else:
        print(f"✗ Failed: {response.status_code}")

    # Test 3: Get stock history
    print("\n3. Testing /stocks/ATW/history?days=7")
    print("-" * 80)
    response = requests.get(f"{base_url}/stocks/ATW/history?days=7")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"  Ticker: {data['data']['ticker']}")
        print(f"  Records: {data['data']['records']}")
        if data['data']['history']:
            first = data['data']['history'][0]
            print(f"  First record: {first['date']}")
            print(f"    Open: {first['open']}, High: {first['high']}, Low: {first['low']}, Close: {first['close']}")
    else:
        print(f"✗ Failed: {response.status_code}")

    # Test 4: List all stocks
    print("\n4. Testing /stocks/list")
    print("-" * 80)
    response = requests.get(f"{base_url}/stocks/list")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"  Total stocks: {data['data']['total']}")
        if data['data']['stocks']:
            print(f"  First 5 stocks:")
            for stock in data['data']['stocks'][:5]:
                print(f"    {stock['ticker']:8} {stock['name']:30} {stock['price']:10.2f} MAD")
    else:
        print(f"✗ Failed: {response.status_code}")

    # Test 5: Market statistics
    print("\n5. Testing /stats")
    print("-" * 80)
    response = requests.get(f"{base_url}/stats")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"  Total stocks: {data['data']['total_stocks']}")
        if data['data']['top_gainers']:
            print(f"  Top gainer: {data['data']['top_gainers'][0]['ticker']} ({data['data']['top_gainers'][0]['change_pct']}%)")
        if data['data']['top_losers']:
            print(f"  Top loser: {data['data']['top_losers'][0]['ticker']} ({data['data']['top_losers'][0]['change_pct']}%)")
    else:
        print(f"✗ Failed: {response.status_code}")

    # Test 6: Search stocks
    print("\n6. Testing /stocks/search/BANK")
    print("-" * 80)
    response = requests.get(f"{base_url}/stocks/search/BANK")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"  Query: {data['data']['query']}")
        print(f"  Results: {data['data']['results']}")
        if data['data']['stocks']:
            print(f"  Found stocks:")
            for stock in data['data']['stocks'][:3]:
                print(f"    {stock['ticker']} - {stock['name']}")
    else:
        print(f"✗ Failed: {response.status_code}")

    # Test 7: Invalid ticker (404)
    print("\n7. Testing /stocks/INVALID (expecting 404)")
    print("-" * 80)
    response = requests.get(f"{base_url}/stocks/INVALID")
    print(f"  Status: {response.status_code} (expected 404)")
    if response.status_code == 404:
        print(f"✓ Correct error handling")
    else:
        print(f"✗ Unexpected status code")

    # Test 8: Documentation
    print("\n8. Testing /docs (Swagger)")
    print("-" * 80)
    response = requests.get(f"{base_url}/docs")
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ Swagger docs available at /docs")

    print("\n" + "=" * 80)
    print("API ENDPOINTS SUMMARY")
    print("=" * 80)
    print("✓ GET /health - API health check")
    print("✓ GET /stocks/{ticker} - Get latest stock data")
    print("✓ GET /stocks/{ticker}/history - Get historical data")
    print("✓ GET /stocks/list - Get all stocks")
    print("✓ GET /stats - Get market statistics")
    print("✓ GET /stocks/search/{query} - Search stocks")
    print("✓ GET /docs - Swagger documentation")
    print("✓ GET /redoc - ReDoc documentation")

    print("\n" + "=" * 80)
    print("API Running on: http://localhost:8000")
    print("Swagger UI: http://localhost:8000/docs")
    print("ReDoc: http://localhost:8000/redoc")
    print("=" * 80 + "\n")

finally:
    # Stop the server
    print("\nStopping API server...")
    proc.terminate()
    proc.wait(timeout=5)
    print("✓ API server stopped\n")
