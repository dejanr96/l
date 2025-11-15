#!/usr/bin/env python3
"""
Paginate through ALL Polymarket markets to find crypto hourly markets
"""

import requests
import time

print("="*60)
print("SEARCHING FOR CRYPTO HOURLY MARKETS")
print("="*60)

base_url = "https://clob.polymarket.com/markets"
all_crypto_hourly = []
page = 0
next_cursor = None
total_markets_checked = 0

crypto_tokens = ['bitcoin', 'ethereum', 'btc', 'eth', 'solana', 'xrp', 'sol']

print("\nPaginating through all markets...")
print("(This may take a minute...)\n")

while True:
    page += 1

    # Build request params
    params = {}
    if next_cursor:
        params['next_cursor'] = next_cursor

    # Fetch page
    response = requests.get(base_url, params=params, timeout=10)

    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        break

    data = response.json()
    markets = data.get('data', [])
    next_cursor = data.get('next_cursor')

    total_markets_checked += len(markets)

    print(f"Page {page}: {len(markets)} markets (Total checked: {total_markets_checked})")

    # Check each market
    for market in markets:
        question = market.get('question', '').lower()

        # Check if it's a crypto hourly market
        is_crypto = any(token in question for token in crypto_tokens)
        is_updown = 'up or down' in question
        is_hourly = any(time in question for time in ['am et', 'pm et', 'am', 'pm'])

        if is_crypto and (is_updown or is_hourly):
            all_crypto_hourly.append(market)
            print(f"  ✅ FOUND: {market.get('question', 'N/A')[:70]}")
            print(f"     active={market.get('active')}, closed={market.get('closed')}, accepting={market.get('accepting_orders')}")

    # Stop if no more pages
    if not next_cursor:
        print(f"\n✓ Reached end of results")
        break

    # Safety: don't fetch more than 10 pages
    if page >= 10:
        print(f"\n⚠️  Stopped at page 10 (safety limit)")
        break

    # Small delay to be nice to API
    time.sleep(0.5)

print(f"\n{'='*60}")
print("RESULTS")
print(f"{'='*60}")

print(f"\nTotal markets checked: {total_markets_checked}")
print(f"Crypto hourly markets found: {len(all_crypto_hourly)}")

if all_crypto_hourly:
    print(f"\n{'='*60}")
    print(f"ALL {len(all_crypto_hourly)} CRYPTO HOURLY MARKETS:")
    print(f"{'='*60}")

    # Group by state
    accepting = [m for m in all_crypto_hourly if m.get('accepting_orders') == True]
    not_closed = [m for m in all_crypto_hourly if m.get('closed') == False]
    active = [m for m in all_crypto_hourly if m.get('active') == True]

    print(f"\nBy state:")
    print(f"  Active: {len(active)}/{len(all_crypto_hourly)}")
    print(f"  Not closed: {len(not_closed)}/{len(all_crypto_hourly)}")
    print(f"  Accepting orders: {len(accepting)}/{len(all_crypto_hourly)}")

    if accepting:
        print(f"\n🔥 LIVE MARKETS (accepting orders):")
        for m in accepting:
            print(f"  - {m.get('question')}")
            print(f"    ID: {m.get('condition_id', 'N/A')[:20]}...")
    else:
        print(f"\n⚠️  No crypto hourly markets accepting orders")

    if active and not accepting:
        print(f"\n📋 ACTIVE MARKETS (but not accepting orders):")
        for m in active[:10]:  # Show first 10
            print(f"  - {m.get('question')}")
            print(f"    active={m.get('active')}, closed={m.get('closed')}, accepting={m.get('accepting_orders')}")

else:
    print("\n❌ No crypto hourly markets found in any pages")
    print("   Polymarket may have discontinued these markets")

print(f"\n{'='*60}")
print("RECOMMENDATION")
print(f"{'='*60}")

if accepting:
    print(f"\n✅ Found {len(accepting)} live crypto hourly markets!")
    print("   The bot should work with these markets")
elif all_crypto_hourly:
    print(f"\n⚠️  Found {len(all_crypto_hourly)} crypto hourly markets but NONE accepting orders")
    print("   These markets may only accept orders at specific times")
    print("   Check polymarket.com to see when they're active")
else:
    print("\n❌ No crypto hourly markets found at all")
    print("   Polymarket may have removed these markets")
    print("   Check https://polymarket.com/crypto?tab=hourly")
