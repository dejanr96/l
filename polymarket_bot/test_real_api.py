#!/usr/bin/env python3
"""
Test bot with REAL Polymarket API
Attempts to fetch actual market data and find real arbitrage opportunities
"""

import requests
import json
import time
from datetime import datetime

def test_clob_api():
    """Test Polymarket CLOB API"""
    print(f"\n{'='*60}")
    print("Testing REAL Polymarket CLOB API")
    print(f"{'='*60}\n")

    base_url = "https://clob.polymarket.com"

    # Try different endpoints
    endpoints = [
        "/markets",
        "/sampling-markets",
        "/simplified-markets",
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
    }

    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"Trying: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ SUCCESS! Got {len(data) if isinstance(data, list) else 'data'}")

                if isinstance(data, list) and len(data) > 0:
                    print(f"  Sample market: {data[0].get('question', 'N/A')[:60]}...")

                    # Save sample
                    with open('real_markets_sample.json', 'w') as f:
                        json.dump(data[:5], f, indent=2)
                    print(f"  💾 Saved sample to real_markets_sample.json")

                return data

            else:
                print(f"  ✗ Failed: {response.text[:100]}")

        except Exception as e:
            print(f"  ✗ Error: {e}")

    return None

def test_gamma_api():
    """Test Polymarket Gamma API"""
    print(f"\n{'='*60}")
    print("Testing REAL Polymarket Gamma API")
    print(f"{'='*60}\n")

    base_url = "https://gamma-api.polymarket.com"

    endpoints = [
        "/markets?limit=20&active=true",
        "/events?limit=10",
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
    }

    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"Trying: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ SUCCESS!")
                print(f"  Data type: {type(data)}")

                if isinstance(data, list):
                    print(f"  Markets: {len(data)}")
                elif isinstance(data, dict):
                    print(f"  Keys: {list(data.keys())}")

                return data

            else:
                print(f"  ✗ Failed")

        except Exception as e:
            print(f"  ✗ Error: {e}")

    return None

def find_crypto_hourly_markets(markets):
    """Filter for crypto hourly markets"""
    if not markets:
        return []

    crypto_hourly = []
    crypto_tokens = ['Bitcoin', 'Ethereum', 'Solana', 'XRP', 'BTC', 'ETH', 'SOL']

    for market in markets:
        question = market.get('question', '')

        # Check if crypto
        is_crypto = any(token.lower() in question.lower() for token in crypto_tokens)

        # Check if hourly
        is_hourly = any(time in question for time in ['AM ET', 'PM ET', 'am et', 'pm et'])

        # Check if up/down
        is_updown = 'up or down' in question.lower()

        if is_crypto and (is_hourly or is_updown):
            crypto_hourly.append(market)

    return crypto_hourly

def scan_for_arbitrage(markets):
    """Scan markets for arbitrage opportunities"""
    print(f"\n{'='*60}")
    print("SCANNING FOR ARBITRAGE OPPORTUNITIES")
    print(f"{'='*60}\n")

    if not markets:
        print("No markets to scan")
        return []

    print(f"Scanning {len(markets)} markets...")

    opportunities = []

    for market in markets:
        market_id = market.get('id') or market.get('condition_id')
        question = market.get('question', 'Unknown')

        # Try to get prices
        outcomes = market.get('outcomes', [])
        tokens = market.get('tokens', [])

        # Different API formats
        if outcomes and len(outcomes) >= 2:
            # Format 1: outcomes with prices
            yes_price = float(outcomes[0].get('price', 0.5))
            no_price = float(outcomes[1].get('price', 0.5))

        elif tokens and len(tokens) >= 2:
            # Format 2: tokens with prices
            yes_price = float(tokens[0].get('price', 0.5))
            no_price = float(tokens[1].get('price', 0.5))

        else:
            # Try other fields
            yes_price = float(market.get('bestBid', 0.5))
            no_price = 1.0 - yes_price

        # Calculate arbitrage
        total_cost = yes_price + no_price
        profit = 1.0 - total_cost
        profit_pct = (profit / total_cost * 100) if total_cost > 0 else 0

        if profit >= 0.02:  # At least 2¢ profit
            opportunities.append({
                'market_id': market_id,
                'question': question,
                'yes_price': yes_price,
                'no_price': no_price,
                'total_cost': total_cost,
                'profit': profit,
                'profit_pct': profit_pct
            })

            print(f"\n🔥 ARBITRAGE FOUND!")
            print(f"   {question[:60]}")
            print(f"   YES: ${yes_price:.3f}, NO: ${no_price:.3f}")
            print(f"   Total: ${total_cost:.3f}")
            print(f"   Profit: ${profit:.3f} ({profit_pct:.2f}%)")

    if not opportunities:
        print("\n❌ No arbitrage opportunities found")
        print("   (Markets are efficient or prices not available)")
    else:
        print(f"\n✅ Found {len(opportunities)} opportunities!")

    return opportunities

def main():
    print(f"\n{'='*60}")
    print("🔍 REAL POLYMARKET DATA TEST")
    print(f"{'='*60}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # Try CLOB API first
    markets = test_clob_api()

    if not markets:
        # Try Gamma API
        markets = test_gamma_api()

    if markets:
        print(f"\n✓ Successfully fetched {len(markets) if isinstance(markets, list) else 'market'} data!")

        # Filter for crypto hourly
        if isinstance(markets, list):
            crypto_markets = find_crypto_hourly_markets(markets)
            print(f"✓ Found {len(crypto_markets)} crypto hourly markets")

            if crypto_markets:
                # Scan for arbitrage
                opportunities = scan_for_arbitrage(crypto_markets)

                if opportunities:
                    print(f"\n{'='*60}")
                    print("SUMMARY")
                    print(f"{'='*60}")
                    print(f"Total markets scanned: {len(crypto_markets)}")
                    print(f"Arbitrage opportunities: {len(opportunities)}")
                    total_potential = sum(o['profit'] * 100 for o in opportunities)
                    print(f"Total potential profit: ${total_potential:.2f} (with 100 shares each)")
            else:
                print("\n⚠️ No crypto hourly markets found")
                print("   Showing all markets sample:")
                for i, m in enumerate(markets[:5]):
                    print(f"   {i+1}. {m.get('question', 'N/A')[:60]}")
    else:
        print("\n❌ Could not fetch real market data")
        print("   Possible reasons:")
        print("   1. Network restrictions")
        print("   2. API requires authentication")
        print("   3. Rate limiting")
        print("\n   Recommendation: Run this script on your local machine")
        print("   Or get a Polymarket API key")

if __name__ == "__main__":
    main()
