#!/usr/bin/env python3
"""
Test arbitrage detection with the fixed API client
"""

from polymarket_api import PolymarketAPI
import json

print("="*60)
print("TESTING ARBITRAGE DETECTION")
print("="*60)

api = PolymarketAPI()

print("\n🔍 Fetching 1H crypto markets...\n")
markets = api.get_hourly_crypto_markets()

if not markets:
    print("❌ No markets found!")
else:
    print(f"✅ Found {len(markets)} markets accepting orders\n")

    print("="*60)
    print("CHECKING FOR ARBITRAGE OPPORTUNITIES")
    print("="*60)

    arbitrage_found = 0
    future_markets = []
    past_markets = []

    for i, market in enumerate(markets, 1):
        question = market.get('question', 'N/A')
        condition_id = market.get('condition_id', 'N/A')
        accepting_orders = market.get('acceptingOrders', False)

        # Get prices (now properly parsed from outcomePrices)
        outcome_prices = market.get('outcome_prices', [])

        if len(outcome_prices) >= 2:
            yes_price = outcome_prices[0]
            no_price = outcome_prices[1]
            total_cost = yes_price + no_price
            profit = 1.0 - total_cost
            profit_pct = (profit / total_cost * 100) if total_cost > 0 else 0

            print(f"\n{i}. {question[:70]}")
            print(f"   ID: {condition_id[:20]}...")
            print(f"   Accepting orders: {accepting_orders}")
            print(f"   💰 YES: ${yes_price:.4f} | NO: ${no_price:.4f}")
            print(f"   📊 Total: ${total_cost:.4f}")

            # Check for arbitrage
            if total_cost < 1.0:
                print(f"   🔥 ARBITRAGE! Profit: ${profit:.4f} ({profit_pct:.2f}%)")
                arbitrage_found += 1

                # Check if it's a future market or past market
                if yes_price > 0.95 or no_price > 0.95:
                    print(f"   ⚠️  Market likely resolved/resolving (one side >95%)")
                    past_markets.append({
                        'question': question,
                        'yes': yes_price,
                        'no': no_price,
                        'total': total_cost
                    })
                else:
                    print(f"   ✅ GENUINE ARBITRAGE OPPORTUNITY!")
                    future_markets.append({
                        'question': question,
                        'yes': yes_price,
                        'no': no_price,
                        'total': total_cost,
                        'profit': profit,
                        'profit_pct': profit_pct
                    })
            elif abs(total_cost - 1.0) < 0.001:
                print(f"   ⚖️  Perfectly priced (no opportunity)")
            else:
                print(f"   ❌ Over-priced: ${total_cost:.4f}")

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}\n")

    print(f"Total markets scanned: {len(markets)}")
    print(f"Arbitrage opportunities found: {arbitrage_found}")
    print(f"  - Genuine opportunities: {len(future_markets)}")
    print(f"  - Past/resolving markets: {len(past_markets)}")

    if future_markets:
        print(f"\n🔥 GENUINE ARBITRAGE OPPORTUNITIES:")
        for opp in future_markets:
            print(f"\n  Market: {opp['question'][:60]}")
            print(f"  YES: ${opp['yes']:.4f} | NO: ${opp['no']:.4f}")
            print(f"  Total: ${opp['total']:.4f}")
            print(f"  💰 Profit: ${opp['profit']:.4f} ({opp['profit_pct']:.2f}%)")

    elif arbitrage_found > 0:
        print(f"\n⚠️  All arbitrage opportunities are from past/resolving markets")
        print(f"    (Markets where one outcome is >95% likely)")

    else:
        print(f"\n✅ All markets are efficiently priced")
        print(f"   This is NORMAL - arbitrage is rare!")
        print(f"\n💡 Tips:")
        print(f"   - Run continuously to catch brief opportunities")
        print(f"   - Check during market creation (top of each hour)")
        print(f"   - Look for opportunities during high crypto volatility")

print(f"\n{'='*60}")
print("NEXT STEPS")
print(f"{'='*60}")
print("""
To run the full bot:
    python bot.py

Or for continuous monitoring:
    python bot.py --quick
""")
