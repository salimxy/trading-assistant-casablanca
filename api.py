#!/usr/bin/env python3
"""FastAPI backend for Casablanca Stock Exchange data"""

import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
import pytz
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from db import init_db, get_latest, get_history, get_all_stocks
from indicators import calculate_all_indicators, get_trading_signals

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")

# Create FastAPI app
app = FastAPI(
    title="Casablanca Stock Exchange API",
    description="API for accessing real-time and historical stock data from Casablanca Bourse",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track start time for uptime
start_time = datetime.now(pytz.UTC)


def sanitize_for_json(obj: Any) -> Any:
    """Convert pandas/numpy types to JSON-serializable types"""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif pd.isna(obj):
        return None
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat() if hasattr(obj, 'isoformat') else str(obj)
    return obj


def success_response(data: Any, ticker: Optional[str] = None) -> Dict[str, Any]:
    """Create a standard success response"""
    response = {
        "success": True,
        "data": sanitize_for_json(data),
        "timestamp": datetime.now(pytz.UTC).isoformat()
    }
    if ticker:
        response["ticker"] = ticker
    return response


def error_response(message: str, status_code: int = 500) -> Dict[str, Any]:
    """Create a standard error response"""
    return {
        "success": False,
        "error": message,
        "timestamp": datetime.now(pytz.UTC).isoformat()
    }


@app.get("/health", tags=["System"])
async def health():
    """
    Check API health and database status

    Returns:
        - status: API status
        - uptime: API uptime in seconds
        - stocks_count: Number of stocks in database
        - timestamp: Current timestamp
    """
    try:
        uptime_seconds = (datetime.now(pytz.UTC) - start_time).total_seconds()

        # Get stocks count
        all_stocks = get_all_stocks()
        stocks_count = len(all_stocks) if not all_stocks.empty else 0

        return success_response({
            "status": "healthy",
            "uptime_seconds": uptime_seconds,
            "stocks_in_database": stocks_count,
            "version": "1.0.0"
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error"
        )


@app.get("/stocks/list", tags=["Stocks"])
async def list_stocks():
    """
    Get all available stocks with current prices

    Returns:
        List of stocks with: ticker, name, price, change_pct, volume, timestamp
    """
    try:
        logger.info("Fetching all stocks")
        df = get_all_stocks()

        if df.empty:
            logger.warning("No stocks found in database")
            return success_response([])

        # Convert DataFrame to list of dicts
        stocks = df.to_dict('records')

        # Convert timestamps to ISO format strings
        for stock in stocks:
            if 'timestamp' in stock and isinstance(stock['timestamp'], pd.Timestamp):
                stock['timestamp'] = stock['timestamp'].isoformat()

        logger.info(f"Returned {len(stocks)} stocks")
        return success_response({
            "total": len(stocks),
            "stocks": stocks
        })
    except Exception as e:
        logger.error(f"Error fetching stocks list: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error"
        )


@app.get("/stocks/{ticker}", tags=["Stocks"])
async def get_stock(ticker: str):
    """
    Get latest data for a specific stock

    Args:
        ticker: Stock ticker symbol (e.g., VCN, ATW, BCP)

    Returns:
        Latest stock data: ticker, name, price, change_pct, volume, timestamp

    Raises:
        404: Ticker not found
    """
    try:
        ticker_upper = ticker.upper().strip()
        logger.info(f"Fetching data for ticker: {ticker_upper}")

        stock_data = get_latest(ticker_upper)

        if not stock_data:
            logger.warning(f"Ticker not found: {ticker_upper}")
            raise HTTPException(
                status_code=404,
                detail=f"Ticker '{ticker_upper}' not found"
            )

        # Convert timestamp to ISO format if it's a Timestamp object
        if 'timestamp' in stock_data and isinstance(stock_data['timestamp'], pd.Timestamp):
            stock_data['timestamp'] = stock_data['timestamp'].isoformat()

        logger.info(f"Successfully retrieved data for {ticker_upper}")
        return success_response(stock_data, ticker=ticker_upper)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error"
        )


@app.get("/stocks/{ticker}/history", tags=["Stocks"])
async def get_stock_history(
    ticker: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of history (1-365)")
):
    """
    Get historical data for a specific stock

    Args:
        ticker: Stock ticker symbol
        days: Number of days of history to retrieve (default: 30)

    Returns:
        List of daily records with: date, open, high, low, close, volume

    Raises:
        404: Ticker not found
        400: Invalid days parameter
    """
    try:
        ticker_upper = ticker.upper().strip()
        logger.info(f"Fetching {days}-day history for ticker: {ticker_upper}")

        df = get_history(ticker_upper, days=days)

        if df.empty:
            logger.warning(f"No history found for ticker: {ticker_upper}")
            raise HTTPException(
                status_code=404,
                detail=f"No history found for ticker '{ticker_upper}'"
            )

        # Convert DataFrame to list of dicts
        history = df.to_dict('records')

        # Convert timestamps to ISO format strings
        for record in history:
            if 'date' in record and isinstance(record['date'], pd.Timestamp):
                record['date'] = record['date'].isoformat()

        logger.info(f"Successfully retrieved {len(history)} history records for {ticker_upper}")
        return success_response({
            "ticker": ticker_upper,
            "days": days,
            "records": len(history),
            "history": history
        }, ticker=ticker_upper)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching history for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error"
        )


