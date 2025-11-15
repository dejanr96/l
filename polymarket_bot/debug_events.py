#!/usr/bin/env python3
"""
Debug what events the API is returning
"""

import requests
import json

url = "https://gamma-api.polymarket.com/events"
params = {
    'tag_id': '102531',  # Crypto markets tag
    'closed': 'false',
    'limit': '100'
}

print("="*60)
print("DEBUGGING CRYPTO EVENTS")
print("="*60)

response = requests.get(url, params=params, timeout=10)

if response.status_code == 200:
    events = response.json()

    print(f"\nTotal events: {len(events)}")

    # Group by crypto
    btc_events = []
    eth_events = []
    sol_events = []
    xrp_events = []
    other_events = []

    for event in events:
        title = event.get('title', '').lower()

        if 'bitcoin' in title or 'btc' in title:
            btc_events.append(event)
        elif 'ethereum' in title or 'eth' in title:
            eth_events.append(event)
        elif 'solana' in title or 'sol' in title:
            sol_events.append(event)
        elif 'xrp' in title or 'ripple' in title:
            xrp_events.append(event)
        else:
            other_events.append(event)

    print(f"\nBreakdown:")
    print(f"  Bitcoin: {len(btc_events)}")
    print(f"  Ethereum: {len(eth_events)}")
    print(f"  Solana: {len(sol_events)}")
    print(f"  XRP: {len(xrp_events)}")
    print(f"  Other: {len(other_events)}")

    # Show samples
    if btc_events:
        print(f"\n✅ Bitcoin events:")
        for e in btc_events[:3]:
            print(f"  - {e.get('title')}")
    else:
        print(f"\n❌ No Bitcoin events found!")

    if eth_events:
        print(f"\n✅ Ethereum events:")
        for e in eth_events[:3]:
            print(f"  - {e.get('title')}")

    if sol_events:
        print(f"\n✅ Solana events:")
        for e in sol_events[:3]:
            print(f"  - {e.get('title')}")
    else:
        print(f"\n❌ No Solana events found!")

    if xrp_events:
        print(f"\n✅ XRP events:")
        for e in xrp_events[:3]:
            print(f"  - {e.get('title')}")
    else:
        print(f"\n❌ No XRP events found!")

    if other_events:
        print(f"\n📋 Other crypto events:")
        for e in other_events[:5]:
            print(f"  - {e.get('title')}")

    # Check markets inside events
    print(f"\n{'='*60}")
    print("CHECKING MARKETS IN EVENTS")
    print(f"{'='*60}")

    total_markets = 0
    for event in events:
        markets = event.get('markets', [])
        total_markets += len(markets)

    print(f"\nTotal markets across all events: {total_markets}")

    # Show first event's markets
    if events:
        first = events[0]
        print(f"\nFirst event: {first.get('title')}")
        print(f"Markets in first event: {len(first.get('markets', []))}")

        for m in first.get('markets', [])[:3]:
            print(f"  - {m.get('question', 'N/A')}")

else:
    print(f"❌ Error: {response.status_code}")

print(f"\n{'='*60}")
print("CONCLUSION")
print(f"{'='*60}")
print("""
If only Ethereum events are returned, it means:
1. tag_id=102531 might be Ethereum-specific tag
2. Need to find different tag_id for Bitcoin, Solana, XRP
3. Or there might be a different parameter to get all crypto

Check the website's Network tab for other requests with different tag_ids!
""")
