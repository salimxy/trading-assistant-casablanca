#!/usr/bin/env python3
"""
API 403 Diagnostic Tool
Identifies why Casablanca Bourse API returns 403 Forbidden
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import urllib3
from datetime import datetime
from constants import CURRENT_BUILD_ID

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Test configuration
TEST_TICKER = "VCN"
BASE_URL = f"https://www.casablanca-bourse.com/_next/data/{CURRENT_BUILD_ID}/fr/live-market/instruments/{TEST_TICKER}.json"
PARAMS = {
    'slug': ['live-market', 'instruments', TEST_TICKER]
}

def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_endpoint(headers=None, description="Default"):
    """Test endpoint with specific headers"""
    print(f"\n{'─' * 80}")
    print(f"Test: {description}")
    print(f"{'─' * 80}")

    try:
        response = requests.get(
            BASE_URL,
            params=PARAMS,
            headers=headers,
            timeout=10,
            verify=False,
            allow_redirects=True
        )

        print(f"Status Code: {response.status_code}")
        print(f"Final URL: {response.url}")

        # Show response headers
        print("\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")

        # Show response body (first 500 chars)
        print("\nResponse Body Preview:")
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
                print(json.dumps(data, indent=2)[:500])
            else:
                print(response.text[:500])
        except:
            print(response.text[:500])

        return {
            'status': response.status_code,
            'headers': dict(response.headers),
            'url': response.url,
            'body_preview': response.text[:200]
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'status': 'ERROR',
            'error': str(e)
        }

def diagnose():
    """Run comprehensive API diagnosis"""

    print_section("CASABLANCA BOURSE API - 403 DIAGNOSTIC TOOL")
    print(f"Timestamp: {datetime.now()}")
    print(f"Test Endpoint: {BASE_URL}")
    print(f"Build ID: {CURRENT_BUILD_ID}")

    results = []

    # Test 1: No headers (minimal request)
    print_section("TEST 1: Minimal Request (No Custom Headers)")
    result1 = test_endpoint(headers=None, description="No headers")
    results.append(('No headers', result1))

    # Test 2: Chrome User-Agent
    print_section("TEST 2: Chrome User-Agent")
    chrome_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    result2 = test_endpoint(headers=chrome_headers, description="Chrome User-Agent")
    results.append(('Chrome UA', result2))

    # Test 3: Firefox User-Agent
    print_section("TEST 3: Firefox User-Agent")
    firefox_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
    }
    result3 = test_endpoint(headers=firefox_headers, description="Firefox User-Agent")
    results.append(('Firefox UA', result3))

    # Test 4: With Referer
    print_section("TEST 4: With Referer Header")
    referer_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': f'https://www.casablanca-bourse.com/fr/live-market/instruments/{TEST_TICKER}',
        'Accept': 'application/json',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br'
    }
    result4 = test_endpoint(headers=referer_headers, description="Full browser headers with Referer")
    results.append(('With Referer', result4))

    # Test 5: Full browser simulation
    print_section("TEST 5: Full Browser Simulation")
    browser_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.casablanca-bourse.com/',
        'Origin': 'https://www.casablanca-bourse.com',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    result5 = test_endpoint(headers=browser_headers, description="Full browser simulation")
    results.append(('Full Browser', result5))

    # Test 6: Try the main page endpoint (without _next/data)
    print_section("TEST 6: Direct Page Access (No API)")
    try:
        page_url = f"https://www.casablanca-bourse.com/fr/live-market/instruments/{TEST_TICKER}"
        response = requests.get(page_url, headers=browser_headers, timeout=10, verify=False)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content Length: {len(response.text)}")
        results.append(('Direct page', {'status': response.status_code, 'headers': dict(response.headers)}))
    except Exception as e:
        print(f"Error: {e}")
        results.append(('Direct page', {'status': 'ERROR', 'error': str(e)}))

    # Analysis
    print_section("DIAGNOSIS & ANALYSIS")

    statuses = [r[1].get('status') for r in results if r[1].get('status') != 'ERROR']
    all_403 = all(s == 403 for s in statuses if isinstance(s, int))
    any_200 = any(s == 200 for s in statuses if isinstance(s, int))

    diagnosis = {
        'endpoint': BASE_URL,
        'build_id': CURRENT_BUILD_ID,
        'test_results': results,
        'all_403': all_403,
        'any_success': any_200
    }

    print("\nTest Summary:")
    for name, result in results:
        status = result.get('status', 'ERROR')
        print(f"  {name:20s} → {status}")

    print("\n" + "─" * 80)
    print("DIAGNOSIS:")
    print("─" * 80)

    if all_403:
        # Check if it's cloudflare or similar protection
        first_result = results[0][1]
        headers = first_result.get('headers', {})

        if 'cf-ray' in headers or 'cloudflare' in str(headers).lower():
            diagnosis['diagnosis'] = "Cloudflare Protection"
            diagnosis['solution'] = """
Cloudflare is blocking API access:
1. The endpoint is protected by Cloudflare
2. Direct API calls are blocked
3. Need to either:
   - Use Selenium/Playwright with real browser
   - Find alternative data source
   - Contact Bourse de Casablanca for API key
"""
        elif 'server' in headers and 'cloudflare' in headers.get('server', '').lower():
            diagnosis['diagnosis'] = "Cloudflare Protection"
            diagnosis['solution'] = "Cloudflare is protecting the endpoint. Need browser automation or API key."

        else:
            # Check body for clues
            body = first_result.get('body_preview', '')
            if 'access denied' in body.lower() or 'forbidden' in body.lower():
                diagnosis['diagnosis'] = "IP Banned or Geo-Blocked"
                diagnosis['solution'] = """
Possible causes:
1. IP address may be banned/blocked
2. Geographic restriction (only Morocco IPs allowed?)
3. Rate limiting from previous requests
4. Need VPN or proxy from Morocco
"""
            else:
                diagnosis['diagnosis'] = "API Endpoint Changed or Deprecated"
                diagnosis['solution'] = f"""
The API structure may have changed:
1. Build ID '{CURRENT_BUILD_ID}' might be outdated
2. Endpoint structure changed
3. API was deprecated or moved
4. Check website source code for new build ID
5. Try inspecting network traffic in browser dev tools
"""

    elif any_200:
        diagnosis['diagnosis'] = "Headers Fixed Issue"
        successful = [name for name, r in results if r.get('status') == 200]
        diagnosis['solution'] = f"Success with: {', '.join(successful)}. Update scraper to use these headers."

    else:
        diagnosis['diagnosis'] = "Mixed Results - Further Investigation Needed"
        diagnosis['solution'] = "Check individual test results above for patterns."

    print(diagnosis['diagnosis'])
    print(diagnosis['solution'])

    print("\n" + "─" * 80)
    print("RECOMMENDATIONS:")
    print("─" * 80)
    print("""
1. Check browser DevTools (Network tab) on casablanca-bourse.com
2. Verify the current build ID in HTML source
3. Look for alternative data sources (RSS, CSV exports, etc.)
4. Consider using Selenium/Playwright for browser automation
5. Contact Bourse de Casablanca for official API access
""")

    return diagnosis

if __name__ == "__main__":
    diagnosis = diagnose()

    print_section("FINAL DIAGNOSTIC REPORT")
    print(json.dumps({
        'endpoint': diagnosis['endpoint'],
        'build_id': diagnosis['build_id'],
        'diagnosis': diagnosis['diagnosis'],
        'all_403': diagnosis['all_403'],
        'any_success': diagnosis['any_success']
    }, indent=2))
