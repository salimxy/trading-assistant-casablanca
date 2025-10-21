"""
Technical Indicators for Stock Analysis

Calculates various technical indicators used for stock analysis:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- SMA (Simple Moving Average)
- Volume analysis
- Trend detection
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging
from db import get_history, get_latest

logger = logging.getLogger(__name__)


def calculate_rsi(data: pd.Series, period: int = 14) -> float:
    """
    Calculate Relative Strength Index (RSI).

    Args:
        data: Price data (close prices)
        period: RSI period (default: 14)

    Returns:
        RSI value (0-100)
    """
    if len(data) < period + 1:
        return None

    # Calculate price changes
    delta = data.diff()

    # Separate gains and losses
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)

    # Calculate average gains and losses
    avg_gain = gains.rolling(window=period).mean()
    avg_loss = losses.rolling(window=period).mean()

    # Avoid division by zero
    if avg_loss.iloc[-1] == 0:
        return 100.0

    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return float(rsi.iloc[-1])


def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
    """
    Calculate MACD (Moving Average Convergence Divergence).

    Args:
        data: Price data (close prices)
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line period (default: 9)

    Returns:
        Dictionary with macd, signal, and histogram values
    """
    if len(data) < slow + signal:
        return {'macd': None, 'signal': None, 'histogram': None}

    # Calculate EMAs
    ema_fast = data.ewm(span=fast, adjust=False).mean()
    ema_slow = data.ewm(span=slow, adjust=False).mean()

    # Calculate MACD line
    macd_line = ema_fast - ema_slow

    # Calculate signal line
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()

    # Calculate histogram
    histogram = macd_line - signal_line

    return {
        'macd': float(macd_line.iloc[-1]),
        'signal': float(signal_line.iloc[-1]),
        'histogram': float(histogram.iloc[-1])
    }


def calculate_sma(data: pd.Series, period: int = 20) -> float:
    """
    Calculate Simple Moving Average (SMA).

    Args:
        data: Price data
        period: SMA period (default: 20)

    Returns:
        SMA value
    """
    if len(data) < period:
        return None

    sma = data.rolling(window=period).mean()
    return float(sma.iloc[-1])


def calculate_ema(data: pd.Series, period: int = 20) -> float:
    """
    Calculate Exponential Moving Average (EMA).

    Args:
        data: Price data
        period: EMA period (default: 20)

    Returns:
        EMA value
    """
    if len(data) < period:
        return None

    ema = data.ewm(span=period, adjust=False).mean()
    return float(ema.iloc[-1])


def detect_trend(data: pd.Series, period: int = 20) -> str:
    """
    Detect price trend (bullish, bearish, or neutral).

    Args:
        data: Price data
        period: Period for trend analysis

    Returns:
        'bullish', 'bearish', or 'neutral'
    """
    if len(data) < period:
        return 'neutral'

    # Calculate slope of linear regression
    x = np.arange(len(data))
    y = data.values

    # Simple linear regression
    slope = np.polyfit(x[-period:], y[-period:], 1)[0]

    # Determine trend based on slope
    if slope > 0.01:
        return 'bullish'
    elif slope < -0.01:
        return 'bearish'
    else:
        return 'neutral'


def analyze_volume(history_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze volume patterns.

    Args:
        history_df: DataFrame with volume data

    Returns:
        Dictionary with volume analysis
    """
    if history_df.empty or 'volume' not in history_df.columns:
        return {
            'current_volume': None,
            'avg_volume': None,
            'volume_ratio': None,
            'above_average': False
        }

    volumes = history_df['volume'].dropna()

    if len(volumes) == 0:
        return {
            'current_volume': None,
            'avg_volume': None,
            'volume_ratio': None,
            'above_average': False
        }

    current_volume = float(volumes.iloc[-1])
    avg_volume = float(volumes.mean())

    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0

    return {
        'current_volume': current_volume,
        'avg_volume': avg_volume,
        'volume_ratio': volume_ratio,
        'above_average': volume_ratio > 1.0
    }


