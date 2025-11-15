#!/usr/bin/env python3
"""
Inspect the actual structure of markets from the Events API
"""

import requests
import json

print("="*60)
print("INSPECTING MARKET DATA STRUCTURE")
print("="*60)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}

url = "https://gamma-api.polymarket.com/events"
params = {
    'tag_id': '102127',  # 1H markets
    'closed': 'false',
    'limit': '5'  # Just get 5 for inspection
}

response = requests.get(url, params=params, headers=headers, timeout=10)

if response.status_code == 200:
    events = response.json()

    if events and len(events) > 0:
        first_event = events[0]

        print(f"\n📋 FIRST EVENT STRUCTURE:")
        print(json.dumps(first_event, indent=2))

        print(f"\n{'='*60}")
        print("MARKET FIELDS AVAILABLE:")
        print(f"{'='*60}\n")

        markets = first_event.get('markets', [])
        if markets:
            first_market = markets[0]

            print(f"Available fields in market object:")
            for key in sorted(first_market.keys()):
                value = first_market[key]
                if isinstance(value, (str, int, float, bool)):
                    print(f"  {key}: {value}")
                elif isinstance(value, list):
                    print(f"  {key}: [list with {len(value)} items]")
                elif isinstance(value, dict):
                    print(f"  {key}: {{dict with keys: {list(value.keys())[:5]}}}")
                else:
                    print(f"  {key}: {type(value)}")

            print(f"\n{'='*60}")
            print("KEY FIELDS WE NEED:")
            print(f"{'='*60}\n")

            # Check for ID fields
            id_fields = ['id', 'market_id', 'condition_id', 'token_id', 'clobTokenIds']
            for field in id_fields:
                value = first_market.get(field)
                if value:
                    print(f"  ✅ {field}: {value}")
                else:
                    print(f"  ❌ {field}: NOT FOUND")

            # Check for price fields
            print(f"\nPrice fields:")
            price_fields = ['outcome_prices', 'prices', 'best_bid', 'best_ask', 'lastPrice']
            for field in price_fields:
                value = first_market.get(field)
                if value:
                    print(f"  ✅ {field}: {value}")
                else:
                    print(f"  ❌ {field}: NOT FOUND")

            print(f"\n{'='*60}")
            print("RECOMMENDATION:")
            print(f"{'='*60}\n")

            # Check if we have clobTokenIds
            clob_token_ids = first_market.get('clobTokenIds')
            if clob_token_ids and len(clob_token_ids) > 0:
                print(f"✅ Found clobTokenIds: {clob_token_ids}")
                print(f"\n💡 USE THESE IDs to fetch orderbook!")
                print(f"\nFor YES token: {clob_token_ids[0]}")
                if len(clob_token_ids) > 1:
                    print(f"For NO token: {clob_token_ids[1]}")

                print(f"\nOrderbook API call:")
                print(f"https://clob.polymarket.com/book?token_id={clob_token_ids[0]}")
            else:
                print(f"❌ No clobTokenIds found")
                print(f"   Markets might not be initialized yet")
    else:
        print("No events returned")
else:
    print(f"Error: {response.status_code}")
