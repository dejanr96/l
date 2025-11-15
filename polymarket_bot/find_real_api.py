#!/usr/bin/env python3
"""
Find the CORRECT API endpoint for CURRENT live markets
The /markets endpoint returns old data - need to find the right one
"""

import requests
import json
from datetime import datetime

def test_endpoint(name, url, params=None):
    """Test an API endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    if params:
        print(f"Params: {params}")
    print(f"{'='*60}")

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Failed")
            return None

        data = response.json()

        # Handle different response formats
        if isinstance(data, dict):
            markets = data.get('data') or data.get('markets') or data.get('events') or []
            print(f"Response: dict with keys {list(data.keys())[:5]}")
        elif isinstance(data, list):
            markets = data
            print(f"Response: list")
        else:
            print(f"Response: {type(data)}")
            return None

        if not isinstance(markets, list):
            print(f"❌ No markets list found")
            return None

        print(f"Markets returned: {len(markets)}")

        # Check for crypto hourly markets
        crypto_hourly = []
        for m in markets[:100]:  # Check first 100
            question = m.get('question', '') or m.get('title', '')
            q_lower = question.lower()

            # Look for TODAY's hourly markets
            is_crypto = any(t in q_lower for t in ['bitcoin', 'ethereum', 'btc', 'eth', 'solana', 'xrp'])
            is_updown = 'up or down' in q_lower
            is_today = 'november 15' in q_lower or '11/15' in q_lower or 'nov 15' in q_lower

            if is_crypto and (is_updown or is_today):
                crypto_hourly.append(m)
                print(f"  ✅ FOUND: {question[:70]}")
                print(f"     active={m.get('active')}, closed={m.get('closed')}, accepting={m.get('accepting_orders')}")

        if crypto_hourly:
            print(f"\n🔥 Found {len(crypto_hourly)} crypto markets for TODAY!")
            return crypto_hourly
        else:
            # Show what we got
            if markets:
                print(f"\nSample markets:")
                for m in markets[:3]:
                    q = m.get('question', '') or m.get('title', 'N/A')
                    print(f"  - {q[:70]}")

        return markets

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


print("="*60)
print("FINDING THE RIGHT API FOR CURRENT LIVE MARKETS")
print("="*60)
print(f"Looking for markets with today's date: November 15, 2025")

# Test different endpoints
endpoints = [
    ("CLOB /simplified-markets", "https://clob.polymarket.com/simplified-markets", None),
    ("CLOB /sampling-markets", "https://clob.polymarket.com/sampling-markets", None),
    ("Gamma /markets", "https://gamma-api.polymarket.com/markets", None),
    ("Gamma /markets?active=true", "https://gamma-api.polymarket.com/markets", {"active": "true"}),
    ("Gamma /markets?closed=false", "https://gamma-api.polymarket.com/markets", {"closed": "false"}),
    ("Gamma /events", "https://gamma-api.polymarket.com/events", None),
    ("Gamma /events?active=true", "https://gamma-api.polymarket.com/events", {"active": "true"}),
]

results = {}
for name, url, params in endpoints:
    markets = test_endpoint(name, url, params)
    if markets:
        results[name] = markets

print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")

if not results:
    print("\n❌ None of the standard APIs returned current markets")
    print("\n💡 The website likely uses:")
    print("   1. A different API endpoint")
    print("   2. GraphQL API")
    print("   3. WebSocket for real-time data")
    print("\n📋 Next step: Check browser DevTools on polymarket.com/crypto?tab=hourly")
    print("   to see what API endpoints the website actually calls")
else:
    print(f"\n✅ Found {len(results)} working endpoints:")
    for name, markets in results.items():
        print(f"   - {name}: {len(markets)} markets")

print(f"\n{'='*60}")
print("HOW TO FIND THE REAL API")
print(f"{'='*60}")

print("""
1. Open https://polymarket.com/crypto?tab=hourly in browser
2. Open DevTools (F12)
3. Go to Network tab
4. Refresh the page
5. Filter by 'Fetch/XHR'
6. Look for API calls that return the hourly crypto markets
7. Copy the URL and share it

The website is definitely calling an API to get those markets.
We just need to find which one!

Alternative: The markets might be fetched using GraphQL or a
different API domain entirely.
""")