@app.get("/stats", tags=["Analytics"])
async def get_stats():
    """
    Get market statistics

    Returns:
        - total_stocks: Number of stocks in database
        - top_gainers: Top 5 stocks by percentage change
        - top_losers: Top 5 stocks by percentage change (negative)
    """
    try:
        logger.info("Fetching market statistics")
        df = get_all_stocks()

        if df.empty:
            return success_response({
                "total_stocks": 0,
                "top_gainers": [],
                "top_losers": []
            })

        # Calculate stats
        total_stocks = len(df)

        # Top gainers (assuming change_pct column)
        if 'change_pct' in df.columns:
            top_gainers = df.nlargest(5, 'change_pct')[
                ['ticker', 'name', 'price', 'change_pct']
            ].to_dict('records')

            top_losers = df.nsmallest(5, 'change_pct')[
                ['ticker', 'name', 'price', 'change_pct']
            ].to_dict('records')
        else:
            top_gainers = []
            top_losers = []

        logger.info("Successfully calculated market statistics")
        return success_response({
            "total_stocks": total_stocks,
            "top_gainers": top_gainers,
            "top_losers": top_losers
        })
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error"
        )


@app.get("/stocks/search/{query}", tags=["Stocks"])
async def search_stocks(query: str):
    """
    Search stocks by ticker or company name

    Args:
        query: Search query (ticker or company name)

    Returns:
        List of matching stocks
    """
    try:
        query_upper = query.upper().strip()
        logger.info(f"Searching stocks with query: {query_upper}")

        df = get_all_stocks()

        if df.empty:
            return success_response([])

        # Search in ticker and name columns
        mask = (
            df['ticker'].str.contains(query_upper, case=False, na=False) |
            df['name'].str.contains(query_upper, case=False, na=False)
        )

        results = df[mask].to_dict('records')

        # Convert timestamps to ISO format
        for result in results:
            if 'timestamp' in result and isinstance(result['timestamp'], pd.Timestamp):
                result['timestamp'] = result['timestamp'].isoformat()

        logger.info(f"Found {len(results)} stocks matching '{query_upper}'")
        return success_response({
            "query": query_upper,
            "results": len(results),
            "stocks": results
        })
    except Exception as e:
        logger.error(f"Error searching stocks: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error"
        )


@app.get("/stocks/{ticker}/indicators", tags=["Technical Analysis"])
async def get_stock_indicators(
    ticker: str,
    days: int = Query(30, ge=20, le=365, description="Number of days of history (minimum 20 for indicators)")
):
    """
    Get technical indicators for a specific stock

    Calculates RSI, MACD, SMA, EMA, Bollinger Bands, and Stochastic Oscillator

    Args:
        ticker: Stock ticker symbol
        days: Number of days of history (minimum 20, default: 30)

    Returns:
        DataFrame with all technical indicators

    Raises:
        404: Ticker not found or insufficient data
        400: Invalid days parameter
    """
    try:
        ticker_upper = ticker.upper().strip()
        logger.info(f"Calculating indicators for {ticker_upper} with {days} days")

        # Get historical data
        df = get_history(ticker_upper, days=days)

        if df.empty:
            logger.warning(f"No history found for ticker: {ticker_upper}")
            raise HTTPException(
                status_code=404,
                detail=f"No history found for ticker '{ticker_upper}'"
            )

        if len(df) < 20:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data for indicators. Need at least 20 days, got {len(df)}"
            )

        # Calculate all indicators
        df_with_indicators = calculate_all_indicators(df)

        # Convert to list of records
        records = df_with_indicators.to_dict('records')

        # Convert timestamps and handle NaN values
        for record in records:
            if 'date' in record and isinstance(record['date'], pd.Timestamp):
                record['date'] = record['date'].isoformat()

        logger.info(f"Successfully calculated indicators for {ticker_upper}")
        return success_response({
            "ticker": ticker_upper,
            "days": days,
            "records": len(records),
            "indicators": records
        }, ticker=ticker_upper)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating indicators for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating indicators: {str(e)}"
        )


@app.get("/stocks/{ticker}/signals", tags=["Technical Analysis"])
async def get_stock_signals(
    ticker: str,
    days: int = Query(30, ge=20, le=365, description="Number of days of history (minimum 20)")
):
    """
    Get trading signals based on technical indicators

    Provides BUY/SELL/HOLD recommendations with confidence levels

    Args:
        ticker: Stock ticker symbol
        days: Number of days of history for analysis (default: 30)

    Returns:
        Trading signal with reasoning and current indicator values

    Raises:
        404: Ticker not found or insufficient data
    """
    try:
        ticker_upper = ticker.upper().strip()
        logger.info(f"Generating trading signals for {ticker_upper}")

        # Get historical data
        df = get_history(ticker_upper, days=days)

        if df.empty:
            logger.warning(f"No history found for ticker: {ticker_upper}")
            raise HTTPException(
                status_code=404,
                detail=f"No history found for ticker '{ticker_upper}'"
            )

        if len(df) < 20:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data for analysis. Need at least 20 days, got {len(df)}"
            )

        # Calculate indicators
        df_with_indicators = calculate_all_indicators(df)

        # Generate trading signals
        signals = get_trading_signals(df_with_indicators)

        # Get latest stock data for context
        latest_stock = get_latest(ticker_upper)

        logger.info(f"Generated signal '{signals['signal']}' for {ticker_upper}")
        return success_response({
            "ticker": ticker_upper,
            "current_price": latest_stock.get('price') if latest_stock else None,
            "signal": signals['signal'],
            "confidence": signals['confidence'],
            "score": signals['score'],
            "analysis": signals['indicators'],
            "current_indicators": signals['latest_values']
        }, ticker=ticker_upper)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating signals for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating signals: {str(e)}"
        )


@app.get("/", tags=["System"])
async def root():
    """API root endpoint with documentation links"""
    return {
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
            "search": "/stocks/search/{query}",
            "indicators": "/stocks/{ticker}/indicators?days=30",
            "signals": "/stocks/{ticker}/signals?days=30"
        }
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.detail, exc.status_code)
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content=error_response("Internal server error", 500)
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
