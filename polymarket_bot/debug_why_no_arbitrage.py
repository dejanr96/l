#!/usr/bin/env python3
"""
Debug why the bot is not finding arbitrage opportunities
"""

from polymarket_api import PolymarketAPI
import re

print("="*60)
print("DEBUGGING: WHY NO ARBITRAGE OPPORTUNITIES?")
print("="*60)

api = PolymarketAPI()

print("\n🔍 Fetching 1H crypto markets...\n")
markets = api.get_hourly_crypto_markets()

if not markets:
    print("❌ NO MARKETS FOUND!")
    print("\nPossible reasons:")
    print("1. API returned 403 (rate limited)")
    print("2. tag_id=102127 has no events")
    print("3. No crypto markets match the filters")
    print("\nTry opening this URL in your browser:")
    print("https://gamma-api.polymarket.com/events?tag_id=102127&closed=false&limit=100")
else:
    print(f"✅ Found {len(markets)} markets\n")

    print("="*60)
    print("ANALYZING EACH MARKET")
    print("="*60)

    arbitrage_found = 0
    no_prices = 0
    perfectly_priced = 0
    close_but_no_cigar = []

    for i, market in enumerate(markets, 1):
        question = market.get('question', 'N/A')
        market_id = market.get('condition_id', 'N/A')
        active = market.get('active')
        closed = market.get('closed')
        accepting = market.get('accepting_orders')

        print(f"\n{i}. {question[:70]}")
        print(f"   ID: {market_id[:20]}...")
        print(f"   active={active}, closed={closed}, accepting_orders={accepting}")

        # Check if 1H market
        time_match = re.search(r'(\d+):00\s*([AP]M)\s*-\s*(\d+):00\s*([AP]M)', question, re.I)
        if time_match:
            start_hour = int(time_match.group(1))
            end_hour = int(time_match.group(3))
            # Simple check (doesn't handle PM/AM conversion)
            if abs(end_hour - start_hour) == 1 or abs(end_hour - start_hour) == 11:
                print(f"   ✅ 1-HOUR market")
            else:
                print(f"   ⚠️  Time interval: {abs(end_hour - start_hour)} hours")

        # Try to get prices
        outcome_prices = market.get('outcome_prices', [])

        if not outcome_prices or len(outcome_prices) < 2:
            print(f"   ❌ No prices available")
            no_prices += 1

            # Try to fetch orderbook
            print(f"   🔍 Attempting to fetch orderbook...")
            orderbook = api.get_orderbook(market_id)

            if orderbook and 'bids' in orderbook and 'asks' in orderbook:
                bids = orderbook.get('bids', [])
                asks = orderbook.get('asks', [])
                print(f"      Orderbook: {len(bids)} bids, {len(asks)} asks")

                if bids and asks:
                    best_bid = float(bids[0]['price']) if bids else None
                    best_ask = float(asks[0]['price']) if asks else None
                    print(f"      Best bid: ${best_bid}, Best ask: ${best_ask}")
            continue

        yes_price = float(outcome_prices[0]) if len(outcome_prices) > 0 else None
        no_price = float(outcome_prices[1]) if len(outcome_prices) > 1 else None

        if yes_price is None or no_price is None:
            print(f"   ❌ Invalid prices: YES={yes_price}, NO={no_price}")
            no_prices += 1
            continue

        total_cost = yes_price + no_price
        potential_profit = 1.0 - total_cost
        profit_percent = (potential_profit / total_cost * 100) if total_cost > 0 else 0

        print(f"   💰 Prices: YES=${yes_price:.4f}, NO=${no_price:.4f}")
        print(f"   📊 Total cost: ${total_cost:.4f}")
        print(f"   💵 Potential profit: ${potential_profit:.4f} ({profit_percent:.2f}%)")

        # Check for arbitrage (need total < $1.00)
        if total_cost < 1.0:
            print(f"   🔥 ARBITRAGE OPPORTUNITY!")
            arbitrage_found += 1
        elif abs(total_cost - 1.0) < 0.001:  # Within 0.1 cent
            print(f"   ⚖️  PERFECTLY PRICED (no opportunity)")
            perfectly_priced += 1
        else:
            print(f"   ❌ Over-priced (total > $1.00)")
            close_but_no_cigar.append({
                'question': question[:50],
                'total': total_cost,
                'over_by': total_cost - 1.0
            })

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}\n")

    print(f"Total markets analyzed: {len(markets)}")
    print(f"Markets with no prices: {no_prices}")
    print(f"Perfectly priced markets: {perfectly_priced}")
    print(f"Over-priced markets: {len(close_but_no_cigar)}")
    print(f"🔥 ARBITRAGE OPPORTUNITIES: {arbitrage_found}")

    if arbitrage_found == 0 and perfectly_priced > 0:
        print(f"\n💡 EXPLANATION:")
        print(f"   The markets are efficiently priced (YES + NO ≈ $1.00)")
        print(f"   This means there's no arbitrage opportunity right now.")
        print(f"   This is actually NORMAL for efficient markets!")
        print(f"\n   Arbitrage opportunities appear when:")
        print(f"   - New markets are created (not yet balanced)")
        print(f"   - Sudden news causes rapid price changes")
        print(f"   - Low liquidity markets have pricing gaps")
        print(f"   - Market makers haven't updated prices yet")

    if no_prices > 0:
        print(f"\n⚠️  WARNING: {no_prices} markets have no prices!")
        print(f"   These might be:")
        print(f"   - Too new (not yet accepting orders)")
        print(f"   - Closed/resolved")
        print(f"   - Low liquidity (no orders yet)")

    if close_but_no_cigar:
        print(f"\n📊 Over-priced markets (total > $1.00):")
        for item in close_but_no_cigar[:5]:
            print(f"   - {item['question']}: ${item['total']:.4f} (${item['over_by']:.4f} over)")

print(f"\n{'='*60}")
print("RECOMMENDATIONS")
print(f"{'='*60}")

print("""
1. Check market timing:
   - 1H markets might only be active at certain times
   - Try running this at different hours of the day

2. Monitor continuously:
   - Arbitrage opportunities are brief
   - Run the bot in a loop to catch them

3. Check @FirstOrder's activity:
   - See what times they were most active
   - Markets might be more mispriced during high volatility

4. Consider:
   - Transaction fees might eat small arbitrage profits
   - You need enough liquidity to execute both sides
   - Slippage on larger orders

5. If markets are perfectly priced:
   - This is NORMAL for efficient markets
   - Wait for market creation or volatility
   - Consider other strategies (not just arbitrage)
""")
