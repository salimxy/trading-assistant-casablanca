#!/usr/bin/env python3
"""
Test suite for technical indicators module
Tests RSI, MACD, SMA, EMA, Bollinger Bands, and Stochastic Oscillator
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from indicators import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_stochastic,
    calculate_all_indicators,
    get_trading_signals
)


def create_test_data(periods: int = 100, seed: int = 42) -> pd.DataFrame:
    """Create synthetic test data"""
    np.random.seed(seed)

    dates = pd.date_range(start='2024-01-01', periods=periods, freq='D')

    # Generate realistic price data with trend
    price = 100
    prices = [price]
    highs = [price * 1.02]
    lows = [price * 0.98]
    opens = [price]

    for i in range(1, periods):
        # Random walk with slight upward bias
        change = np.random.randn() * 2 + 0.1
        price = max(price * (1 + change / 100), 1)
        prices.append(price)

        # High/Low/Open
        highs.append(price * (1 + abs(np.random.randn()) * 0.01))
        lows.append(price * (1 - abs(np.random.randn()) * 0.01))
        opens.append(prices[-2] * (1 + np.random.randn() * 0.005))

    df = pd.DataFrame({
        'date': dates,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, periods)
    })

    return df


def test_sma():
    """Test Simple Moving Average calculation"""
    print("\n" + "=" * 80)
    print("TEST 1: Simple Moving Average (SMA)")
    print("=" * 80)

    # Create simple test data
    data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # Test SMA(5)
    sma = calculate_sma(data, period=5)

    # Expected: [NaN, NaN, NaN, NaN, 3, 4, 5, 6, 7, 8]
    # (1+2+3+4+5)/5 = 3, (2+3+4+5+6)/5 = 4, etc.

    assert pd.isna(sma.iloc[3]), "First 4 values should be NaN"
    assert abs(sma.iloc[4] - 3.0) < 0.01, f"SMA(5) at index 4 should be 3.0, got {sma.iloc[4]}"
    assert abs(sma.iloc[5] - 4.0) < 0.01, f"SMA(5) at index 5 should be 4.0, got {sma.iloc[5]}"
    assert abs(sma.iloc[-1] - 8.0) < 0.01, f"SMA(5) at last index should be 8.0, got {sma.iloc[-1]}"

    print(f"✓ SMA calculation correct")
    print(f"  Sample values: {sma.tail(5).tolist()}")


def test_ema():
    """Test Exponential Moving Average calculation"""
    print("\n" + "=" * 80)
    print("TEST 2: Exponential Moving Average (EMA)")
    print("=" * 80)

    df = create_test_data(periods=50)
    ema_12 = calculate_ema(df['close'], period=12)
    ema_26 = calculate_ema(df['close'], period=26)

    # EMA should have some values after the period
    assert not pd.isna(ema_12.iloc[-1]), "EMA(12) should have value at end"
    assert not pd.isna(ema_26.iloc[-1]), "EMA(26) should have value at end"

    # EMA should generally follow price trend
    assert ema_12.iloc[-1] > 0, "EMA should be positive"

    print(f"✓ EMA calculation correct")
    print(f"  EMA(12) last value: {ema_12.iloc[-1]:.2f}")
    print(f"  EMA(26) last value: {ema_26.iloc[-1]:.2f}")


def test_rsi():
    """Test RSI calculation"""
    print("\n" + "=" * 80)
    print("TEST 3: Relative Strength Index (RSI)")
    print("=" * 80)

    df = create_test_data(periods=100)
    rsi = calculate_rsi(df['close'], period=14)

    # RSI should be between 0 and 100
    valid_rsi = rsi.dropna()
    assert all(valid_rsi >= 0), "RSI should be >= 0"
    assert all(valid_rsi <= 100), "RSI should be <= 100"

    # Should have valid values after warmup period
    assert not pd.isna(rsi.iloc[-1]), "RSI should have value at end"

    print(f"✓ RSI calculation correct")
    print(f"  RSI range: {valid_rsi.min():.2f} - {valid_rsi.max():.2f}")
    print(f"  Last RSI value: {rsi.iloc[-1]:.2f}")

    # Test interpretation
    last_rsi = rsi.iloc[-1]
    if last_rsi < 30:
        print(f"  → OVERSOLD signal")
    elif last_rsi > 70:
        print(f"  → OVERBOUGHT signal")
    else:
        print(f"  → NEUTRAL")


def test_macd():
    """Test MACD calculation"""
    print("\n" + "=" * 80)
    print("TEST 4: MACD (Moving Average Convergence Divergence)")
    print("=" * 80)

    df = create_test_data(periods=100)
    macd_line, signal_line, histogram = calculate_macd(df['close'])

    # Should have values after warmup
    assert not pd.isna(macd_line.iloc[-1]), "MACD line should have value"
    assert not pd.isna(signal_line.iloc[-1]), "Signal line should have value"
    assert not pd.isna(histogram.iloc[-1]), "Histogram should have value"

    # Histogram should equal MACD - Signal
    last_hist_calc = macd_line.iloc[-1] - signal_line.iloc[-1]
    assert abs(histogram.iloc[-1] - last_hist_calc) < 0.01, "Histogram should equal MACD - Signal"

    print(f"✓ MACD calculation correct")
    print(f"  MACD Line: {macd_line.iloc[-1]:.4f}")
    print(f"  Signal Line: {signal_line.iloc[-1]:.4f}")
    print(f"  Histogram: {histogram.iloc[-1]:.4f}")

    # Check for crossover
    if macd_line.iloc[-1] > signal_line.iloc[-1]:
        print(f"  → MACD above signal (BULLISH)")
    else:
        print(f"  → MACD below signal (BEARISH)")


def test_bollinger_bands():
    """Test Bollinger Bands calculation"""
    print("\n" + "=" * 80)
    print("TEST 5: Bollinger Bands")
    print("=" * 80)

    df = create_test_data(periods=100)
    upper, middle, lower = calculate_bollinger_bands(df['close'], period=20, std_dev=2)

    # Should have values
    assert not pd.isna(upper.iloc[-1]), "Upper band should have value"
    assert not pd.isna(middle.iloc[-1]), "Middle band should have value"
    assert not pd.isna(lower.iloc[-1]), "Lower band should have value"

    # Upper > Middle > Lower
    assert upper.iloc[-1] > middle.iloc[-1], "Upper band should be > middle"
    assert middle.iloc[-1] > lower.iloc[-1], "Middle band should be > lower"

    # Price should usually be within bands
    current_price = df['close'].iloc[-1]

    print(f"✓ Bollinger Bands calculation correct")
    print(f"  Upper Band: {upper.iloc[-1]:.2f}")
    print(f"  Middle Band: {middle.iloc[-1]:.2f}")
    print(f"  Lower Band: {lower.iloc[-1]:.2f}")
    print(f"  Current Price: {current_price:.2f}")

    if current_price > upper.iloc[-1]:
        print(f"  → Price ABOVE upper band (OVERBOUGHT)")
    elif current_price < lower.iloc[-1]:
        print(f"  → Price BELOW lower band (OVERSOLD)")
    else:
        print(f"  → Price WITHIN bands (NORMAL)")


def test_stochastic():
    """Test Stochastic Oscillator calculation"""
    print("\n" + "=" * 80)
    print("TEST 6: Stochastic Oscillator")
    print("=" * 80)

    df = create_test_data(periods=100)
    k_percent, d_percent = calculate_stochastic(
        df['high'], df['low'], df['close'], k_period=14, d_period=3
    )

    # Should have values
    assert not pd.isna(k_percent.iloc[-1]), "%K should have value"
    assert not pd.isna(d_percent.iloc[-1]), "%D should have value"

    # Should be between 0 and 100
    valid_k = k_percent.dropna()
    valid_d = d_percent.dropna()
    assert all(valid_k >= 0) and all(valid_k <= 100), "%K should be 0-100"
    assert all(valid_d >= 0) and all(valid_d <= 100), "%D should be 0-100"

    print(f"✓ Stochastic calculation correct")
    print(f"  %K: {k_percent.iloc[-1]:.2f}")
    print(f"  %D: {d_percent.iloc[-1]:.2f}")

    if k_percent.iloc[-1] < 20:
        print(f"  → OVERSOLD signal")
    elif k_percent.iloc[-1] > 80:
        print(f"  → OVERBOUGHT signal")
    else:
        print(f"  → NEUTRAL")


def test_all_indicators():
    """Test calculating all indicators at once"""
    print("\n" + "=" * 80)
    print("TEST 7: Calculate All Indicators")
    print("=" * 80)

    df = create_test_data(periods=100)
    result = calculate_all_indicators(df)

    # Check that all expected columns exist
    expected_cols = [
        'rsi', 'macd', 'macd_signal', 'macd_histogram',
        'sma_20', 'sma_50', 'ema_12', 'ema_26',
        'bb_upper', 'bb_middle', 'bb_lower',
        'stoch_k', 'stoch_d'
    ]

    for col in expected_cols:
        assert col in result.columns, f"Missing column: {col}"

    # Check that we have values in the latest row
    latest = result.iloc[-1]
    print(f"✓ All indicators calculated successfully")
    print(f"\n  Latest values:")
    print(f"    RSI: {latest['rsi']:.2f}")
    print(f"    MACD: {latest['macd']:.4f}")
    print(f"    SMA(20): {latest['sma_20']:.2f}")
    print(f"    SMA(50): {latest['sma_50']:.2f}")
    print(f"    Close: {latest['close']:.2f}")


def test_trading_signals():
    """Test trading signal generation"""
    print("\n" + "=" * 80)
    print("TEST 8: Trading Signals Generation")
    print("=" * 80)

    df = create_test_data(periods=100)
    df_with_indicators = calculate_all_indicators(df)
    signals = get_trading_signals(df_with_indicators)

    # Should have required keys
    assert 'signal' in signals, "Should have 'signal' key"
    assert 'confidence' in signals, "Should have 'confidence' key"
    assert 'score' in signals, "Should have 'score' key"
    assert 'indicators' in signals, "Should have 'indicators' key"

    # Signal should be one of the expected values
    valid_signals = ['STRONG BUY', 'BUY', 'HOLD', 'SELL', 'STRONG SELL']
    assert signals['signal'] in valid_signals, f"Invalid signal: {signals['signal']}"

    # Confidence should be HIGH, MEDIUM, or LOW
    valid_confidence = ['HIGH', 'MEDIUM', 'LOW']
    assert signals['confidence'] in valid_confidence, f"Invalid confidence: {signals['confidence']}"

    print(f"✓ Trading signals generated successfully")
    print(f"\n  SIGNAL: {signals['signal']}")
    print(f"  CONFIDENCE: {signals['confidence']}")
    print(f"  SCORE: {signals['score']}")
    print(f"\n  Analysis:")
    for indicator in signals['indicators']:
        print(f"    • {indicator}")


def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n" + "=" * 80)
    print("TEST 9: Edge Cases and Error Handling")
    print("=" * 80)

    # Test with insufficient data
    df_small = create_test_data(periods=10)

    # RSI with insufficient data
    rsi = calculate_rsi(df_small['close'], period=14)
    assert all(pd.isna(rsi)), "RSI should be all NaN with insufficient data"
    print(f"✓ RSI handles insufficient data correctly")

    # MACD with insufficient data
    macd_line, signal_line, histogram = calculate_macd(df_small['close'])
    assert all(pd.isna(macd_line)), "MACD should be all NaN with insufficient data"
    print(f"✓ MACD handles insufficient data correctly")

    # Test with exactly minimum data
    df_min = create_test_data(periods=30)
    result = calculate_all_indicators(df_min)
    assert 'rsi' in result.columns, "Should calculate indicators with minimum data"
    print(f"✓ Indicators work with minimum data")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("TECHNICAL INDICATORS TEST SUITE")
    print("=" * 80)
    print(f"Testing all technical indicators...")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Simple Moving Average (SMA)", test_sma),
        ("Exponential Moving Average (EMA)", test_ema),
        ("Relative Strength Index (RSI)", test_rsi),
        ("MACD", test_macd),
        ("Bollinger Bands", test_bollinger_bands),
        ("Stochastic Oscillator", test_stochastic),
        ("All Indicators", test_all_indicators),
        ("Trading Signals", test_trading_signals),
        ("Edge Cases", test_edge_cases)
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ FAILED: {name}")
            print(f"  Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ ERROR: {name}")
            print(f"  Error: {e}")
            failed += 1

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {failed} ✗")
    print(f"Success Rate: {100 * passed / len(tests):.1f}%")
    print("=" * 80)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉\n")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