def calculate_indicators(ticker: str, days: int = 30) -> Optional[Dict[str, Any]]:
    """
    Calculate all technical indicators for a stock.

    Args:
        ticker: Stock ticker symbol
        days: Number of days of historical data to use

    Returns:
        Dictionary with all calculated indicators or None if insufficient data
    """
    try:
        # Get historical data
        history_df = get_history(ticker, days=days)

        if history_df.empty:
            logger.warning(f"No historical data for {ticker}")
            return None

        # Need at least 30 days for reliable indicators
        if len(history_df) < 30:
            logger.warning(f"Insufficient data for {ticker}: {len(history_df)} days (need 30+)")
            return None

        # Get current price
        latest = get_latest(ticker)
        current_price = latest['price'] if latest else None

        # Extract close prices
        close_prices = history_df['close'].dropna()

        if len(close_prices) < 30:
            logger.warning(f"Insufficient close price data for {ticker}")
            return None

        # Calculate all indicators
        rsi = calculate_rsi(close_prices, period=14)
        macd_data = calculate_macd(close_prices)
        sma_20 = calculate_sma(close_prices, period=20)
        sma_50 = calculate_sma(close_prices, period=50) if len(close_prices) >= 50 else None
        ema_20 = calculate_ema(close_prices, period=20)
        trend = detect_trend(close_prices, period=20)
        volume_analysis = analyze_volume(history_df)

        indicators = {
            'ticker': ticker,
            'current_price': current_price,
            'rsi': rsi,
            'macd': macd_data,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'ema_20': ema_20,
            'trend': trend,
            'volume': volume_analysis,
            'data_points': len(history_df)
        }

        logger.info(f"Calculated indicators for {ticker}: RSI={rsi:.2f}, Trend={trend}")

        return indicators

    except Exception as e:
        logger.error(f"Error calculating indicators for {ticker}: {e}")
        return None


def format_indicators(indicators: Dict[str, Any]) -> str:
    """
    Format indicators for display.

    Args:
        indicators: Dictionary of calculated indicators

    Returns:
        Formatted string
    """
    if not indicators:
        return "No indicators available"

    lines = [
        f"=" * 60,
        f"Technical Indicators - {indicators['ticker']}",
        f"=" * 60,
        f"Current Price: {indicators['current_price']:.2f} MAD" if indicators['current_price'] else "Current Price: N/A",
        f"",
        f"Momentum:",
        f"  RSI (14): {indicators['rsi']:.2f}" if indicators['rsi'] else "  RSI: N/A",
        f"",
        f"Trend:",
        f"  MACD: {indicators['macd']['macd']:.4f}" if indicators['macd']['macd'] is not None else "  MACD: N/A",
        f"  Signal: {indicators['macd']['signal']:.4f}" if indicators['macd']['signal'] is not None else "  Signal: N/A",
        f"  Histogram: {indicators['macd']['histogram']:.4f}" if indicators['macd']['histogram'] is not None else "  Histogram: N/A",
        f"  Trend: {indicators['trend'].upper()}",
        f"",
        f"Moving Averages:",
        f"  SMA (20): {indicators['sma_20']:.2f} MAD" if indicators['sma_20'] else "  SMA (20): N/A",
        f"  SMA (50): {indicators['sma_50']:.2f} MAD" if indicators['sma_50'] else "  SMA (50): N/A",
        f"  EMA (20): {indicators['ema_20']:.2f} MAD" if indicators['ema_20'] else "  EMA (20): N/A",
        f"",
        f"Volume:",
        f"  Current: {indicators['volume']['current_volume']:,.0f}" if indicators['volume']['current_volume'] else "  Current: N/A",
        f"  Average: {indicators['volume']['avg_volume']:,.0f}" if indicators['volume']['avg_volume'] else "  Average: N/A",
        f"  Ratio: {indicators['volume']['volume_ratio']:.2f}x" if indicators['volume']['volume_ratio'] else "  Ratio: N/A",
        f"  Status: {'ABOVE AVERAGE' if indicators['volume'].get('above_average') else 'BELOW AVERAGE'}",
        f"",
        f"Data Points: {indicators['data_points']} days",
        f"=" * 60
    ]

    return "\n".join(lines)


if __name__ == "__main__":
    # Test indicators
    import sys

    logging.basicConfig(level=logging.INFO)

    test_tickers = ['VCN', 'ATW', 'BCP']

    print("\n" + "=" * 60)
    print("TECHNICAL INDICATORS TEST")
    print("=" * 60 + "\n")

    for ticker in test_tickers:
        indicators = calculate_indicators(ticker, days=30)

        if indicators:
            print(format_indicators(indicators))
        else:
            print(f"Could not calculate indicators for {ticker}")

        print()
