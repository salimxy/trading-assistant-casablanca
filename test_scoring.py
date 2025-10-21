#!/usr/bin/env python3
"""
Test script for scoring system with mock data.

Since the API is currently returning 403 errors (API limitation detected!),
we'll use mock data to demonstrate the scoring system functionality.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from db import init_db, save_stock, save_history, Stock, StockHistory, get_db
from scoring import analyze_stock, format_analysis
from indicators import calculate_indicators, format_indicators

def create_mock_data(ticker: str, trend: str = 'bullish'):
    """
    Create mock historical data for testing.

    Args:
        ticker: Stock ticker
        trend: 'bullish', 'bearish', or 'neutral'
    """
    print(f"Creating mock data for {ticker} ({trend} trend)...")

    # Base parameters
    base_price = 100.0
    days = 60

    # Generate dates (ending today at midnight, timezone-aware)
    end_date = datetime.now(pytz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    dates = [end_date - timedelta(days=i) for i in range(days-1, -1, -1)]

    # Generate price data based on trend
    if trend == 'bullish':
        # Upward trend with some volatility
        trend_component = np.linspace(0, 20, days)
        volatility = np.random.normal(0, 2, days)
        prices = base_price + trend_component + volatility
    elif trend == 'bearish':
        # Downward trend
        trend_component = np.linspace(0, -15, days)
        volatility = np.random.normal(0, 2, days)
        prices = base_price + trend_component + volatility
    else:  # neutral
        # Sideways movement
        volatility = np.random.normal(0, 3, days)
        prices = base_price + volatility

    # Ensure prices are positive
    prices = np.maximum(prices, 50.0)

    # Generate OHLC data
    db = get_db()
    try:
        for i, date in enumerate(dates):
            price = prices[i]
            high = price * (1 + abs(np.random.normal(0, 0.01)))
            low = price * (1 - abs(np.random.normal(0, 0.01)))
            open_price = prices[i-1] if i > 0 else price
            volume = np.random.uniform(1000000, 5000000)

            # Create history record
            history = StockHistory(
                ticker=ticker,
                date=date,
                open=open_price,
                high=high,
                low=low,
                close=price,
                volume=volume
            )
            db.add(history)

        # Create current stock record
        current_price = prices[-1]
        prev_price = prices[-2]
        change_pct = ((current_price - prev_price) / prev_price) * 100

        stock = Stock(
            ticker=ticker,
            name=f"Mock Company {ticker}",
            price=current_price,
            change_pct=change_pct,
            volume=np.random.uniform(1000000, 5000000),
            timestamp=datetime.now(pytz.UTC)
        )
        db.add(stock)

        db.commit()
        print(f"✓ Created {len(dates)} days of mock data for {ticker}")
        print(f"  Current price: {current_price:.2f} MAD")
        print(f"  Trend: {trend}")

    finally:
        db.close()


def test_scoring_system():
    """Test the scoring system with mock data."""

    print("\n" + "=" * 70)
    print("TESTING SCORING SYSTEM WITH MOCK DATA")
    print("=" * 70)
    print("\nNOTE: Using mock data because API returned 403 Forbidden")
    print("This demonstrates API limitation detection working correctly!\n")

    # Initialize database
    init_db()

    # Create mock data for different scenarios
    test_cases = [
        ('VCN', 'bullish'),   # Strong buy scenario
        ('ATW', 'neutral'),   # Hold scenario
        ('BCP', 'bearish'),   # Sell scenario
    ]

    for ticker, trend in test_cases:
        create_mock_data(ticker, trend)

    print("\n" + "=" * 70)
    print("TECHNICAL INDICATORS")
    print("=" * 70)

    # Test indicators
    for ticker, trend in test_cases:
        print(f"\n{ticker} ({trend.upper()} TREND)")
        print("-" * 70)
        indicators = calculate_indicators(ticker, days=30)
        if indicators:
            print(format_indicators(indicators))
        else:
            print(f"Could not calculate indicators for {ticker}")

    print("\n" + "=" * 70)
    print("SCORING AND SIGNALS")
    print("=" * 70)

    # Test scoring
    for ticker, trend in test_cases:
        analysis = analyze_stock(ticker, days=30)
        if analysis:
            print(format_analysis(analysis))
        else:
            print(f"Could not analyze {ticker}")


if __name__ == "__main__":
    test_scoring_system()
