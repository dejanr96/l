#!/usr/bin/env python3
"""
Find the 13 markets that are accepting_orders=True
These might be the live ones!
"""

import requests

print("="*60)
print("FINDING MARKETS ACCEPTING ORDERS")
print("="*60)

response = requests.get("https://clob.polymarket.com/markets", timeout=10)
data = response.json()
markets = data.get('data', [])

print(f"\nTotal markets: {len(markets)}")

# Find markets accepting orders
accepting = [m for m in markets if m.get('accepting_orders') == True]

print(f"Markets accepting orders: {len(accepting)}")

if accepting:
    print(f"\n{'='*60}")
    print(f"ALL {len(accepting)} MARKETS ACCEPTING ORDERS:")
    print(f"{'='*60}")

    for i, m in enumerate(accepting, 1):
        question = m.get('question', 'N/A')
        active = m.get('active')
        closed = m.get('closed')
        accepting = m.get('accepting_orders')

        print(f"\n{i}. {question}")
        print(f"   active={active}, closed={closed}, accepting_orders={accepting}")

        # Check if crypto
        q_lower = question.lower()
        is_crypto = any(token in q_lower for token in ['bitcoin', 'ethereum', 'btc', 'eth', 'crypto', 'solana', 'xrp'])
        is_hourly = any(time in q_lower for time in ['am et', 'pm et'])

        if is_crypto:
            print(f"   🔥 CRYPTO MARKET!")
        if is_hourly:
            print(f"   ⏰ HOURLY MARKET!")

    # Count crypto hourly in accepting markets
    crypto_hourly = [m for m in accepting
                     if any(t in m.get('question', '').lower() for t in ['bitcoin', 'ethereum', 'crypto', 'btc', 'eth', 'solana', 'xrp'])
                     and any(time in m.get('question', '').lower() for time in ['am et', 'pm et'])]

    print(f"\n{'='*60}")
    print(f"CRYPTO HOURLY IN ACCEPTING MARKETS: {len(crypto_hourly)}")
    print(f"{'='*60}")

    if crypto_hourly:
        print("\n✅ FOUND LIVE CRYPTO HOURLY MARKETS!")
        for m in crypto_hourly:
            print(f"  - {m.get('question')}")
    else:
        print("\n⚠️  No crypto hourly markets in the 13 accepting orders")
        print("   They might be in a different API response or paginated")

else:
    print("\n❌ No markets accepting orders in this response")

print(f"\n{'='*60}")
print("NEXT STEPS")
print(f"{'='*60}")

if accepting:
    print("\n✅ Found markets accepting orders!")
    print("   Update filter to use: active=True AND accepting_orders=True")
else:
    print("\n⚠️  Need to use API parameters or different endpoint")
    print("   Run: python test_api_params.py")
