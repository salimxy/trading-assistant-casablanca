"""
Stock Scoring and Recommendation System

Analyzes stocks using technical indicators and generates buy/sell signals.

Scoring System (0-100):
- RSI optimal 40-60: +30pts
- MACD positive: +20pts
- Price > SMA_20: +20pts
- Volume > average: +15pts
- Bullish trend: +15pts

Signals:
- 80-100: STRONG BUY
- 60-79: BUY
- 40-59: HOLD
- 20-39: SELL
- 0-19: STRONG SELL
"""

import logging
from typing import Dict, Any, Optional, List
from indicators import calculate_indicators
from db import get_latest, get_history

logger = logging.getLogger(__name__)


def calculate_score(indicators: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate technical score based on indicators.

    Args:
        indicators: Dictionary of calculated indicators

    Returns:
        Dictionary with score breakdown
    """
    score = 0
    breakdown = []
    confidence_factors = []

    # RSI Score (0-30 points)
    # Optimal RSI: 40-60 (not oversold, not overbought)
    rsi = indicators.get('rsi')
    if rsi is not None:
        if 40 <= rsi <= 60:
            rsi_score = 30
            breakdown.append(f"RSI optimal ({rsi:.1f}): +30pts")
            confidence_factors.append(1.0)
        elif 30 <= rsi < 40 or 60 < rsi <= 70:
            rsi_score = 20
            breakdown.append(f"RSI acceptable ({rsi:.1f}): +20pts")
            confidence_factors.append(0.7)
        elif 20 <= rsi < 30 or 70 < rsi <= 80:
            rsi_score = 10
            breakdown.append(f"RSI warning ({rsi:.1f}): +10pts")
            confidence_factors.append(0.5)
        else:
            rsi_score = 0
            breakdown.append(f"RSI extreme ({rsi:.1f}): +0pts")
            confidence_factors.append(0.3)
        score += rsi_score
    else:
        breakdown.append("RSI unavailable: +0pts")
        confidence_factors.append(0.5)

    # MACD Score (0-20 points)
    macd_data = indicators.get('macd', {})
    macd_histogram = macd_data.get('histogram')
    if macd_histogram is not None:
        if macd_histogram > 0:
            macd_score = 20
            breakdown.append(f"MACD bullish ({macd_histogram:.4f}): +20pts")
            confidence_factors.append(1.0)
        elif macd_histogram > -0.5:
            macd_score = 10
            breakdown.append(f"MACD neutral ({macd_histogram:.4f}): +10pts")
            confidence_factors.append(0.6)
        else:
            macd_score = 0
            breakdown.append(f"MACD bearish ({macd_histogram:.4f}): +0pts")
            confidence_factors.append(0.4)
        score += macd_score
    else:
        breakdown.append("MACD unavailable: +0pts")
        confidence_factors.append(0.5)

    # Price vs SMA_20 Score (0-20 points)
    current_price = indicators.get('current_price')
    sma_20 = indicators.get('sma_20')
    if current_price and sma_20:
        price_diff_pct = ((current_price - sma_20) / sma_20) * 100
        if current_price > sma_20:
            if price_diff_pct > 5:
                sma_score = 20
                breakdown.append(f"Price >> SMA20 (+{price_diff_pct:.1f}%): +20pts")
                confidence_factors.append(1.0)
            else:
                sma_score = 15
                breakdown.append(f"Price > SMA20 (+{price_diff_pct:.1f}%): +15pts")
                confidence_factors.append(0.8)
            score += sma_score
        else:
            breakdown.append(f"Price < SMA20 ({price_diff_pct:.1f}%): +0pts")
            confidence_factors.append(0.4)
    else:
        breakdown.append("SMA20 unavailable: +0pts")
        confidence_factors.append(0.5)

    # Volume Score (0-15 points)
    volume_data = indicators.get('volume', {})
    volume_ratio = volume_data.get('volume_ratio')
    if volume_ratio is not None:
        if volume_ratio > 1.5:
            volume_score = 15
            breakdown.append(f"Volume high ({volume_ratio:.2f}x): +15pts")
            confidence_factors.append(1.0)
        elif volume_ratio > 1.0:
            volume_score = 10
            breakdown.append(f"Volume above avg ({volume_ratio:.2f}x): +10pts")
            confidence_factors.append(0.8)
        else:
            volume_score = 0
            breakdown.append(f"Volume below avg ({volume_ratio:.2f}x): +0pts")
            confidence_factors.append(0.6)
        score += volume_score
    else:
        breakdown.append("Volume unavailable: +0pts")
        confidence_factors.append(0.5)

    # Trend Score (0-15 points)
    trend = indicators.get('trend')
    if trend:
        if trend == 'bullish':
            trend_score = 15
            breakdown.append("Trend bullish: +15pts")
            confidence_factors.append(1.0)
        elif trend == 'neutral':
            trend_score = 7
            breakdown.append("Trend neutral: +7pts")
            confidence_factors.append(0.7)
        else:
            trend_score = 0
            breakdown.append("Trend bearish: +0pts")
            confidence_factors.append(0.4)
        score += trend_score
    else:
        breakdown.append("Trend unavailable: +0pts")
        confidence_factors.append(0.5)

    # Calculate confidence (average of all factors)
    confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5

    return {
        'score': score,
        'breakdown': breakdown,
        'confidence': confidence
    }


def generate_signal(score: int) -> Dict[str, str]:
    """
    Generate trading signal based on score.

    Args:
        score: Technical score (0-100)

    Returns:
        Dictionary with signal and description
    """
    if score >= 80:
        return {
            'signal': 'STRONG BUY',
            'description': 'Très fortes conditions techniques positives',
            'action': 'Acheter immédiatement'
        }
    elif score >= 60:
        return {
            'signal': 'BUY',
            'description': 'Bonnes conditions techniques d\'achat',
            'action': 'Acheter'
        }
    elif score >= 40:
        return {
            'signal': 'HOLD',
            'description': 'Conditions techniques neutres',
            'action': 'Conserver position actuelle'
        }
    elif score >= 20:
        return {
            'signal': 'SELL',
            'description': 'Conditions techniques de vente',
            'action': 'Vendre'
        }
    else:
        return {
            'signal': 'STRONG SELL',
            'description': 'Très fortes conditions techniques négatives',
            'action': 'Vendre immédiatement'
        }


def generate_justification(indicators: Dict[str, Any], score_data: Dict[str, Any]) -> List[str]:
    """
    Generate detailed justification for the signal.

    Args:
        indicators: Technical indicators
        score_data: Score breakdown data

    Returns:
        List of justification points
    """
    justifications = []

    # RSI analysis
    rsi = indicators.get('rsi')
    if rsi is not None:
        if rsi < 30:
            justifications.append(f"RSI en zone de survente ({rsi:.1f}) - potentiel rebond")
        elif rsi > 70:
            justifications.append(f"RSI en zone de surachat ({rsi:.1f}) - risque correction")
        elif 40 <= rsi <= 60:
            justifications.append(f"RSI en zone optimale ({rsi:.1f}) - momentum équilibré")

    # MACD analysis
    macd_data = indicators.get('macd', {})
    if macd_data.get('histogram') is not None:
        if macd_data['histogram'] > 0:
            justifications.append("MACD positif - momentum haussier confirmé")
        else:
            justifications.append("MACD négatif - momentum baissier")

    # Price vs SMA
    current_price = indicators.get('current_price')
    sma_20 = indicators.get('sma_20')
    if current_price and sma_20:
        if current_price > sma_20:
            diff_pct = ((current_price - sma_20) / sma_20) * 100
            justifications.append(f"Prix au-dessus SMA20 (+{diff_pct:.1f}%) - tendance haussière")
        else:
            diff_pct = ((sma_20 - current_price) / sma_20) * 100
            justifications.append(f"Prix en-dessous SMA20 (-{diff_pct:.1f}%) - tendance baissière")

    # Volume analysis
    volume_data = indicators.get('volume', {})
    if volume_data.get('above_average'):
        justifications.append(f"Volume supérieur à la moyenne ({volume_data['volume_ratio']:.2f}x) - forte activité")

    # Trend
    trend = indicators.get('trend')
    if trend == 'bullish':
        justifications.append("Tendance générale haussière sur 20 jours")
    elif trend == 'bearish':
        justifications.append("Tendance générale baissière sur 20 jours")

    return justifications


def analyze_stock(ticker: str, days: int = 30) -> Optional[Dict[str, Any]]:
    """
    Analyze stock and generate recommendation.

    Args:
        ticker: Stock ticker symbol
        days: Number of days of historical data (default: 30)

    Returns:
        Dictionary with score, signal, confidence, and justification
    """
    try:
        logger.info(f"Analyzing {ticker} with {days} days of data")

        # Get latest price data
        latest = get_latest(ticker)
        if not latest:
            logger.warning(f"No current data for {ticker}")
            return None

        # Calculate technical indicators
        indicators = calculate_indicators(ticker, days=days)
        if not indicators:
            logger.warning(f"Could not calculate indicators for {ticker}")
            return None

        # Calculate score
        score_data = calculate_score(indicators)
        score = score_data['score']

        # Generate signal
        signal_data = generate_signal(score)

        # Generate justification
        justifications = generate_justification(indicators, score_data)

        # Compile analysis
        analysis = {
            'ticker': ticker,
            'current_price': latest['price'],
            'timestamp': latest.get('timestamp'),
            'score': score,
            'signal': signal_data['signal'],
            'signal_description': signal_data['description'],
            'action': signal_data['action'],
            'confidence': round(score_data['confidence'] * 100, 1),
            'breakdown': score_data['breakdown'],
            'justification': justifications,
            'indicators': {
                'rsi': indicators.get('rsi'),
                'macd_histogram': indicators.get('macd', {}).get('histogram'),
                'sma_20': indicators.get('sma_20'),
                'trend': indicators.get('trend'),
                'volume_ratio': indicators.get('volume', {}).get('volume_ratio')
            },
            'data_points': indicators.get('data_points')
        }

        logger.info(f"Analysis complete for {ticker}: {signal_data['signal']} (score: {score})")

        return analysis

    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}")
        return None


def format_analysis(analysis: Dict[str, Any]) -> str:
    """
    Format analysis for display.

    Args:
        analysis: Analysis results

    Returns:
        Formatted string
    """
    if not analysis:
        return "No analysis available"

    lines = [
        f"",
        f"{'=' * 70}",
        f"ANALYSE TECHNIQUE - {analysis['ticker']}",
        f"{'=' * 70}",
        f"Prix actuel: {analysis['current_price']:.2f} MAD",
        f"",
        f"{'─' * 70}",
        f"SIGNAL: {analysis['signal']} ({analysis['score']}/100)",
        f"{'─' * 70}",
        f"Confiance: {analysis['confidence']}%",
        f"Action recommandée: {analysis['action']}",
        f"Description: {analysis['signal_description']}",
        f"",
        f"{'─' * 70}",
        f"DÉTAILS DU SCORE",
        f"{'─' * 70}",
    ]

    for item in analysis['breakdown']:
        lines.append(f"  • {item}")

    lines.extend([
        f"",
        f"{'─' * 70}",
        f"JUSTIFICATION",
        f"{'─' * 70}",
    ])

    for justif in analysis['justification']:
        lines.append(f"  • {justif}")

    lines.extend([
        f"",
        f"{'─' * 70}",
        f"INDICATEURS TECHNIQUES",
        f"{'─' * 70}",
        f"  RSI (14): {analysis['indicators']['rsi']:.2f}" if analysis['indicators']['rsi'] else "  RSI: N/A",
        f"  MACD Histogram: {analysis['indicators']['macd_histogram']:.4f}" if analysis['indicators']['macd_histogram'] is not None else "  MACD: N/A",
        f"  SMA (20): {analysis['indicators']['sma_20']:.2f} MAD" if analysis['indicators']['sma_20'] else "  SMA20: N/A",
        f"  Tendance: {analysis['indicators']['trend'].upper()}" if analysis['indicators']['trend'] else "  Tendance: N/A",
        f"  Volume Ratio: {analysis['indicators']['volume_ratio']:.2f}x" if analysis['indicators']['volume_ratio'] else "  Volume: N/A",
        f"",
        f"Basé sur {analysis['data_points']} jours de données",
        f"{'=' * 70}",
        f""
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    # Test scoring system
    import sys

    logging.basicConfig(level=logging.INFO)

    test_tickers = ['VCN', 'ATW', 'BCP']

    print("\n" + "=" * 70)
    print("SYSTÈME DE SCORING - TEST")
    print("=" * 70)

    for ticker in test_tickers:
        analysis = analyze_stock(ticker, days=30)

        if analysis:
            print(format_analysis(analysis))
        else:
            print(f"\nCould not analyze {ticker} - insufficient data\n")
