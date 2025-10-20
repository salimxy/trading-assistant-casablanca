#!/usr/bin/env python3
"""Test script for database operations"""

import sys
from scraper import get_stock_data
from db import init_db, save_stock, get_latest, get_all_stocks, save_history

def main():
    print("\n" + "=" * 70)
    print("CASABLANCA STOCK EXCHANGE - DATABASE TEST")
    print("=" * 70 + "\n")

    # Initialize database
    print("1. Initializing database...")
    init_db()
    print()

    # Tickers to test
    tickers = ['VCN', 'ATW', 'BCP']

    # Fetch and save stock data
    print("2. Fetching and saving stock data...")
    for ticker in tickers:
        print(f"\n   Fetching {ticker}...")
        stock_data = get_stock_data(ticker)

        if stock_data:
            # Save current stock data
            save_stock(stock_data)

            # Also save to history
            save_history(ticker, stock_data)
        else:
            print(f"   ✗ Failed to fetch {ticker}")

    print()

    # Retrieve and display all stocks
    print("3. Retrieving all stocks from database...")
    print()
    df_all = get_all_stocks()

    if not df_all.empty:
        print(df_all.to_string(index=False))
    else:
        print("   No stocks found")

    print()

    # Get individual stock details
    print("4. Retrieving latest data for each ticker...")
    print()

    for ticker in tickers:
        latest = get_latest(ticker)
        if latest:
            print(f"   {ticker}:")
            print(f"      Name: {latest['name']}")
            print(f"      Price: {latest['price']} MAD")
            print(f"      Change: {latest['change_pct']}%")
            print(f"      Volume: {latest['volume']} MAD")
            print(f"      Updated: {latest['timestamp']}")
        else:
            print(f"   {ticker}: Not found")

    print()
    print("=" * 70)
    print("Database file: stocks.db")
    print("You can open it with DB Browser for SQLite (Mac)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
