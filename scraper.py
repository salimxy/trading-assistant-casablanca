import requests
import logging
import time
import urllib3
from typing import Optional, Dict, Any
from constants import (
    CURRENT_BUILD_ID,
    REQUEST_DELAY_SECONDS,
    MAX_RETRIES,
    RETRY_BACKOFF_BASE,
    REQUEST_TIMEOUT,
    VERIFY_SSL
)

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API monitoring
class APIMonitor:
    """Monitor API changes and potential issues"""

    @staticmethod
    def check_api_structure(data: dict, ticker: str) -> bool:
        """
        Validate API response structure to detect breaking changes.

        Returns:
            True if structure is valid, False otherwise
        """
        try:
            # Check for expected top-level keys
            if 'pageProps' not in data:
                logger.error(f"API structure changed: 'pageProps' missing for {ticker}")
                return False

            if 'node' not in data['pageProps']:
                logger.error(f"API structure changed: 'node' missing for {ticker}")
                return False

            # Check for expected nested structure
            node = data['pageProps']['node']
            if 'field_vactory_paragraphs' not in node:
                logger.error(f"API structure changed: 'field_vactory_paragraphs' missing for {ticker}")
                return False

            return True
        except Exception as e:
            logger.error(f"API structure validation error for {ticker}: {e}")
            return False

    @staticmethod
    def detect_build_id_change(response_url: str) -> Optional[str]:
        """
        Detect if build ID has changed by inspecting response.

        Returns:
            New build ID if detected, None otherwise
        """
        try:
            # Build ID is in the URL path
            if '/_next/data/' in response_url:
                parts = response_url.split('/_next/data/')
                if len(parts) > 1:
                    build_id = parts[1].split('/')[0]
                    if build_id != CURRENT_BUILD_ID:
                        logger.warning(f"Build ID changed! Old: {CURRENT_BUILD_ID}, New: {build_id}")
                        return build_id
        except Exception as e:
            logger.debug(f"Build ID detection error: {e}")

        return None


