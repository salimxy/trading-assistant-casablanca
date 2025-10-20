#!/usr/bin/env python3
"""
Technical Indicators Module for Stock Analysis
Supports: RSI, MACD, SMA, EMA, Bollinger Bands, Stochastic Oscillator
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def calculate_sma(data: pd.Series, period: int = 20) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA)

    Args:
        data: Price series (typically close prices)
        period: Number of periods for the moving average

    Returns:
        Series with SMA values
    """
    if len(data) < period:
        logger.warning(f"Not enough data for SMA calculation. Need {period}, got {len(data)}")
        return pd.Series([np.nan] * len(data), index=data.index)

    return data.rolling(window=period).mean()


def calculate_ema(data: pd.Series, period: int = 20) -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA)

    Args:
        data: Price series (typically close prices)
        period: Number of periods for the moving average

    Returns:
        Series with EMA values
    """
    if len(data) < period:
        logger.warning(f"Not enough data for EMA calculation. Need {period}, got {len(data)}")
        return pd.Series([np.nan] * len(data), index=data.index)

    return data.ewm(span=period, adjust=False).mean()


def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI)

    RSI = 100 - (100 / (1 + RS))
    where RS = Average Gain / Average Loss

    Args:
        data: Price series (typically close prices)
        period: RSI period (default: 14)

    Returns:
        Series with RSI values (0-100)
    """
    if len(data) < period + 1:
        logger.warning(f"Not enough data for RSI calculation. Need {period + 1}, got {len(data)}")
        return pd.Series([np.nan] * len(data), index=data.index)

    # Calculate price changes
    delta = data.diff()

    # Separate gains and losses
    gains = delta.where(delta > 0, 0.0)
    losses = -delta.where(delta < 0, 0.0)

    # Calculate average gains and losses using exponential moving average
    avg_gains = gains.ewm(span=period, adjust=False).mean()
    avg_losses = losses.ewm(span=period, adjust=False).mean()

    # Calculate RS and RSI
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_macd(
    data: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence)

    MACD Line = EMA(12) - EMA(26)
    Signal Line = EMA(9) of MACD Line
    Histogram = MACD Line - Signal Line

    Args:
        data: Price series (typically close prices)
        fast_period: Fast EMA period (default: 12)
        slow_period: Slow EMA period (default: 26)
        signal_period: Signal line period (default: 9)

    Returns:
        Tuple of (MACD line, Signal line, Histogram)
    """
    if len(data) < slow_period:
        logger.warning(f"Not enough data for MACD calculation. Need {slow_period}, got {len(data)}")
        empty_series = pd.Series([np.nan] * len(data), index=data.index)
        return empty_series, empty_series, empty_series

    # Calculate EMAs
    ema_fast = calculate_ema(data, fast_period)
    ema_slow = calculate_ema(data, slow_period)

    # MACD Line
    macd_line = ema_fast - ema_slow

    # Signal Line
    signal_line = calculate_ema(macd_line, signal_period)

    # Histogram
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def calculate_bollinger_bands(
    data: pd.Series,
    period: int = 20,
    std_dev: float = 2.0
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Bollinger Bands

    Middle Band = SMA(20)
    Upper Band = SMA(20) + (2 * Standard Deviation)
    Lower Band = SMA(20) - (2 * Standard Deviation)

    Args:
        data: Price series (typically close prices)
        period: SMA period (default: 20)
        std_dev: Number of standard deviations (default: 2)

    Returns:
        Tuple of (Upper Band, Middle Band, Lower Band)
    """
    if len(data) < period:
        logger.warning(f"Not enough data for Bollinger Bands calculation. Need {period}, got {len(data)}")
        empty_series = pd.Series([np.nan] * len(data), index=data.index)
        return empty_series, empty_series, empty_series

    # Calculate middle band (SMA)
    middle_band = calculate_sma(data, period)

    # Calculate standard deviation
    rolling_std = data.rolling(window=period).std()

    # Calculate upper and lower bands
    upper_band = middle_band + (rolling_std * std_dev)
    lower_band = middle_band - (rolling_std * std_dev)

    return upper_band, middle_band, lower_band


