#!/usr/bin/env python3
"""
Try to discover all available tags from the Polymarket API
"""

import requests
import json
import time

print("="*60)
print("DISCOVERING AVAILABLE TAGS")
print("="*60)

# Try common API endpoints that might list tags
endpoints = [
    "https://gamma-api.polymarket.com/tags",
    "https://gamma-api.polymarket.com/tag",
    "https://gamma-api.polymarket.com/events/tags",
    "https://gamma-api.polymarket.com/markets/tags",
]

for url in endpoints:
    print(f"\nTrying: {url}")
    try:
        response = requests.get(url, timeout=10)
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Success!")
            print(f"  Response type: {type(data)}")

            if isinstance(data, list):
                print(f"  Items: {len(data)}")
                if data:
                    print(f"  Sample: {json.dumps(data[0], indent=2)}")

                    # Look for 1H tag
                    for item in data:
                        if isinstance(item, dict):
                            label = item.get('label', '')
                            slug = item.get('slug', '')
                            if '1h' in label.lower() or '1h' in slug.lower():
                                print(f"  🔥 FOUND 1H TAG: {item}")

            elif isinstance(data, dict):
                print(f"  Keys: {list(data.keys())}")
                print(f"  Sample: {json.dumps(data, indent=2)[:500]}")

        time.sleep(1)  # Be nice to API

    except Exception as e:
        print(f"  Error: {e}")

print(f"\n{'='*60}")
print("ANALYZING EXISTING EVENTS FOR TAG PATTERNS")
print(f"{'='*60}")

# Fetch a bunch of events and collect all unique tags
print("\nFetching events to analyze tag patterns...")

try:
    # Try without tag_id filter to get all events
    response = requests.get(
        "https://gamma-api.polymarket.com/events",
        params={'closed': 'false', 'limit': '100'},
        timeout=10
    )

    if response.status_code == 200:
        events = response.json()
        print(f"✅ Got {len(events)} events")

        # Collect all unique tags
        all_tags = {}

        for event in events:
            tags = event.get('tags', [])
            for tag in tags:
                if isinstance(tag, dict):
                    tag_id = tag.get('id')
                    if tag_id:
                        all_tags[tag_id] = tag

        print(f"\n📋 Found {len(all_tags)} unique tags:")
        print("-" * 60)

        # Sort by ID and display
        for tag_id in sorted(all_tags.keys()):
            tag = all_tags[tag_id]
            label = tag.get('label', 'N/A')
            slug = tag.get('slug', 'N/A')
            print(f"  ID: {tag_id:>10}  |  Label: {label:>10}  |  Slug: {slug}")

            if '1h' in label.lower() or '1h' in slug.lower():
                print(f"    🔥 THIS IS THE 1H TAG!")
    else:
        print(f"❌ Failed: {response.status_code}")

except Exception as e:
    print(f"❌ Error: {e}")

print(f"\n{'='*60}")
print("NEXT STEP")
print(f"{'='*60}")
print("""
If we found the 1H tag above, we can update the bot!

If not, please check browser DevTools on:
https://polymarket.com/crypto?tab=hourly

Look for the API call that loads 1-hour markets and check its tag_id parameter.
""")
