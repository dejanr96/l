#!/usr/bin/env python3
"""
Find 1H tag using proper browser headers to avoid 403
"""

import requests
import json
import time

# Use browser-like headers to avoid 403
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://polymarket.com/',
    'Origin': 'https://polymarket.com'
}

print("="*60)
print("FINDING ALL TAGS FROM EVENTS (WITH BROWSER HEADERS)")
print("="*60)

print("\nFetching all open events to analyze their tags...")

time.sleep(2)  # Wait a bit to avoid rate limit

try:
    response = requests.get(
        "https://gamma-api.polymarket.com/events",
        params={
            'closed': 'false',
            'limit': '100'
        },
        headers=headers,
        timeout=10
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        events = response.json()
        print(f"✅ Got {len(events)} events")

        # Collect all unique tags
        all_tags = {}
        tag_to_events = {}

        for event in events:
            title = event.get('title', '')
            tags = event.get('tags', [])

            for tag in tags:
                if isinstance(tag, dict):
                    tag_id = tag.get('id')
                    tag_label = tag.get('label', '')
                    tag_slug = tag.get('slug', '')

                    if tag_id:
                        all_tags[tag_id] = tag

                        # Track which events have this tag
                        if tag_id not in tag_to_events:
                            tag_to_events[tag_id] = []
                        tag_to_events[tag_id].append(title)

        print(f"\n{'='*60}")
        print(f"FOUND {len(all_tags)} UNIQUE TAGS:")
        print(f"{'='*60}\n")

        # Sort by ID and display
        for tag_id in sorted(all_tags.keys()):
            tag = all_tags[tag_id]
            label = tag.get('label', 'N/A')
            slug = tag.get('slug', 'N/A')
            event_count = len(tag_to_events.get(tag_id, []))

            print(f"Tag ID: {tag_id:>10}  |  Label: {label:>10}  |  Slug: {slug:>10}  |  Events: {event_count}")

            # Highlight time-related tags
            if any(x in label.lower() for x in ['h', 'hour', 'time']) or \
               any(x in slug.lower() for x in ['h', 'hour', 'time']):
                print(f"  ⏰ TIME-RELATED TAG!")

                # Show sample events
                sample_events = tag_to_events.get(tag_id, [])[:3]
                for evt in sample_events:
                    print(f"    - {evt[:60]}")

            if '1h' in label.lower() or '1h' in slug.lower() or label == '1H':
                print(f"  🔥🔥🔥 THIS IS THE 1H TAG WE NEED! 🔥🔥🔥")

        print(f"\n{'='*60}")
        print("CRYPTO-SPECIFIC TAGS")
        print(f"{'='*60}\n")

        # Filter for crypto-related events
        crypto_events = []
        for event in events:
            title = event.get('title', '').lower()
            if any(token in title for token in ['bitcoin', 'ethereum', 'crypto', 'btc', 'eth', 'solana', 'xrp']):
                crypto_events.append(event)

        print(f"Found {len(crypto_events)} crypto events")

        # Collect tags from crypto events only
        crypto_tags = {}
        for event in crypto_events:
            tags = event.get('tags', [])
            for tag in tags:
                if isinstance(tag, dict):
                    tag_id = tag.get('id')
                    if tag_id:
                        crypto_tags[tag_id] = tag

        print(f"\nTags used in crypto events:")
        for tag_id in sorted(crypto_tags.keys()):
            tag = crypto_tags[tag_id]
            label = tag.get('label', 'N/A')
            slug = tag.get('slug', 'N/A')
            print(f"  {tag_id}: {label} ({slug})")

    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"Response: {response.text[:200]}")

except Exception as e:
    print(f"❌ Error: {e}")

print(f"\n{'='*60}")
print("RECOMMENDATION")
print(f"{'='*60}")
print("""
Once we find the 1H tag_id above, we'll update polymarket_api.py
to use that tag instead of 102531 (which is the 4H tag).
""")