def calculate_stochastic(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    k_period: int = 14,
    d_period: int = 3
) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate Stochastic Oscillator

    %K = (Current Close - Lowest Low) / (Highest High - Lowest Low) * 100
    %D = SMA of %K

    Args:
        high: High price series
        low: Low price series
        close: Close price series
        k_period: %K period (default: 14)
        d_period: %D period (default: 3)

    Returns:
        Tuple of (%K, %D)
    """
    if len(close) < k_period:
        logger.warning(f"Not enough data for Stochastic calculation. Need {k_period}, got {len(close)}")
        empty_series = pd.Series([np.nan] * len(close), index=close.index)
        return empty_series, empty_series

    # Calculate %K
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()

    k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))

    # Calculate %D (smoothed %K)
    d_percent = k_percent.rolling(window=d_period).mean()

    return k_percent, d_percent


def calculate_all_indicators(
    df: pd.DataFrame,
    rsi_period: int = 14,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9,
    sma_periods: list = [20, 50, 200],
    ema_periods: list = [12, 26]
) -> pd.DataFrame:
    """
    Calculate all technical indicators for a DataFrame

    Args:
        df: DataFrame with OHLCV data (columns: open, high, low, close, volume)
        rsi_period: RSI period
        macd_fast: MACD fast period
        macd_slow: MACD slow period
        macd_signal: MACD signal period
        sma_periods: List of SMA periods to calculate
        ema_periods: List of EMA periods to calculate

    Returns:
        DataFrame with all indicators added as new columns
    """
    result = df.copy()

    # Validate required columns
    required_cols = ['close']
    if not all(col in df.columns for col in required_cols):
        logger.error(f"DataFrame must contain 'close' column")
        return result

    close_prices = df['close']

    # Calculate RSI
    result['rsi'] = calculate_rsi(close_prices, rsi_period)

    # Calculate MACD
    macd_line, signal_line, histogram = calculate_macd(
        close_prices, macd_fast, macd_slow, macd_signal
    )
    result['macd'] = macd_line
    result['macd_signal'] = signal_line
    result['macd_histogram'] = histogram

    # Calculate SMAs
    for period in sma_periods:
        result[f'sma_{period}'] = calculate_sma(close_prices, period)

    # Calculate EMAs
    for period in ema_periods:
        result[f'ema_{period}'] = calculate_ema(close_prices, period)

    # Calculate Bollinger Bands
    if len(df) >= 20:
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(close_prices)
        result['bb_upper'] = bb_upper
        result['bb_middle'] = bb_middle
        result['bb_lower'] = bb_lower

    # Calculate Stochastic Oscillator (if high/low data available)
    if all(col in df.columns for col in ['high', 'low']):
        k_percent, d_percent = calculate_stochastic(
            df['high'], df['low'], df['close']
        )
        result['stoch_k'] = k_percent
        result['stoch_d'] = d_percent

    logger.info(f"Calculated all indicators for {len(df)} periods")
    return result


def get_trading_signals(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate trading signals based on technical indicators

    Args:
        df: DataFrame with calculated indicators

    Returns:
        Dictionary with buy/sell/hold signals and reasoning
    """
    if len(df) < 2:
        return {
            "signal": "HOLD",
            "confidence": "LOW",
            "reason": "Insufficient data for analysis"
        }

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    signals = []
    score = 0  # Positive = bullish, Negative = bearish

    # RSI Signals
    if 'rsi' in latest and not pd.isna(latest['rsi']):
        if latest['rsi'] < 30:
            signals.append("RSI oversold (< 30) - Bullish signal")
            score += 2
        elif latest['rsi'] > 70:
            signals.append("RSI overbought (> 70) - Bearish signal")
            score -= 2
        elif 40 < latest['rsi'] < 60:
            signals.append("RSI neutral (40-60) - No clear signal")

    # MACD Signals
    if all(k in latest for k in ['macd', 'macd_signal']) and not pd.isna(latest['macd']):
        # MACD crossover
        if previous['macd'] < previous['macd_signal'] and latest['macd'] > latest['macd_signal']:
            signals.append("MACD bullish crossover - Buy signal")
            score += 3
        elif previous['macd'] > previous['macd_signal'] and latest['macd'] < latest['macd_signal']:
            signals.append("MACD bearish crossover - Sell signal")
            score -= 3
        elif latest['macd'] > latest['macd_signal']:
            signals.append("MACD above signal - Bullish")
            score += 1
        else:
            signals.append("MACD below signal - Bearish")
            score -= 1

    # Moving Average Signals
    if all(k in latest for k in ['sma_20', 'sma_50']) and not pd.isna(latest['sma_20']):
        if latest['close'] > latest['sma_20']:
            signals.append("Price above SMA(20) - Bullish")
            score += 1
        else:
            signals.append("Price below SMA(20) - Bearish")
            score -= 1

        if latest['sma_20'] > latest['sma_50']:
            signals.append("SMA(20) > SMA(50) - Uptrend")
            score += 1
        else:
            signals.append("SMA(20) < SMA(50) - Downtrend")
            score -= 1

    # Bollinger Bands Signals
    if all(k in latest for k in ['bb_upper', 'bb_lower']) and not pd.isna(latest['bb_upper']):
        if latest['close'] < latest['bb_lower']:
            signals.append("Price below lower Bollinger Band - Oversold")
            score += 2
        elif latest['close'] > latest['bb_upper']:
            signals.append("Price above upper Bollinger Band - Overbought")
            score -= 2

    # Stochastic Signals
    if all(k in latest for k in ['stoch_k', 'stoch_d']) and not pd.isna(latest['stoch_k']):
        if latest['stoch_k'] < 20:
            signals.append("Stochastic oversold (< 20) - Bullish")
            score += 1
        elif latest['stoch_k'] > 80:
            signals.append("Stochastic overbought (> 80) - Bearish")
            score -= 1

    # Determine overall signal
    if score >= 5:
        signal = "STRONG BUY"
        confidence = "HIGH"
    elif score >= 2:
        signal = "BUY"
        confidence = "MEDIUM"
    elif score <= -5:
        signal = "STRONG SELL"
        confidence = "HIGH"
    elif score <= -2:
        signal = "SELL"
        confidence = "MEDIUM"
    else:
        signal = "HOLD"
        confidence = "LOW"

    return {
        "signal": signal,
        "confidence": confidence,
        "score": score,
        "indicators": signals,
        "latest_values": {
            "rsi": float(latest.get('rsi', np.nan)) if not pd.isna(latest.get('rsi', np.nan)) else None,
            "macd": float(latest.get('macd', np.nan)) if not pd.isna(latest.get('macd', np.nan)) else None,
            "macd_signal": float(latest.get('macd_signal', np.nan)) if not pd.isna(latest.get('macd_signal', np.nan)) else None,
            "price": float(latest.get('close', np.nan)) if not pd.isna(latest.get('close', np.nan)) else None,
            "sma_20": float(latest.get('sma_20', np.nan)) if not pd.isna(latest.get('sma_20', np.nan)) else None,
            "sma_50": float(latest.get('sma_50', np.nan)) if not pd.isna(latest.get('sma_50', np.nan)) else None
        }
    }


def main():
    """Test indicators with sample data"""
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    np.random.seed(42)

    # Generate synthetic price data
    price = 100
    prices = [price]
    for _ in range(99):
        price = price * (1 + np.random.randn() * 0.02)
        prices.append(price)

    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.02 for p in prices],
        'low': [p * 0.98 for p in prices],
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, 100)
    })

    # Calculate indicators
    df_with_indicators = calculate_all_indicators(df)

    # Display results
    print("\n" + "=" * 80)
    print("TECHNICAL INDICATORS TEST")
    print("=" * 80)
    print(f"\nLast 5 periods:")
    print(df_with_indicators[['date', 'close', 'rsi', 'macd', 'macd_signal', 'sma_20', 'sma_50']].tail())

    # Get trading signals
    signals = get_trading_signals(df_with_indicators)
    print("\n" + "=" * 80)
    print("TRADING SIGNALS")
    print("=" * 80)
    print(f"Signal: {signals['signal']}")
    print(f"Confidence: {signals['confidence']}")
    print(f"Score: {signals['score']}")
    print(f"\nIndicator Analysis:")
    for indicator in signals['indicators']:
        print(f"  • {indicator}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
