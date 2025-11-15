#!/usr/bin/env python3
"""
Find the correct tag_id for 1-HOUR crypto markets (not 4-hour)
tag_id=102531 is for 4H markets - we need to find 1H!
"""

import requests
import json

print("="*60)
print("FINDING 1-HOUR CRYPTO MARKET TAG")
print("="*60)

# Try different tag_ids to find the 1H markets
# Based on the pattern: tag_id=102531 is "4H"
# There should be a different tag for "1H"

test_tags = [
    ('102531', '4H (known)'),
    ('102530', '1H? (guess -1)'),
    ('102532', '2H? (guess +1)'),
    ('102529', '1H? (guess -2)'),
    # Try some common patterns
    ('102500', '1H? (round number)'),
    ('102501', '1H? (round +1)'),
]

base_url = "https://gamma-api.polymarket.com/events"

print("\nTesting different tag_ids to find 1-hour markets...\n")

for tag_id, description in test_tags:
    print(f"\nTesting tag_id={tag_id} ({description})")
    print("-" * 40)

    try:
        response = requests.get(
            base_url,
            params={
                'tag_id': tag_id,
                'closed': 'false',
                'limit': '10'
            },
            timeout=10
        )

        if response.status_code != 200:
            print(f"  ❌ Failed: {response.status_code}")
            continue

        events = response.json()

        if not isinstance(events, list):
            print(f"  ⚠️  Not a list: {type(events)}")
            continue

        print(f"  ✅ Got {len(events)} events")

        if events:
            # Check first event
            first = events[0]
            title = first.get('title', 'N/A')
            tags = first.get('tags', [])

            print(f"  Title: {title[:60]}")
            print(f"  Tags: {tags}")

            # Check if it has 1H tag
            has_1h = any(tag.get('label') == '1H' or tag.get('slug') == '1h'
                        for tag in tags if isinstance(tag, dict))
            has_4h = any(tag.get('label') == '4H' or tag.get('slug') == '4h'
                        for tag in tags if isinstance(tag, dict))

            if has_1h:
                print(f"  🔥 FOUND 1H TAG!")
            if has_4h:
                print(f"  (This is 4H)")

            # Show markets to check time intervals
            markets = first.get('markets', [])
            if markets:
                print(f"  Markets: {len(markets)}")
                for m in markets[:2]:
                    q = m.get('question', '')
                    print(f"    - {q[:70]}")

                    # Check if 1-hour interval by looking at time range
                    # 1H: "4:00PM-5:00PM" or "5:00PM-6:00PM"
                    # 4H: "4:00PM-8:00PM" or "8:00PM-12:00AM"
                    if 'pm-' in q.lower() or 'am-' in q.lower():
                        # Extract time range
                        import re
                        time_match = re.search(r'(\d+):00([AP]M)-(\d+):00([AP]M)', q, re.I)
                        if time_match:
                            start_hour = int(time_match.group(1))
                            start_period = time_match.group(2).upper()
                            end_hour = int(time_match.group(3))
                            end_period = time_match.group(4).upper()

                            # Calculate hour difference
                            if start_period == end_period:
                                diff = end_hour - start_hour
                            else:
                                diff = 12 - start_hour + end_hour

                            print(f"      → {diff} hour interval")

                            if diff == 1:
                                print(f"      🎯 THIS IS A 1-HOUR MARKET!")
        else:
            print(f"  ⚠️  No events returned")

    except Exception as e:
        print(f"  ❌ Error: {e}")

print(f"\n{'='*60}")
print("ALTERNATIVE: SEARCH ALL TAGS")
print(f"{'='*60}")

print("""
If the above didn't find it, we need to:

1. Check the Polymarket website at:
   https://polymarket.com/crypto?tab=hourly

2. Open DevTools → Network tab

3. Look for the API call that loads 1-hour markets

4. Check the tag_id parameter in that request

The website definitely has 1-hour markets - we just need to find
which tag_id they use!
""")
