#!/usr/bin/env python3
"""
Direct blockchain data scraper using alternative methods
"""

import requests
import json
from datetime import datetime
import time

def try_polygonscan_api(address):
    """Try PolygonScan API with different approach"""
    print("Trying PolygonScan API...")

    # Try without API key first - some endpoints work
    base_url = "https://api.polygonscan.com/api"

    # Token transfers
    params = {
        'module': 'account',
        'action': 'tokentx',
        'address': address,
        'startblock': 0,
        'endblock': 99999999,
        'page': 1,
        'offset': 100,
        'sort': 'desc'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get('status') == '1' and data.get('result'):
                print(f"✓ Got {len(data['result'])} token transfers!")
                return data['result']
            else:
                print(f"API Message: {data.get('message', 'No data')}")
                return None
        else:
            print(f"HTTP Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def try_covalent_api(address):
    """Try Covalent API (has free tier)"""
    print("\nTrying Covalent API...")

    # Covalent free API endpoint
    url = f"https://api.covalenthq.com/v1/137/address/{address}/transactions_v2/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get('data') and data['data'].get('items'):
                print(f"✓ Got {len(data['data']['items'])} transactions!")
                return data['data']['items']
        else:
            print(f"HTTP Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def try_quicknode_api(address):
    """Try QuickNode public RPC"""
    print("\nTrying public Polygon RPC...")

    # Public Polygon RPC endpoints
    rpcs = [
        "https://polygon-rpc.com",
        "https://rpc-mainnet.matic.network",
        "https://polygon-mainnet.public.blastapi.io"
    ]

    for rpc in rpcs:
        try:
            # Get transaction count
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getTransactionCount",
                "params": [address, "latest"],
                "id": 1
            }

            response = requests.post(rpc, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    tx_count = int(result['result'], 16)
                    print(f"✓ RPC works! Address has {tx_count} transactions")

                    # Get balance
                    payload = {
                        "jsonrpc": "2.0",
                        "method": "eth_getBalance",
                        "params": [address, "latest"],
                        "id": 1
                    }
                    response = requests.post(rpc, json=payload, timeout=10)
                    if response.status_code == 200:
                        result = response.json()
                        balance = int(result['result'], 16) / 1e18
                        print(f"  Balance: {balance:.4f} MATIC")

                    return {"rpc": rpc, "tx_count": tx_count}
        except Exception as e:
            print(f"  {rpc}: {e}")
            continue

    return None

def try_bitquery(address):
    """Try Bitquery GraphQL API"""
    print("\nTrying Bitquery API...")

    url = "https://graphql.bitquery.io"

    query = """
    {
      ethereum(network: matic) {
        address(address: {is: "%s"}) {
          balances {
            currency {
              symbol
              name
            }
            value
          }
        }
        transfers(
          txFrom: {is: "%s"}
          options: {limit: 50, desc: "block.height"}
        ) {
          block {
            timestamp {
              time
            }
          }
          sender {
            address
          }
          receiver {
            address
          }
          currency {
            symbol
            name
          }
          amount
          transaction {
            hash
          }
        }
      }
    }
    """ % (address, address)

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.post(url, json={'query': query}, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                print(f"✓ Got response from Bitquery!")
                return data['data']
        else:
            print(f"HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

    return None

def analyze_basic_data(address):
    """Try to get basic information about the address"""
    print(f"\n{'='*60}")
    print(f"Analyzing: {address}")
    print(f"{'='*60}\n")

    results = {}

    # Try different APIs
    transfers = try_polygonscan_api(address)
    if transfers:
        results['polygonscan'] = transfers
        analyze_transfers(transfers)
        return results

    covalent = try_covalent_api(address)
    if covalent:
        results['covalent'] = covalent
        analyze_covalent_data(covalent)
        return results

    rpc_data = try_quicknode_api(address)
    if rpc_data:
        results['rpc'] = rpc_data

    bitquery = try_bitquery(address)
    if bitquery:
        results['bitquery'] = bitquery
        analyze_bitquery_data(bitquery)
        return results

    print("\n⚠️ All methods failed. Possible reasons:")
    print("1. Rate limiting without API key")
    print("2. IP blocking")
    print("3. Need authentication")
    print("\nRecommendation: Get free API key from PolygonScan")

    return results

def analyze_transfers(transfers):
    """Analyze PolygonScan transfer data"""
    print(f"\n{'='*60}")
    print("ANALYSIS RESULTS")
    print(f"{'='*60}\n")

    print(f"Total transfers found: {len(transfers)}")

    # Count tokens
    tokens_in = {}
    tokens_out = {}

    target = "0xeffcc79a8572940cee2238b44eac89f2c48fda88"

    for tx in transfers[:50]:  # Analyze first 50
        symbol = tx.get('tokenSymbol', 'UNK')

        if tx.get('to', '').lower() == target.lower():
            tokens_in[symbol] = tokens_in.get(symbol, 0) + 1
        else:
            tokens_out[symbol] = tokens_out.get(symbol, 0) + 1

    print("\nTOKENS RECEIVED (top 10):")
    for token, count in sorted(tokens_in.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {token}: {count} times")

    print("\nTOKENS SENT (top 10):")
    for token, count in sorted(tokens_out.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {token}: {count} times")

    # Recent activity
    print("\nRECENT TRANSACTIONS (last 10):")
    for tx in transfers[:10]:
        ts = datetime.fromtimestamp(int(tx.get('timeStamp', 0)))
        symbol = tx.get('tokenSymbol', 'UNK')
        direction = "IN" if tx.get('to', '').lower() == target.lower() else "OUT"
        print(f"  {ts.strftime('%Y-%m-%d %H:%M')} - {direction:3} {symbol}")

def analyze_covalent_data(data):
    """Analyze Covalent API data"""
    print(f"\n{'='*60}")
    print("COVALENT DATA ANALYSIS")
    print(f"{'='*60}\n")

    print(f"Found {len(data)} transactions")

    for i, tx in enumerate(data[:10]):
        ts = tx.get('block_signed_at', 'Unknown')
        print(f"\nTx {i+1}: {ts}")
        print(f"  Hash: {tx.get('tx_hash', 'N/A')[:20]}...")
        print(f"  Value: {tx.get('value', 0)}")

def analyze_bitquery_data(data):
    """Analyze Bitquery GraphQL data"""
    print(f"\n{'='*60}")
    print("BITQUERY DATA ANALYSIS")
    print(f"{'='*60}\n")

    if 'ethereum' in data:
        transfers = data['ethereum'].get('transfers', [])
        print(f"Found {len(transfers)} transfers")

        for i, transfer in enumerate(transfers[:10]):
            symbol = transfer.get('currency', {}).get('symbol', 'UNK')
            amount = transfer.get('amount', 0)
            print(f"\n{i+1}. {symbol}: {amount}")

def main():
    address = "0xeffcc79a8572940cee2238b44eac89f2c48fda88"
    results = analyze_basic_data(address)

    # Save results
    if results:
        with open('bot_data.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Data saved to bot_data.json")

if __name__ == "__main__":
    main()
