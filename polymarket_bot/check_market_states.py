#!/usr/bin/env python3
"""
Standalone script to check actual market states
Shows why markets are being filtered out
"""

import requests
import json

print("="*60)
print("CHECKING MARKET STATES")
print("="*60)

# Fetch markets
response = requests.get("https://clob.polymarket.com/markets", timeout=10)
if response.status_code != 200:
    print(f"Error: {response.status_code}")
    exit(1)

data = response.json()
markets = data.get('data', [])

print(f"\nTotal markets fetched: {len(markets)}")

# Check first 10 markets' states
print(f"\n{'='*60}")
print("SAMPLE MARKET STATES (first 10)")
print(f"{'='*60}")

for i, market in enumerate(markets[:10]):
    active = market.get('active')
    closed = market.get('closed')
    accepting = market.get('accepting_orders')
    question = market.get('question', 'N/A')[:60]

    print(f"\n{i+1}. {question}")
    print(f"   active={active}, closed={closed}, accepting_orders={accepting}")

# Count states across ALL markets
print(f"\n{'='*60}")
print("STATISTICS ACROSS ALL MARKETS")
print(f"{'='*60}")

active_true = sum(1 for m in markets if m.get('active') == True)
active_false = sum(1 for m in markets if m.get('active') == False)
closed_true = sum(1 for m in markets if m.get('closed') == True)
closed_false = sum(1 for m in markets if m.get('closed') == False)
accepting_true = sum(1 for m in markets if m.get('accepting_orders') == True)
accepting_false = sum(1 for m in markets if m.get('accepting_orders') == False)

print(f"\nactive=True:  {active_true:4d} / {len(markets)}")
print(f"active=False: {active_false:4d} / {len(markets)}")
print(f"\nclosed=True:  {closed_true:4d} / {len(markets)}")
print(f"closed=False: {closed_false:4d} / {len(markets)}")
print(f"\naccepting_orders=True:  {accepting_true:4d} / {len(markets)}")
print(f"accepting_orders=False: {accepting_false:4d} / {len(markets)}")

# Find markets that match our criteria
print(f"\n{'='*60}")
print("FILTERING TESTS")
print(f"{'='*60}")

# Test 1: active AND not closed AND accepting_orders
test1 = [m for m in markets if
         m.get('active') == True and
         m.get('closed') == False and
         m.get('accepting_orders') == True]
print(f"\n1. active=True AND closed=False AND accepting_orders=True:")
print(f"   Result: {len(test1)} markets")

# Test 2: active AND not closed
test2 = [m for m in markets if
         m.get('active') == True and
         m.get('closed') == False]
print(f"\n2. active=True AND closed=False:")
print(f"   Result: {len(test2)} markets")

# Test 3: just active
test3 = [m for m in markets if m.get('active') == True]
print(f"\n3. active=True (ignore closed):")
print(f"   Result: {len(test3)} markets")

if test3:
    print(f"\n   Sample active markets:")
    for m in test3[:3]:
        print(f"   - {m.get('question', 'N/A')[:70]}")
        print(f"     closed={m.get('closed')}, accepting={m.get('accepting_orders')}")

# Check for crypto hourly markets in active markets
print(f"\n{'='*60}")
print("LOOKING FOR CRYPTO HOURLY MARKETS")
print(f"{'='*60}")

crypto_tokens = ['Bitcoin', 'Ethereum', 'Solana', 'XRP', 'BTC', 'ETH', 'SOL']
hourly_markets = []

for market in test3:  # Use active markets
    question = market.get('question', '').lower()

    is_crypto = any(token.lower() in question for token in crypto_tokens)
    is_updown = 'up or down' in question
    is_hourly = any(time in question for time in ['am et', 'pm et'])

    if is_crypto and (is_updown or is_hourly):
        hourly_markets.append(market)

print(f"\nFound {len(hourly_markets)} crypto hourly markets in active markets:")
if hourly_markets:
    for m in hourly_markets[:10]:
        print(f"  - {m.get('question', 'N/A')}")
        print(f"    closed={m.get('closed')}, accepting={m.get('accepting_orders')}")

print(f"\n{'='*60}")
print("RECOMMENDATION")
print(f"{'='*60}")

if test1:
    print(f"\n✅ {len(test1)} markets are open and accepting orders!")
elif test2:
    print(f"\n⚠️  {len(test2)} markets are open but NOT accepting orders")
    print(f"   Bot can view these but cannot trade")
elif test3:
    print(f"\n⚠️  Only {len(test3)} active markets found, but all are CLOSED")
    print(f"   Polymarket may not have live hourly markets right now")
    print(f"   Try again during market hours (check polymarket.com)")
else:
    print(f"\n❌ No active markets found at all!")

if hourly_markets:
    print(f"\n✅ Found {len(hourly_markets)} crypto hourly markets")
    print(f"   Bot should be able to scan these for arbitrage")
else:
    print(f"\n❌ No crypto hourly markets found")
    print(f"   These markets may not exist on Polymarket anymore,")
    print(f"   or they're only active at certain times")
