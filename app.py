"""
Trading Assistant MVP - Streamlit Dashboard

Interface web interactive pour visualiser les recommandations de trading
et les indicateurs techniques de la Bourse de Casablanca.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_all_stocks, get_latest, get_history
from scoring import analyze_stock
from indicators import calculate_indicators
from constants import WORKING_TICKERS

# Page configuration
st.set_page_config(
    page_title="Trading Assistant - Bourse de Casablanca",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .buy-signal {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
    }
    .sell-signal {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
    }
    .hold-signal {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def get_signal_color(signal):
    """Get color for signal"""
    if signal in ['STRONG BUY', 'BUY']:
        return '#28a745'
    elif signal in ['STRONG SELL', 'SELL']:
        return '#dc3545'
    else:
        return '#ffc107'

def get_signal_class(signal):
    """Get CSS class for signal"""
    if signal in ['STRONG BUY', 'BUY']:
        return 'buy-signal'
    elif signal in ['STRONG SELL', 'SELL']:
        return 'sell-signal'
    else:
        return 'hold-signal'

def plot_price_chart(ticker, days=30):
    """Plot price chart with technical indicators"""
    history = get_history(ticker, days=days)

    if history.empty:
        st.warning(f"Pas de données historiques pour {ticker}")
        return

    # Calculate indicators
    indicators = calculate_indicators(ticker, days=days)

    if not indicators:
        st.warning(f"Impossible de calculer les indicateurs pour {ticker}")
        return

    # Create candlestick chart
    fig = go.Figure()

    # Add candlestick
    fig.add_trace(go.Candlestick(
        x=history['date'],
        open=history['open'],
        high=history['high'],
        low=history['low'],
        close=history['close'],
        name='Prix'
    ))

    # Add SMA if available
    if indicators.get('sma_20'):
        dates = history['date'].tolist()
        sma_values = [indicators['sma_20']] * len(dates)
        fig.add_trace(go.Scatter(
            x=dates,
            y=sma_values,
            name='SMA 20',
            line=dict(color='orange', width=2)
        ))

    fig.update_layout(
        title=f"{ticker} - Évolution du prix",
        yaxis_title="Prix (MAD)",
        xaxis_title="Date",
        template="plotly_white",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_volume_chart(ticker, days=30):
    """Plot volume chart"""
    history = get_history(ticker, days=days)

    if history.empty:
        return

    fig = px.bar(
        history,
        x='date',
        y='volume',
        title=f"{ticker} - Volume d'échanges"
    )

    fig.update_layout(
        yaxis_title="Volume",
        xaxis_title="Date",
        template="plotly_white",
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)

def show_stock_analysis(ticker):
    """Show detailed analysis for a stock"""
    st.header(f"📊 Analyse de {ticker}")

    # Get analysis
    with st.spinner("Analyse en cours..."):
        analysis = analyze_stock(ticker, days=30)

    if not analysis:
        st.error(f"❌ Impossible d'analyser {ticker}. Données insuffisantes (besoin de 30+ jours).")
        return

    # Display main metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Prix actuel", f"{analysis['current_price']:.2f} MAD")

    with col2:
        st.metric("Score", f"{analysis['score']}/100")

    with col3:
        st.metric("Confiance", f"{analysis['confidence']}%")

    with col4:
        st.metric("Points de données", analysis['data_points'])

    # Display signal
    st.markdown(f"""
    <div class="{get_signal_class(analysis['signal'])}">
        <h2>{analysis['signal']}</h2>
        <p>{analysis['signal_description']}</p>
        <p><strong>Action recommandée:</strong> {analysis['action']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Two columns for charts and details
    col_left, col_right = st.columns([2, 1])

    with col_left:
        # Price chart
        plot_price_chart(ticker, days=30)

        # Volume chart
        plot_volume_chart(ticker, days=30)

    with col_right:
        # Technical indicators
        st.subheader("📈 Indicateurs Techniques")

        indicators = analysis['indicators']

        if indicators['rsi']:
            st.metric("RSI (14)", f"{indicators['rsi']:.2f}")

        if indicators['sma_20']:
            st.metric("SMA (20)", f"{indicators['sma_20']:.2f} MAD")

        if indicators['trend']:
            trend_emoji = "🟢" if indicators['trend'] == 'bullish' else "🔴" if indicators['trend'] == 'bearish' else "🟡"
            st.metric("Tendance", f"{trend_emoji} {indicators['trend'].upper()}")

        if indicators['volume_ratio']:
            st.metric("Volume Ratio", f"{indicators['volume_ratio']:.2f}x")

        # Score breakdown
        st.subheader("🔍 Détails du Score")
        for item in analysis['breakdown']:
            st.text(f"• {item}")

        # Justification
        st.subheader("💡 Justification")
        for justif in analysis['justification']:
            st.info(justif)

def show_market_overview():
    """Show market overview"""
    st.header("🌍 Vue d'ensemble du marché")

    # Note about mock data
    st.info("ℹ️ **Note:** Utilisation de données simulées (API bloquée - Geo-blocking détecté)")

    # Get all stocks
    all_stocks = get_all_stocks()

    if all_stocks.empty:
        st.warning("Aucune donnée disponible. Veuillez d'abord peupler la base de données.")
        st.code("python3 test_scoring.py  # Pour créer des données de test")
        return

    # Display stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Actions", len(all_stocks))

    with col2:
        avg_change = all_stocks['change_pct'].mean() if 'change_pct' in all_stocks.columns else 0
        st.metric("Variation Moyenne", f"{avg_change:.2f}%")

    with col3:
        total_volume = all_stocks['volume'].sum() if 'volume' in all_stocks.columns else 0
        st.metric("Volume Total", f"{total_volume/1e6:.1f}M MAD")

    # Show top movers
    st.subheader("📊 Top Movers")

    col_gain, col_loss = st.columns(2)

    with col_gain:
        st.markdown("### 🟢 Top Gagnants")
        if 'change_pct' in all_stocks.columns:
            top_gainers = all_stocks.nlargest(5, 'change_pct')[['ticker', 'name', 'price', 'change_pct']]
            st.dataframe(top_gainers, hide_index=True, use_container_width=True)

    with col_loss:
        st.markdown("### 🔴 Top Perdants")
        if 'change_pct' in all_stocks.columns:
            top_losers = all_stocks.nsmallest(5, 'change_pct')[['ticker', 'name', 'price', 'change_pct']]
            st.dataframe(top_losers, hide_index=True, use_container_width=True)

    # All stocks table
    st.subheader("📋 Toutes les Actions")
    st.dataframe(all_stocks, hide_index=True, use_container_width=True)

def main():
    """Main application"""

    # Sidebar
    st.sidebar.title("📊 Trading Assistant")
    st.sidebar.markdown("**Bourse de Casablanca**")
    st.sidebar.markdown("---")

    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Vue d'ensemble", "🔍 Analyser une action", "ℹ️ À propos"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Configuration")

    # Settings
    analysis_days = st.sidebar.slider(
        "Période d'analyse (jours)",
        min_value=7,
        max_value=90,
        value=30,
        step=1
    )

    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Version:** 1.1.0
    **Tickers:** 60 validés
    **Endpoints:** 9
    **Scoring:** ✅ Actif
    """)

    # Main content
    if page == "🏠 Vue d'ensemble":
        show_market_overview()

    elif page == "🔍 Analyser une action":
        st.header("🔍 Analyse Technique")

        # Ticker selection
        all_stocks = get_all_stocks()

        if not all_stocks.empty:
            available_tickers = all_stocks['ticker'].tolist()
        else:
            available_tickers = ['VCN', 'ATW', 'BCP']  # Default test tickers

        ticker = st.selectbox(
            "Sélectionnez une action",
            options=available_tickers,
            index=0
        )

        if st.button("🚀 Analyser", type="primary"):
            show_stock_analysis(ticker)

    elif page == "ℹ️ À propos":
        st.header("ℹ️ À propos")

        st.markdown("""
        ## Trading Assistant - Bourse de Casablanca

        Outil d'analyse automatisé avec scoring technique et recommandations d'achat/vente.

        ### 📊 Système de Scoring (0-100)

        - **RSI optimal 40-60:** +30pts
        - **MACD positif:** +20pts
        - **Prix > SMA_20:** +20pts
        - **Volume > moyenne:** +15pts
        - **Tendance haussière:** +15pts

        ### 🎯 Signaux Générés

        - **80-100:** STRONG BUY 🟢
        - **60-79:** BUY 🟢
        - **40-59:** HOLD 🟡
        - **20-39:** SELL 🔴
        - **0-19:** STRONG SELL 🔴

        ### 📈 Indicateurs Techniques

        - RSI (Relative Strength Index)
        - MACD (Moving Average Convergence Divergence)
        - SMA/EMA (Simple/Exponential Moving Averages)
        - Analyse de volume
        - Détection de tendance

        ### ⚠️ Avertissement

        **API Casablanca Bourse:** Actuellement bloquée (geo-blocking détecté)
        **Données:** Simulées pour démonstration
        **Production:** Nécessite IP marocaine ou API officielle

        ### 🔧 Stack Technique

        - **Backend:** Python 3.11+ / FastAPI
        - **Base de données:** SQLite
        - **Analyse:** Pandas, NumPy
        - **Interface:** Streamlit
        - **API:** 9 endpoints REST

        ### 📞 Support

        Pour questions ou problèmes:
        - Consulter la documentation (README.md)
        - Vérifier les logs
        - Tester avec l'API Swagger (/docs)

        ---

        **Version:** 1.1.0
        **Dernière mise à jour:** 21 Octobre 2025
        **Tickers validés:** 60
        """)

if __name__ == "__main__":
    main()
