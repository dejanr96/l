#!/usr/bin/env python3
"""
Test the CORRECT API endpoint found via browser DevTools
"""

import requests
import json

print("="*60)
print("TESTING THE REAL API ENDPOINT")
print("="*60)

# The real endpoint from browser DevTools
url = "https://gamma-api.polymarket.com/events"
params = {
    'tag_id': '102531',  # Crypto markets tag
    'closed': 'false',   # Only open markets
    'limit': '100'
}

print(f"\nURL: {url}")
print(f"Params: {params}")

response = requests.get(url, params=params, timeout=10)

print(f"\nStatus: {response.status_code}")

if response.status_code == 200:
    data = response.json()

    print(f"Response type: {type(data)}")

    if isinstance(data, list):
        print(f"✅ Got {len(data)} events!")

        # Show first few
        print(f"\n{'='*60}")
        print("FIRST 10 EVENTS:")
        print(f"{'='*60}")

        for i, event in enumerate(data[:10], 1):
            title = event.get('title', 'N/A')
            description = event.get('description', 'N/A')
            markets = event.get('markets', [])

            print(f"\n{i}. {title}")
            print(f"   Description: {description[:80]}")
            print(f"   Markets: {len(markets)}")

            # Show markets
            if markets:
                for m in markets[:2]:
                    question = m.get('question', 'N/A')
                    active = m.get('active')
                    closed = m.get('closed')
                    print(f"     - {question[:60]}")
                    print(f"       active={active}, closed={closed}")

        # Look for crypto hourly
        print(f"\n{'='*60}")
        print("LOOKING FOR CRYPTO HOURLY MARKETS")
        print(f"{'='*60}")

        crypto_count = 0
        hourly_count = 0

        for event in data:
            title = event.get('title', '').lower()
            description = event.get('description', '').lower()

            is_crypto = any(t in title or t in description for t in ['bitcoin', 'ethereum', 'btc', 'eth'])
            is_hourly = 'hourly' in title or 'hourly' in description or 'up or down' in title.lower()

            if is_crypto:
                crypto_count += 1
            if is_hourly:
                hourly_count += 1

            if is_crypto and is_hourly:
                print(f"\n✅ FOUND: {event.get('title')}")
                markets = event.get('markets', [])
                print(f"   Markets: {len(markets)}")
                for m in markets[:3]:
                    print(f"   - {m.get('question', 'N/A')[:70]}")

        print(f"\nSummary:")
        print(f"  Total events: {len(data)}")
        print(f"  Crypto events: {crypto_count}")
        print(f"  Hourly events: {hourly_count}")

    elif isinstance(data, dict):
        print(f"Response is dict with keys: {list(data.keys())}")

else:
    print(f"❌ Error: {response.status_code}")
    print(f"Response: {response.text[:200]}")

print(f"\n{'='*60}")
print("NEXT STEP")
print(f"{'='*60}")
print("\nIf this shows crypto hourly markets, we'll update the bot to use this API!")
