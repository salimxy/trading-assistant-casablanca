#!/usr/bin/env python3
"""
Populate database with validated Casablanca Stock Exchange tickers.

This script uses only the pre-validated working tickers from constants.py
to avoid wasting time on known-failed tickers.
"""

import time
import logging
import argparse
from typing import Tuple, Optional, Dict, Any
from tqdm import tqdm
from scraper import get_stock_data
from db import init_db, save_stock, save_history
from constants import WORKING_TICKERS, REQUEST_DELAY_SECONDS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_all_tickers.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Use only validated working tickers
TICKERS = WORKING_TICKERS


def test_ticker(ticker: str, delay: float = REQUEST_DELAY_SECONDS) -> Tuple[str, bool, Optional[Dict[str, Any]]]:
    """
    Test if a ticker is accessible.

    Args:
        ticker: Stock ticker
        delay: Delay before request (seconds, default from constants)

    Returns:
        Tuple of (ticker, success, data_or_error_message)
    """
    try:
        time.sleep(delay)
        data = get_stock_data(ticker)

        if data is None:
            return (ticker, False, "No data returned")

        return (ticker, True, data)

    except Exception as e:
        logger.warning(f"Error testing {ticker}: {str(e)}")
        return (ticker, False, str(e))


def test_all(save_to_db: bool = False) -> Tuple[int, int, list, list]:
    """
    Test all tickers with progress bar.

    Args:
        save_to_db: Whether to save working tickers to database

    Returns:
        Tuple of (working_count, failed_count, working_list, failed_list)
    """
    working_tickers = []
    failed_tickers = []

    print("\n" + "=" * 80)
    print("POPULATING DATABASE WITH VALIDATED TICKERS")
    print("=" * 80 + "\n")

    print(f"Total validated tickers: {len(TICKERS)}")
    print(f"Note: Only testing pre-validated working tickers from constants.py\n")

    with tqdm(total=len(TICKERS), desc="Testing tickers", unit="ticker") as pbar:
        for i, ticker in enumerate(TICKERS):
            ticker_norm = ticker.strip().upper()
            test_ticker_symbol, success, data_or_error = test_ticker(
                ticker_norm,
                delay=0.5 if i == 0 else 2.0  # 0.5s for first, 2s for others
            )

            if success:
                working_tickers.append(ticker_norm)
                pbar.set_postfix({"Status": f"✓ {ticker_norm}"})
                logger.info(f"✓ {ticker_norm} - OK")

                # Save to database if requested
                if save_to_db and isinstance(data_or_error, dict):
                    try:
                        save_stock(data_or_error)
                        save_history(ticker_norm, data_or_error)
                    except Exception as e:
                        logger.warning(f"Could not save {ticker_norm} to DB: {e}")
            else:
                failed_tickers.append(ticker_norm)
                pbar.set_postfix({"Status": f"✗ {ticker_norm}"})
                logger.warning(f"✗ {ticker_norm} - FAILED: {data_or_error}")

            pbar.update(1)

    return len(working_tickers), len(failed_tickers), working_tickers, failed_tickers


def save_working_tickers(tickers: list) -> None:
    """Save list of working tickers to file"""
    with open('working_tickers.txt', 'w') as f:
        f.write(f"# Casablanca Stock Exchange - Working Tickers\n")
        f.write(f"# Total: {len(tickers)}\n")
        f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for ticker in sorted(tickers):
            f.write(f"{ticker}\n")

    logger.info(f"✓ Saved {len(tickers)} working tickers to working_tickers.txt")


def save_failed_tickers(tickers: list) -> None:
    """Save list of failed tickers to file"""
    with open('failed_tickers.txt', 'w') as f:
        f.write(f"# Casablanca Stock Exchange - Failed Tickers\n")
        f.write(f"# Total: {len(tickers)}\n")
        f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for ticker in sorted(tickers):
            f.write(f"{ticker}\n")

    logger.info(f"✓ Saved {len(tickers)} failed tickers to failed_tickers.txt")


def main():
    parser = argparse.ArgumentParser(
        description='Populate database with validated Casablanca Stock Exchange tickers'
    )
    parser.add_argument(
        '--save',
        action='store_true',
        help='Save tickers to database (required for first-time setup)'
    )
    args = parser.parse_args()

    # Initialize database if saving
    if args.save:
        init_db()

    # Test all tickers
    working_count, failed_count, working_list, failed_list = test_all(save_to_db=args.save)

    # Save results to files
    save_working_tickers(working_list)
    save_failed_tickers(failed_list)

    # Display summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total tickers tested: {len(TICKERS)}")
    print(f"✓ Working: {working_count}")
    print(f"✗ Failed: {failed_count}")
    print(f"Success rate: {(working_count / len(TICKERS) * 100):.1f}%")
    print()

    # Display working tickers
    print("=" * 80)
    print("WORKING TICKERS")
    print("=" * 80)
    if working_list:
        # Display in columns
        cols = 5
        for i in range(0, len(working_list), cols):
            row = working_list[i:i+cols]
            print("  " + "  ".join(f"{t:8}" for t in row))
    else:
        print("  No working tickers found")

    print()

    # Display failed tickers
    if failed_list:
        print("=" * 80)
        print("FAILED TICKERS")
        print("=" * 80)
        cols = 5
        for i in range(0, len(failed_list), cols):
            row = failed_list[i:i+cols]
            print("  " + "  ".join(f"{t:8}" for t in row))
    else:
        print("=" * 80)
        print("✓ All tickers are accessible!")
        print("=" * 80)

    print()
    print(f"Results saved to:")
    print(f"  - working_tickers.txt ({working_count} tickers)")
    print(f"  - failed_tickers.txt ({failed_count} tickers)")
    print(f"  - test_all_tickers.log (detailed log)")

    if args.save and working_count > 0:
        print(f"  - stocks.db (database with {working_count} stocks)")

    print()


if __name__ == "__main__":
    main()
