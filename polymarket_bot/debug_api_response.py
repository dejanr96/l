#!/usr/bin/env python3
"""
Debug script to see exactly what Polymarket API returns
"""

import requests
import json

def test_clob_api():
    """Test CLOB API and show response structure"""
    print("="*60)
    print("TESTING CLOB API")
    print("="*60)

    url = "https://clob.polymarket.com/markets"

    try:
        response = requests.get(url, timeout=10)
        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Type: {type(data)}")

                if isinstance(data, dict):
                    print(f"\nDict Keys: {list(data.keys())}")

                    # Show first few items of each key
                    for key, value in list(data.items())[:5]:
                        print(f"\n'{key}': {type(value)}")
                        if isinstance(value, list):
                            print(f"  Length: {len(value)}")
                            if len(value) > 0:
                                print(f"  First item type: {type(value[0])}")
                                if isinstance(value[0], dict):
                                    print(f"  First item keys: {list(value[0].keys())[:10]}")
                                    print(f"  Sample: {json.dumps(value[0], indent=2)[:500]}")
                        elif isinstance(value, str):
                            print(f"  Value: {value[:100]}")
                        elif isinstance(value, (int, float, bool)):
                            print(f"  Value: {value}")

                    # Try to find markets
                    print("\n" + "="*60)
                    print("LOOKING FOR MARKETS...")
                    print("="*60)

                    for key in ['data', 'markets', 'results', 'items', 'market', 'events']:
                        if key in data:
                            print(f"\n✓ Found key '{key}'!")
                            markets = data[key]
                            print(f"  Type: {type(markets)}")
                            if isinstance(markets, list):
                                print(f"  Count: {len(markets)}")
                                if len(markets) > 0:
                                    print(f"  First market: {json.dumps(markets[0], indent=2)[:500]}")

                elif isinstance(data, list):
                    print(f"\n✓ Response is a LIST!")
                    print(f"  Length: {len(data)}")
                    if len(data) > 0:
                        print(f"  First item type: {type(data[0])}")
                        if isinstance(data[0], dict):
                            print(f"  First item keys: {list(data[0].keys())[:10]}")
                            print(f"  Sample: {json.dumps(data[0], indent=2)[:500]}")

                else:
                    print(f"\nUnexpected type: {type(data)}")
                    print(f"Content: {str(data)[:500]}")

            except json.JSONDecodeError as e:
                print(f"\n❌ JSON decode error: {e}")
                print(f"Raw response: {response.text[:500]}")

        elif response.status_code == 403:
            print("\n❌ 403 Forbidden - API is blocked")

        else:
            print(f"\n❌ Error status code: {response.status_code}")
            print(f"Response: {response.text[:500]}")

    except Exception as e:
        print(f"\n❌ Exception: {e}")


def test_gamma_api():
    """Test Gamma API"""
    print("\n\n" + "="*60)
    print("TESTING GAMMA API")
    print("="*60)

    url = "https://gamma-api.polymarket.com/markets"

    try:
        response = requests.get(url, timeout=10)
        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Type: {type(data)}")

                if isinstance(data, dict):
                    print(f"Dict Keys: {list(data.keys())}")
                elif isinstance(data, list):
                    print(f"List Length: {len(data)}")
                    if len(data) > 0:
                        print(f"First item: {json.dumps(data[0], indent=2)[:500]}")

            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")

        elif response.status_code == 403:
            print("❌ 403 Forbidden - API is blocked")

    except Exception as e:
        print(f"Exception: {e}")


if __name__ == "__main__":
    test_clob_api()
    test_gamma_api()

    print("\n\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("\nRun this script on your PC to see the API response structure.")
    print("Then we can update the bot to extract markets correctly.")
