#!/usr/bin/env python3
"""
Aggressive Polymarket scraper - tries multiple methods
"""

import requests
import json
import time

def try_gamma_api(address):
    """Try Gamma API (Polymarket's main API)"""
    print("Trying Gamma API...")

    endpoints = [
        f"https://gamma-api.polymarket.com/markets",
        f"https://gamma-api.polymarket.com/events",
        f"https://strapi-matic.poly.market/markets",
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Origin': 'https://polymarket.com',
        'Referer': 'https://polymarket.com/'
    }

    for endpoint in endpoints:
        try:
            print(f"  Trying: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"    Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"    ✓ Got data! {len(str(data))} chars")
                return data
        except Exception as e:
            print(f"    Error: {e}")

    return None

def try_clob_api(address):
    """Try CLOB (Central Limit Order Book) API"""
    print("\nTrying CLOB API...")

    base = "https://clob.polymarket.com"

    endpoints = [
        f"{base}/markets",
        f"{base}/book",
        f"{base}/trades",
        f"{base}/positions?user={address}",
        f"{base}/orders?maker={address}",
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
    }

    for endpoint in endpoints:
        try:
            print(f"  Trying: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"    Status: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"    ✓ Got data! Type: {type(data)}")
                    if data:
                        print(f"    Sample: {str(data)[:200]}")
                        return data
                except:
                    print(f"    Response text: {response.text[:200]}")
        except Exception as e:
            print(f"    Error: {e}")

    return None