def get_stock_data(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetch stock data from Casablanca Bourse API.

    Args:
        ticker: Stock ticker symbol (e.g., 'VCN', 'ATW', 'BCP')

    Returns:
        Dictionary with stock data or None if error occurs
    """
    base_url = f"https://www.casablanca-bourse.com/_next/data/{CURRENT_BUILD_ID}/fr/live-market/instruments/{ticker}.json"
    params = {
        'slug': ['live-market', 'instruments', ticker]
    }

    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Fetching data for {ticker} (attempt {attempt + 1}/{MAX_RETRIES})")

            response = requests.get(base_url, params=params, timeout=REQUEST_TIMEOUT, verify=VERIFY_SSL)

            # Monitor for build ID changes
            new_build_id = APIMonitor.detect_build_id_change(response.url)
            if new_build_id:
                logger.critical(f"⚠️  API BUILD ID CHANGED! Update CURRENT_BUILD_ID in constants.py to: {new_build_id}")

            response.raise_for_status()

            # Handle 404 - invalid ticker
            if response.status_code == 404:
                logger.error(f"Ticker '{ticker}' not found (404)")
                return None

            data = response.json()

            # Validate API structure
            if not APIMonitor.check_api_structure(data, ticker):
                logger.critical(f"⚠️  API STRUCTURE CHANGED for {ticker}! Review API response format.")
                return None

            node = data['pageProps']['node']

            # Find the market data component
            market_data = None
            company_name = None

            for paragraph in node.get('field_vactory_paragraphs', []):
                widget_id = paragraph.get('field_vactory_component', {}).get('widget_id', '')

                # Extract company name from instrument-top component
                if 'instrument-top' in widget_id:
                    widget_data_str = paragraph.get('field_vactory_component', {}).get('widget_data', '{}')
                    import json as json_module
                    widget_data = json_module.loads(widget_data_str)
                    components = widget_data.get('components', [{}])
                    if components:
                        collection_data = components[0].get('collection', {}).get('data', {}).get('data', [])
                        if collection_data:
                            company_name = collection_data[0].get('attributes', {}).get('libelleFR')

                # Extract market data from instrument-data component
                if 'instrument-data' in widget_id:
                    widget_data_str = paragraph.get('field_vactory_component', {}).get('widget_data', '{}')
                    import json as json_module
                    widget_data = json_module.loads(widget_data_str)
                    components = widget_data.get('components', [{}])
                    if components:
                        collection_data = components[0].get('collection', {}).get('data', {}).get('data', [])
                        if collection_data:
                            market_data = collection_data[0].get('attributes', {})
                            break

            if not market_data:
                logger.error(f"Could not find market data for {ticker}")
                return None

            # Extract stock information
            stock_data = {
                'ticker': ticker,
                'name': company_name,
                'current_price': market_data.get('coursCourant'),
                'variation_percent': market_data.get('varVeille'),
                'volume': market_data.get('cumulVolumeEchange'),
                'shares_traded': market_data.get('cumulTitresEchanges'),
                'market_cap': market_data.get('capitalisation'),
                'opening_price': market_data.get('openingPrice'),
                'high_price': market_data.get('highPrice'),
                'low_price': market_data.get('lowPrice'),
                'total_trades': market_data.get('totalTrades'),
                'reference_price': market_data.get('staticReferencePrice')
            }

            logger.info(f"Successfully fetched data for {ticker}")
            return stock_data

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout for {ticker} on attempt {attempt + 1}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request error for {ticker} on attempt {attempt + 1}: {e}")
        except (KeyError, ValueError) as e:
            logger.error(f"Data parsing error for {ticker}: {e}")
            return None

        # Exponential backoff if not the last attempt
        if attempt < MAX_RETRIES - 1:
            sleep_time = RETRY_BACKOFF_BASE * (2 ** attempt)
            logger.info(f"Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)

    logger.error(f"Failed to fetch data for {ticker} after {MAX_RETRIES} attempts")
    return None


def format_stock_data(stock_data: Dict[str, Any]) -> str:
    """Format stock data for display."""
    if not stock_data:
        return "No data available"

    # Format numbers
    def fmt_num(val, decimals=2):
        if val is None:
            return 'N/A'
        try:
            return f"{float(val):,.{decimals}f}"
        except:
            return str(val)

    lines = [
        f"=" * 60,
        f"Ticker: {stock_data.get('ticker', 'N/A')}",
        f"Company: {stock_data.get('name', 'N/A')}",
        f"",
        f"Current Price: {fmt_num(stock_data.get('current_price'))} MAD",
        f"Variation: {fmt_num(stock_data.get('variation_percent'))}%",
        f"Opening Price: {fmt_num(stock_data.get('opening_price'))} MAD",
        f"High: {fmt_num(stock_data.get('high_price'))} MAD",
        f"Low: {fmt_num(stock_data.get('low_price'))} MAD",
        f"Reference Price: {fmt_num(stock_data.get('reference_price'))} MAD",
        f"",
        f"Volume: {fmt_num(stock_data.get('volume'), 0)} MAD",
        f"Shares Traded: {fmt_num(stock_data.get('shares_traded'), 0)}",
        f"Total Trades: {stock_data.get('total_trades', 'N/A')}",
        f"Market Cap: {fmt_num(stock_data.get('market_cap'), 0)} MAD",
        f"=" * 60
    ]
    return "\n".join(lines)


def main():
    """Test the scraper with sample tickers."""
    from constants import WORKING_TICKERS

    # Test with first 3 working tickers
    tickers = WORKING_TICKERS[:3]

    print("\n" + "=" * 60)
    print("CASABLANCA STOCK EXCHANGE DATA SCRAPER")
    print(f"Testing {len(tickers)} sample tickers from {len(WORKING_TICKERS)} validated tickers")
    print("=" * 60 + "\n")

    for ticker in tickers:
        stock_data = get_stock_data(ticker)

        if stock_data:
            print(format_stock_data(stock_data))
        else:
            print(f"=" * 60)
            print(f"Failed to retrieve data for {ticker}")
            print(f"=" * 60)

        print()  # Add blank line between results
        time.sleep(REQUEST_DELAY_SECONDS)  # Rate limiting


if __name__ == "__main__":
    main()
