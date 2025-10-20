from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
import pandas as pd
from typing import Optional, Dict, Any
import pytz

# Database configuration
DATABASE_URL = "sqlite:///stocks.db"
Base = declarative_base()

# Models
class Stock(Base):
    """Current stock data"""
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    ticker = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    price = Column(Float)
    change_pct = Column(Float)
    volume = Column(Float)
    timestamp = Column(DateTime, default=lambda: datetime.now(pytz.UTC), index=True)

    def __repr__(self):
        return f"<Stock {self.ticker} @ {self.price} MAD>"


class StockHistory(Base):
    """Historical stock data"""
    __tablename__ = "history"

    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

    __table_args__ = (
        Index('idx_ticker_date', 'ticker', 'date'),
    )

    def __repr__(self):
        return f"<StockHistory {self.ticker} {self.date}>"


# Initialize database engine
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables if they don't exist"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized")


def get_db():
    """Get database session"""
    return SessionLocal()


def save_stock(data_dict: Dict[str, Any]) -> Stock:
    """
    Insert or update stock data.

    Args:
        data_dict: Dictionary with stock data (ticker, name, current_price, etc.)

    Returns:
        Stock object
    """
    db = get_db()
    try:
        ticker = data_dict.get('ticker')

        if not ticker:
            raise ValueError("Ticker is required")

        # Check if stock exists
        existing = db.query(Stock).filter(Stock.ticker == ticker).first()

        if existing:
            # Update existing
            existing.name = data_dict.get('name')
            existing.price = data_dict.get('current_price')
            existing.change_pct = data_dict.get('variation_percent')
            existing.volume = data_dict.get('volume')
            existing.timestamp = datetime.now(pytz.UTC)
            db.commit()
            print(f"✓ Updated {ticker}")
            return existing
        else:
            # Create new
            stock = Stock(
                ticker=ticker,
                name=data_dict.get('name'),
                price=data_dict.get('current_price'),
                change_pct=data_dict.get('variation_percent'),
                volume=data_dict.get('volume'),
                timestamp=datetime.now(pytz.UTC)
            )
            db.add(stock)
            db.commit()
            print(f"✓ Created {ticker}")
            return stock
    finally:
        db.close()


def save_history(ticker: str, data_dict: Dict[str, Any], date: Optional[datetime] = None) -> StockHistory:
    """
    Save historical stock data.

    Args:
        ticker: Stock ticker
        data_dict: Dictionary with OHLCV data (opening_price, high_price, low_price, current_price, volume)
        date: Date of the record (default: today UTC)

    Returns:
        StockHistory object
    """
    db = get_db()
    try:
        if date is None:
            date = datetime.now(pytz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # Ensure date is timezone aware
            if date.tzinfo is None:
                date = pytz.UTC.localize(date)

        history = StockHistory(
            ticker=ticker,
            date=date,
            open=data_dict.get('opening_price'),
            high=data_dict.get('high_price'),
            low=data_dict.get('low_price'),
            close=data_dict.get('current_price'),
            volume=data_dict.get('volume')
        )
        db.add(history)
        db.commit()
        print(f"✓ Saved history for {ticker}")
        return history
    finally:
        db.close()


def get_latest(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Get latest stock data.

    Args:
        ticker: Stock ticker

    Returns:
        Dictionary with stock data or None
    """
    db = get_db()
    try:
        stock = db.query(Stock).filter(Stock.ticker == ticker).first()

        if not stock:
            return None

        return {
            'ticker': stock.ticker,
            'name': stock.name,
            'price': stock.price,
            'change_pct': stock.change_pct,
            'volume': stock.volume,
            'timestamp': stock.timestamp
        }
    finally:
        db.close()


def get_history(ticker: str, days: int = 30) -> pd.DataFrame:
    """
    Get historical stock data as DataFrame.

    Args:
        ticker: Stock ticker
        days: Number of days to retrieve (default: 30)

    Returns:
        Pandas DataFrame with columns: date, open, high, low, close, volume
    """
    db = get_db()
    try:
        cutoff_date = datetime.now(pytz.UTC) - timedelta(days=days)

        records = db.query(StockHistory).filter(
            StockHistory.ticker == ticker,
            StockHistory.date >= cutoff_date
        ).order_by(StockHistory.date.asc()).all()

        if not records:
            return pd.DataFrame()

        data = [
            {
                'date': record.date,
                'open': record.open,
                'high': record.high,
                'low': record.low,
                'close': record.close,
                'volume': record.volume
            }
            for record in records
        ]

        df = pd.DataFrame(data)
        return df
    finally:
        db.close()


def get_all_stocks() -> pd.DataFrame:
    """Get all current stocks as DataFrame"""
    db = get_db()
    try:
        stocks = db.query(Stock).all()

        if not stocks:
            return pd.DataFrame()

        data = [
            {
                'ticker': s.ticker,
                'name': s.name,
                'price': s.price,
                'change_pct': s.change_pct,
                'volume': s.volume,
                'timestamp': s.timestamp
            }
            for s in stocks
        ]

        return pd.DataFrame(data)
    finally:
        db.close()


def delete_stock(ticker: str) -> bool:
    """Delete a stock record"""
    db = get_db()
    try:
        db.query(Stock).filter(Stock.ticker == ticker).delete()
        db.commit()
        return True
    finally:
        db.close()
