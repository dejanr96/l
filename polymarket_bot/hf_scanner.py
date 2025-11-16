#!/usr/bin/env python3
"""
High-Frequency Arbitrage Scanner
Scans 10x per second with minimal output
"""

import time
import sys
from datetime import datetime
from polymarket_api import PolymarketAPI
import config

print("="*60)
print("⚡ HIGH-FREQUENCY ARBITRAGE SCANNER")
print("="*60)
print(f"Scan interval: {config.SCAN_INTERVAL}s ({1/config.SCAN_INTERVAL:.0f} scans/second)")
print(f"Min profit: ${config.MIN_ARBITRAGE_PROFIT:.4f}")
print(f"Starting balance: ${config.PAPER_STARTING_BALANCE:.2f}")
print("="*60)
print("\nPress Ctrl+C to stop\n")

api = PolymarketAPI()

# Stats
scan_count = 0
opportunities_found = 0
best_opportunity = None
last_market_count = 0

# Timing
start_time = time.time()
last_output_time = time.time()

def clear_line():
    """Clear the current line"""
    sys.stdout.write('\r' + ' ' * 100 + '\r')
    sys.stdout.flush()

def format_time(seconds):
    """Format seconds into human readable"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

try:
    while True:
        scan_count += 1
        scan_start = time.time()

        # Get markets
        markets = api.get_hourly_crypto_markets()

        if markets:
            last_market_count = len(markets)

            # Check each market for arbitrage
            for market in markets:
                outcome_prices = market.get('outcome_prices', [])

                if len(outcome_prices) >= 2:
                    yes_price = outcome_prices[0]
                    no_price = outcome_prices[1]
                    total_cost = yes_price + no_price

                    # Check for arbitrage
                    if total_cost < 1.0:
                        profit = 1.0 - total_cost

                        # Only report if above minimum threshold
                        if profit >= config.MIN_ARBITRAGE_PROFIT:
                            opportunities_found += 1
                            profit_pct = (profit / total_cost * 100)

                            # ALERT!
                            clear_line()
                            print(f"\n{'='*60}")
                            print(f"🔥 ARBITRAGE OPPORTUNITY #{opportunities_found}!")
                            print(f"{'='*60}")
                            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                            print(f"Market: {market.get('question', 'N/A')[:70]}")
                            print(f"YES: ${yes_price:.4f} | NO: ${no_price:.4f}")
                            print(f"Total: ${total_cost:.4f}")
                            print(f"💰 Profit: ${profit:.4f} ({profit_pct:.2f}%)")
                            print(f"{'='*60}\n")

                            # Track best
                            if best_opportunity is None or profit > best_opportunity['profit']:
                                best_opportunity = {
                                    'question': market.get('question'),
                                    'yes': yes_price,
                                    'no': no_price,
                                    'total': total_cost,
                                    'profit': profit,
                                    'profit_pct': profit_pct,
                                    'timestamp': datetime.now()
                                }

        # Calculate stats
        scan_duration = time.time() - scan_start
        elapsed = time.time() - start_time
        scans_per_sec = scan_count / elapsed if elapsed > 0 else 0

        # Update status line every 0.5 seconds
        current_time = time.time()
        if current_time - last_output_time >= 0.5:
            clear_line()

            status = (
                f"⚡ Scans: {scan_count:,} | "
                f"Rate: {scans_per_sec:.1f}/s | "
                f"Markets: {last_market_count} | "
                f"Opportunities: {opportunities_found} | "
                f"Runtime: {format_time(elapsed)} | "
                f"Last scan: {scan_duration*1000:.0f}ms"
            )

            sys.stdout.write(status)
            sys.stdout.flush()
            last_output_time = current_time

        # Wait for next scan
        wait_time = max(0, config.SCAN_INTERVAL - scan_duration)
        if wait_time > 0:
            time.sleep(wait_time)

except KeyboardInterrupt:
    clear_line()
    print("\n\n" + "="*60)
    print("🛑 STOPPING SCANNER")
    print("="*60)

    elapsed = time.time() - start_time

    print(f"\n📊 FINAL STATISTICS:")
    print(f"Total runtime: {format_time(elapsed)}")
    print(f"Total scans: {scan_count:,}")
    print(f"Average scan rate: {scan_count/elapsed:.2f} scans/second")
    print(f"Markets monitored: {last_market_count}")
    print(f"Opportunities found: {opportunities_found}")

    if best_opportunity:
        print(f"\n🏆 BEST OPPORTUNITY:")
        print(f"Market: {best_opportunity['question'][:70]}")
        print(f"Profit: ${best_opportunity['profit']:.4f} ({best_opportunity['profit_pct']:.2f}%)")
        print(f"Time: {best_opportunity['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n💡 No arbitrage opportunities found")
        print(f"   This is normal - markets are efficient!")
        print(f"   Keep running during high volatility periods")

    print("\n" + "="*60)
    print("Goodbye! 👋\n")

except Exception as e:
    clear_line()
    print(f"\n\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
