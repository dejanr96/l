#!/usr/bin/env python3
"""
Verify the bot is now fetching 1-HOUR markets instead of 4-hour markets
"""

from polymarket_api import PolymarketAPI
import re

print("="*60)
print("VERIFYING 1-HOUR MARKET FETCHING")
print("="*60)

api = PolymarketAPI()

print("\nFetching markets with updated tag_id=102127...\n")

markets = api.get_hourly_crypto_markets()

if not markets:
    print("❌ No markets found!")
else:
    print(f"\n{'='*60}")
    print("ANALYZING TIME INTERVALS")
    print(f"{'='*60}\n")

    intervals = []

    for i, market in enumerate(markets[:20], 1):  # Check first 20
        question = market.get('question', '')
        print(f"{i}. {question[:80]}")

        # Extract time range
        time_match = re.search(r'(\d+):00\s*([AP]M)\s*-\s*(\d+):00\s*([AP]M)', question, re.I)

        if time_match:
            start_hour = int(time_match.group(1))
            start_period = time_match.group(2).upper()
            end_hour = int(time_match.group(3))
            end_period = time_match.group(4).upper()

            # Convert to 24-hour
            if start_period == 'PM' and start_hour != 12:
                start_hour += 12
            elif start_period == 'AM' and start_hour == 12:
                start_hour = 0

            if end_period == 'PM' and end_hour != 12:
                end_hour += 12
            elif end_period == 'AM' and end_hour == 12:
                end_hour = 0

            # Calculate interval
            if end_hour < start_hour:
                interval = 24 - start_hour + end_hour
            else:
                interval = end_hour - start_hour

            intervals.append(interval)
            print(f"   → {interval} hour interval", end="")

            if interval == 1:
                print(" ✅ 1-HOUR!")
            elif interval == 4:
                print(" ❌ 4-HOUR (STILL WRONG!)")
            else:
                print(f" ⚠️  Unexpected")
        print()

    # Summary
    print(f"\n{'='*60}")
    print("VERDICT")
    print(f"{'='*60}\n")

    if intervals:
        one_hour = sum(1 for x in intervals if x == 1)
        four_hour = sum(1 for x in intervals if x == 4)
        avg = sum(intervals) / len(intervals)

        print(f"Total markets analyzed: {len(intervals)}")
        print(f"1-hour markets: {one_hour} ({one_hour/len(intervals)*100:.1f}%)")
        print(f"4-hour markets: {four_hour} ({four_hour/len(intervals)*100:.1f}%)")
        print(f"Average interval: {avg:.1f} hours")

        if one_hour > 0 and four_hour == 0:
            print(f"\n🎉 SUCCESS! Bot is now fetching 1-HOUR markets!")
            print(f"✅ Ready to replicate @FirstOrder's strategy!")
        elif four_hour > 0:
            print(f"\n❌ FAILED! Still fetching 4-hour markets")
            print(f"   tag_id=102127 might not be the right one")
        else:
            print(f"\n⚠️  Unexpected interval pattern")
    else:
        print("No time intervals found in market questions")
