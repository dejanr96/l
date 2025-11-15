#!/usr/bin/env python3
"""
Continuous Arbitrage Monitor
Runs every 10 seconds to catch brief arbitrage opportunities
"""

import time
from datetime import datetime
from polymarket_api import PolymarketAPI
import json

print("="*60)
print("🤖 CONTINUOUS ARBITRAGE MONITOR")
print("="*60)
print("\nThis will check for arbitrage every 10 seconds.")
print("Press Ctrl+C to stop.\n")

api = PolymarketAPI()

# Stats
total_checks = 0
total_opportunities = 0
best_opportunity = None
opportunities_log = []

def check_for_arbitrage():
    """Check markets for arbitrage opportunities"""
    global total_checks, total_opportunities, best_opportunity

    total_checks += 1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n[{timestamp}] Check #{total_checks}")
    print("-" * 60)

    try:
        markets = api.get_hourly_crypto_markets()

        if not markets:
            print("⚠️  No markets found (might be rate limited)")
            return []

        print(f"📊 Scanning {len(markets)} markets...")

        opportunities = []

        for market in markets:
            question = market.get('question', 'N/A')
            outcome_prices = market.get('outcome_prices', [])

            if not outcome_prices or len(outcome_prices) < 2:
                continue

            yes_price = float(outcome_prices[0])
            no_price = float(outcome_prices[1])
            total_cost = yes_price + no_price

            # Check for arbitrage (total < $1.00)
            if total_cost < 1.0:
                profit = 1.0 - total_cost
                profit_percent = (profit / total_cost * 100)

                opportunity = {
                    'timestamp': timestamp,
                    'question': question,
                    'yes_price': yes_price,
                    'no_price': no_price,
                    'total_cost': total_cost,
                    'profit': profit,
                    'profit_percent': profit_percent
                }

                opportunities.append(opportunity)

                # Track best
                if best_opportunity is None or profit_percent > best_opportunity['profit_percent']:
                    best_opportunity = opportunity

        if opportunities:
            total_opportunities += len(opportunities)
            print(f"\n🔥 FOUND {len(opportunities)} ARBITRAGE OPPORTUNITIES! 🔥\n")

            for opp in opportunities:
                print(f"📈 {opp['question'][:60]}")
                print(f"   YES: ${opp['yes_price']:.4f} | NO: ${opp['no_price']:.4f}")
                print(f"   Total: ${opp['total_cost']:.4f}")
                print(f"   💰 Profit: ${opp['profit']:.4f} ({opp['profit_percent']:.2f}%)")
                print()

                # Log to file
                opportunities_log.append(opp)
                with open('arbitrage_log.json', 'w') as f:
                    json.dump(opportunities_log, f, indent=2)

        else:
            print("✅ All markets efficiently priced (no arbitrage)")

        return opportunities

    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def show_stats():
    """Display running statistics"""
    print("\n" + "="*60)
    print("📊 SESSION STATISTICS")
    print("="*60)
    print(f"Total checks: {total_checks}")
    print(f"Opportunities found: {total_opportunities}")
    print(f"Hit rate: {(total_opportunities/total_checks*100) if total_checks > 0 else 0:.2f}%")

    if best_opportunity:
        print(f"\n🏆 BEST OPPORTUNITY:")
        print(f"   {best_opportunity['question'][:60]}")
        print(f"   Profit: ${best_opportunity['profit']:.4f} ({best_opportunity['profit_percent']:.2f}%)")
        print(f"   Time: {best_opportunity['timestamp']}")

    if opportunities_log:
        print(f"\n📁 All opportunities logged to: arbitrage_log.json")

    print("="*60)


# Main monitoring loop
try:
    while True:
        opportunities = check_for_arbitrage()

        # Show stats every 10 checks
        if total_checks % 10 == 0:
            show_stats()

        # Wait 10 seconds before next check
        print(f"\n⏳ Waiting 10 seconds... (Ctrl+C to stop)")
        time.sleep(10)

except KeyboardInterrupt:
    print("\n\n🛑 Monitoring stopped by user\n")
    show_stats()
    print("\nGoodbye! 👋\n")

except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    show_stats()
