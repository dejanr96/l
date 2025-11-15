#!/usr/bin/env python3
"""
Test tag_id=102127 to verify it returns 1-HOUR markets (not 4-hour)
"""

import requests
import json
import re

print("="*60)
print("TESTING tag_id=102127 FOR 1-HOUR MARKETS")
print("="*60)

url = "https://gamma-api.polymarket.com/events"
params = {
    'tag_id': '102127',
    'closed': 'false',
    'limit': '100'
}

print(f"\nURL: {url}")
print(f"Params: {params}\n")

try:
    response = requests.get(url, params=params, timeout=10)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        events = response.json()
        print(f"✅ Got {len(events)} events\n")

        if events:
            # Check first event
            first = events[0]
            print(f"First event: {first.get('title')}")

            # Check tags
            tags = first.get('tags', [])
            print(f"\nTags in first event:")
            for tag in tags:
                print(f"  - ID: {tag.get('id')}, Label: {tag.get('label')}, Slug: {tag.get('slug')}")

                if tag.get('label') == '1H' or tag.get('slug') == '1h':
                    print(f"    🔥 CONFIRMED: This is a 1H tag!")

            # Check markets
            markets = first.get('markets', [])
            print(f"\nMarkets: {len(markets)}")

            print(f"\n{'='*60}")
            print("CHECKING TIME INTERVALS")
            print(f"{'='*60}\n")

            intervals = []

            for i, market in enumerate(markets[:10], 1):  # Check first 10
                question = market.get('question', '')
                print(f"{i}. {question}")

                # Extract time range to calculate interval
                time_match = re.search(r'(\d+):00\s*([AP]M)\s*-\s*(\d+):00\s*([AP]M)', question, re.I)

                if time_match:
                    start_hour = int(time_match.group(1))
                    start_period = time_match.group(2).upper()
                    end_hour = int(time_match.group(3))
                    end_period = time_match.group(4).upper()

                    # Convert to 24-hour format
                    if start_period == 'PM' and start_hour != 12:
                        start_hour += 12
                    elif start_period == 'AM' and start_hour == 12:
                        start_hour = 0

                    if end_period == 'PM' and end_hour != 12:
                        end_hour += 12
                    elif end_period == 'AM' and end_hour == 12:
                        end_hour = 0

                    # Calculate interval (handle midnight wrap)
                    if end_hour < start_hour:
                        interval = 24 - start_hour + end_hour
                    else:
                        interval = end_hour - start_hour

                    intervals.append(interval)
                    print(f"   → Time interval: {interval} hour(s)")

                    if interval == 1:
                        print(f"   ✅ 1-HOUR MARKET!")
                    elif interval == 4:
                        print(f"   ❌ 4-HOUR MARKET (wrong tag!)")

            # Summary
            print(f"\n{'='*60}")
            print("SUMMARY")
            print(f"{'='*60}\n")

            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                one_hour_count = sum(1 for x in intervals if x == 1)
                four_hour_count = sum(1 for x in intervals if x == 4)

                print(f"Markets checked: {len(intervals)}")
                print(f"1-hour markets: {one_hour_count}")
                print(f"4-hour markets: {four_hour_count}")
                print(f"Average interval: {avg_interval:.1f} hours")

                if one_hour_count > 0 and four_hour_count == 0:
                    print(f"\n🎉 SUCCESS! tag_id=102127 returns 1-HOUR markets!")
                    print(f"✅ This is the correct tag_id to use in the bot!")
                elif four_hour_count > 0:
                    print(f"\n❌ WRONG! This still returns 4-hour markets")
                else:
                    print(f"\n⚠️  Unexpected interval: {avg_interval} hours")
        else:
            print("⚠️  No events returned")

    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text[:200]}")

except Exception as e:
    print(f"❌ Error: {e}")

print(f"\n{'='*60}")
print("NEXT STEP")
print(f"{'='*60}")
print("""
If this shows 1-hour markets, update polymarket_api.py:
- Line 168: Change 'tag_id': '102531' to 'tag_id': '102127'
""")
