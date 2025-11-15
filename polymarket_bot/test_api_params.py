#!/usr/bin/env python3
"""
Test different API parameters to find LIVE markets
"""

import requests
import json

def test_endpoint(url, params=None):
    """Test an API endpoint with parameters"""
    param_str = f"?{params}" if params else ""
    print(f"\nTesting: {url}{param_str}")

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            if isinstance(data, dict) and 'data' in data:
                markets = data['data']
                print(f"Markets: {len(markets)}")

                if markets:
                    m = markets[0]
                    print(f"Sample: {m.get('question', 'N/A')[:60]}")
                    print(f"  active={m.get('active')}, closed={m.get('closed')}, accepting={m.get('accepting_orders')}")

                    # Count states
                    active = sum(1 for x in markets if x.get('active'))
                    not_closed = sum(1 for x in markets if not x.get('closed'))
                    accepting = sum(1 for x in markets if x.get('accepting_orders'))

                    print(f"  active={active}, not_closed={not_closed}, accepting={accepting}")

                return markets
            elif isinstance(data, list):
                print(f"Markets: {len(data)}")
                if data:
                    print(f"Sample: {data[0].get('question', 'N/A')[:60]}")
                return data
    except Exception as e:
        print(f"Error: {e}")

    return None

print("="*60)
print("TESTING API PARAMETERS TO FIND LIVE MARKETS")
print("="*60)

base_url = "https://clob.polymarket.com/markets"

# Test 1: Default (what we're currently doing)
print("\n1. DEFAULT (no params)")
markets = test_endpoint(base_url)

# Test 2: Filter by active
print("\n2. FILTER: active=true")
markets = test_endpoint(base_url, {"active": "true"})

# Test 3: Filter by closed
print("\n3. FILTER: closed=false")
markets = test_endpoint(base_url, {"closed": "false"})

# Test 4: Filter by both
print("\n4. FILTER: active=true&closed=false")
markets = test_endpoint(base_url, {"active": "true", "closed": "false"})

# Test 5: Try different endpoint - simplified markets
print("\n5. SIMPLIFIED MARKETS ENDPOINT")
markets = test_endpoint("https://clob.polymarket.com/simplified-markets")

# Test 6: Try sampling markets
print("\n6. SAMPLING MARKETS ENDPOINT")
markets = test_endpoint("https://clob.polymarket.com/sampling-markets")

# Test 7: Look for crypto specifically
print("\n7. Try to search for crypto markets")
# Some APIs support search/filter
test_endpoint(base_url, {"search": "bitcoin"})
test_endpoint(base_url, {"tag": "crypto"})

# Test 8: Check if there's a next_cursor for pagination
print("\n8. Check what next_cursor gives us")
response = requests.get(base_url, timeout=10)
if response.status_code == 200:
    data = response.json()
    if 'next_cursor' in data:
        print(f"next_cursor found: {data['next_cursor']}")
        # Try with next cursor to see different markets
        test_endpoint(base_url, {"next_cursor": data['next_cursor']})

print("\n" + "="*60)
print("RECOMMENDATION")
print("="*60)

print("\nBased on test results:")
print("1. If any endpoint returns markets with closed=False, use that")
print("2. If active=true param works, use that")
print("3. Otherwise we may need to use Gamma API or different approach")