def try_subgraph(address):
    """Try The Graph subgraph"""
    print("\nTrying The Graph subgraph...")

    # Polymarket subgraph
    url = "https://api.thegraph.com/subgraphs/name/tokenunion/polymarket"

    # Query for user data
    query = """
    {
      user(id: "%s") {
        id
        positions {
          id
          market {
            id
            question
          }
          quantityBought
          quantitySold
        }
      }
    }
    """ % address.lower()

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }

    try:
        print(f"  Trying: {url}")
        response = requests.post(url, json={'query': query}, headers=headers, timeout=10)
        print(f"    Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"    ✓ Got data!")
            if 'data' in data:
                print(f"    User data: {data['data']}")
                return data['data']
            else:
                print(f"    Response: {data}")
        else:
            print(f"    Response: {response.text[:200]}")
    except Exception as e:
        print(f"    Error: {e}")

    return None

def try_polygonscan_with_polymarket_contracts(address):
    """Check PolygonScan for interactions with known Polymarket contracts"""
    print("\nChecking PolygonScan for Polymarket contract interactions...")

    # Known Polymarket contracts
    polymarket_contracts = {
        'CTF_Exchange': '0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E',
        'ConditionalTokens': '0x4D97DCd97eC945f40cF65F87097ACe5EA0476045',
        'NegRiskAdapter': '0xC5d563A36AE78145C45a50134d48A1215220f80a',
        'USDC': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
    }

    base_url = "https://api.polygonscan.com/api"

    for name, contract in polymarket_contracts.items():
        print(f"\n  Checking {name} ({contract[:10]}...)...")

        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': 0,
            'endblock': 99999999,
            'page': 1,
            'offset': 10,
            'sort': 'desc'
        }

        try:
            response = requests.get(base_url, params=params, timeout=10)
            print(f"    Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1' and data.get('result'):
                    txs = data['result']

                    # Filter for Polymarket contracts
                    polymarket_txs = [tx for tx in txs if tx.get('to', '').lower() in
                                     [c.lower() for c in polymarket_contracts.values()]]

                    if polymarket_txs:
                        print(f"    ✓ Found {len(polymarket_txs)} Polymarket transactions!")
                        return polymarket_txs
                    else:
                        print(f"    No Polymarket txs in recent {len(txs)} transactions")
                else:
                    print(f"    API message: {data.get('message', 'No data')}")
            else:
                print(f"    HTTP error: {response.status_code}")
        except Exception as e:
            print(f"    Error: {e}")

    return None

def try_public_polymarket_endpoints():
    """Try to get public market data"""
    print("\nTrying public Polymarket endpoints...")

    endpoints = [
        "https://strapi-matic.poly.market/markets?_limit=5",
        "https://strapi-matic.poly.market/events?_limit=5",
        "https://lb-api.polymarket.com/events",
        "https://data-api.polymarket.com/markets",
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Origin': 'https://polymarket.com',
        'Referer': 'https://polymarket.com/'
    }

    for url in endpoints:
        try:
            print(f"  Trying: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"    Status: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"    ✓ SUCCESS! Got {len(str(data))} chars")
                    print(f"    Sample: {str(data)[:300]}")
                    return data
                except:
                    print(f"    Text: {response.text[:200]}")
        except Exception as e:
            print(f"    Error: {e}")

    return None

def main():
    address = "0xeffcc79a8572940cee2238b44eac89f2c48fda88"

    print(f"""
╔══════════════════════════════════════════════════════════╗
║        AGGRESSIVE POLYMARKET SCRAPER                     ║
╚══════════════════════════════════════════════════════════╝

Target: {address}

Trying every possible method to get data...
""")

    results = {}

    # Try public data first
    public_data = try_public_polymarket_endpoints()
    if public_data:
        results['public_markets'] = public_data
        print("\n✓ Got public market data!")

    # Try Gamma API
    gamma_data = try_gamma_api(address)
    if gamma_data:
        results['gamma'] = gamma_data

    # Try CLOB API
    clob_data = try_clob_api(address)
    if clob_data:
        results['clob'] = clob_data

    # Try The Graph
    subgraph_data = try_subgraph(address)
    if subgraph_data:
        results['subgraph'] = subgraph_data

    # Try PolygonScan
    polygonscan_data = try_polygonscan_with_polymarket_contracts(address)
    if polygonscan_data:
        results['polygonscan'] = polygonscan_data

        # Analyze the transactions
        print("\n" + "="*60)
        print("ANALYZING POLYMARKET TRANSACTIONS FROM POLYGONSCAN")
        print("="*60)

        analyze_polymarket_transactions(polygonscan_data, address)

    # Save results
    if results:
        with open('polymarket_data.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Data saved to polymarket_data.json")
    else:
        print("\n⚠️ Unable to fetch any data")
        print("\nAll methods blocked. You'll need to:")
        print("1. Visit https://polymarket.com/@FirstOrder manually")
        print("2. Visit https://polygonscan.com/address/" + address)
        print("3. Tell me what you see")

def analyze_polymarket_transactions(txs, address):
    """Analyze Polymarket transactions from PolygonScan"""

    from collections import Counter
    from datetime import datetime

    contracts_hit = Counter()
    daily_activity = Counter()

    contract_names = {
        '0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e': 'CTF Exchange',
        '0x4d97dcd97ec945f40cf65f87097ace5ea0476045': 'Conditional Tokens',
        '0xc5d563a36ae78145c45a50134d48a1215220f80a': 'Neg Risk Adapter',
        '0x2791bca1f2de4661ed88a30c99a7a9449aa84174': 'USDC',
    }

    for tx in txs:
        to_addr = tx.get('to', '').lower()
        timestamp = int(tx.get('timeStamp', 0))
        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

        contracts_hit[to_addr] += 1
        daily_activity[date] += 1

    print(f"\nTotal Polymarket transactions: {len(txs)}")

    print("\nContracts interacted with:")
    for addr, count in contracts_hit.items():
        name = contract_names.get(addr, addr[:10] + '...')
        print(f"  {name}: {count} times")

    print("\nRecent activity:")
    for date, count in sorted(daily_activity.items(), reverse=True)[:10]:
        print(f"  {date}: {count} transactions")

    print("\nRecent transactions (last 5):")
    for i, tx in enumerate(txs[:5]):
        ts = datetime.fromtimestamp(int(tx.get('timeStamp', 0)))
        to_name = contract_names.get(tx.get('to', '').lower(), tx.get('to', '')[:10])
        print(f"\n  {i+1}. {ts.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"     To: {to_name}")
        print(f"     Hash: {tx.get('hash', '')[:20]}...")

if __name__ == "__main__":
    main()
