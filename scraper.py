import requests
import logging
import time
import urllib3
from typing import Optional, Dict, Any

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_stock_data(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetch stock data from Casablanca Bourse API.

    Args:
        ticker: Stock ticker symbol (e.g., 'VCN', 'ATW', 'BCP')

    Returns:
        Dictionary with stock data or None if error occurs
    """
    base_url = f"https://www.casablanca-bourse.com/_next/data/uwlP8zo7fj-u9phPebGR5/fr/live-market/instruments/{ticker}.json"
    params = {
        'slug': ['live-market', 'instruments', ticker]
    }

    max_retries = 3
    retry_delay = 1  # Initial delay in seconds

    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching data for {ticker} (attempt {attempt + 1}/{max_retries})")

            response = requests.get(base_url, params=params, timeout=10, verify=False)

            # Handle 404 - invalid ticker
            if response.status_code == 404:
                logger.error(f"Ticker '{ticker}' not found (404)")
                return None

            response.raise_for_status()

            data = response.json()

            # Extract data from pageProps.node
            if 'pageProps' not in data or 'node' not in data['pageProps']:
                logger.error(f"Unexpected JSON structure for {ticker}")
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
        if attempt < max_retries - 1:
            sleep_time = retry_delay * (2 ** attempt)
            logger.info(f"Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)

    logger.error(f"Failed to fetch data for {ticker} after {max_retries} attempts")
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
    """Test the scraper with specified tickers."""
    tickers = ['VCN', 'ATW', 'BCP']

    print("\n" + "=" * 60)
    print("CASABLANCA STOCK EXCHANGE DATA SCRAPER")
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


if __name__ == "__main__":
    main()
