"""
Main Polymarket Arbitrage Bot
Combines scanner, paper trading, and monitoring
"""

import time
import sys
from datetime import datetime
from arbitrage_scanner import ArbitrageScanner
from paper_trader import PaperTradingEngine
import config

class PolymarketBot:
    def __init__(self, use_mock=False, starting_balance=None):
        print(f"\n{'='*60}")
        print(f"🤖 Polymarket Arbitrage Bot")
        print(f"{'='*60}")
        print(f"Mode: {'PAPER TRADING' if config.PAPER_TRADING else '⚠️  LIVE TRADING'}")
        print(f"API: {'MOCK (Testing)' if use_mock else 'REAL'}")
        print(f"Starting Balance: ${starting_balance or config.PAPER_STARTING_BALANCE:,.2f}")
        print(f"Min Arbitrage Profit: {config.MIN_ARBITRAGE_PROFIT * 100}¢")
        print(f"Scan Interval: {config.SCAN_INTERVAL}s")
        print(f"{'='*60}\n")

        self.scanner = ArbitrageScanner(use_mock=use_mock)
        self.trader = PaperTradingEngine(starting_balance=starting_balance)
        self.running = False
        self.auto_execute = False  # Manual approval by default

    def set_auto_execute(self, enabled=True):
        """Enable/disable automatic execution of opportunities"""
        self.auto_execute = enabled
        mode = "AUTO" if enabled else "MANUAL"
        print(f"\n⚙️  Execution mode set to: {mode}")

    def run_scan(self):
        """Run a single scan and optionally execute"""
        opportunities = self.scanner.scan_for_opportunities()

        if not opportunities:
            return

        print(f"\n{'='*60}")
        print(f"EXECUTION DECISION")
        print(f"{'='*60}")

        for i, opp in enumerate(opportunities, 1):
            print(f"\nOpportunity {i}/{len(opportunities)}:")
            print(f"  Market: {opp['question']}")
            print(f"  Profit: ${opp['profit']:.3f} ({opp['profit_pct']:.2f}%)")
            print(f"  Size: {opp['recommended_size']} shares")
            print(f"  Expected Profit: ${opp['profit'] * opp['recommended_size']:.2f}")

            if self.auto_execute:
                print(f"  Status: ✅ AUTO-EXECUTING...")
                result = self.trader.execute_arbitrage(opp)

                if not result['success']:
                    print(f"  Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"  Status: ⏸️  Waiting for manual approval")
                response = input(f"\n  Execute this trade? (y/n): ").lower()

                if response == 'y':
                    result = self.trader.execute_arbitrage(opp)

                    if not result['success']:
                        print(f"\n❌ Trade failed: {result.get('error', 'Unknown error')}")
                else:
                    print(f"  ⏭️  Skipped")

    def run_continuous(self, interval=None):
        """Run bot continuously"""
        interval = interval or config.SCAN_INTERVAL
        self.running = True

        print(f"\n{'='*60}")
        print(f"🚀 Starting continuous operation...")
        print(f"{'='*60}")
        print(f"Press Ctrl+C to stop\n")

        scan_count = 0

        try:
            while self.running:
                scan_count += 1

                print(f"\n{'='*60}")
                print(f"Scan #{scan_count} - {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*60}")

                self.run_scan()

                # Show portfolio every 10 scans
                if scan_count % 10 == 0:
                    self.trader.print_portfolio()

                print(f"\n⏳ Next scan in {interval} seconds...")
                time.sleep(interval)

        except KeyboardInterrupt:
            print(f"\n\n{'='*60}")
            print(f"🛑 Stopping bot...")
            print(f"{'='*60}")
            self.stop()

    def stop(self):
        """Stop the bot and show final results"""
        self.running = False

        print(f"\n{'='*60}")
        print(f"FINAL RESULTS")
        print(f"{'='*60}")

        self.trader.print_portfolio()

        # Save state
        self.trader.save_state()

        print(f"\n✅ Bot stopped successfully")

    def simulate_resolutions(self):
        """Manually trigger market resolutions for testing"""
        import random

        print(f"\n🎲 Simulating market resolutions...")

        for position in self.trader.positions:
            if position['status'] == 'open':
                # Randomly pick YES or NO
                outcome = random.choice(['YES', 'NO'])
                self.trader.simulate_market_resolution(
                    position['market_id'],
                    outcome
                )

        self.trader.print_portfolio()


def interactive_mode():
    """Interactive mode with menu"""
    print(f"\n{'='*60}")
    print(f"🤖 Polymarket Arbitrage Bot - Interactive Mode")
    print(f"{'='*60}")

    # Ask if using mock API
    print(f"\nAPI Selection:")
    print(f"1. Mock API (for testing - generates fake opportunities)")
    print(f"2. Real API (requires internet access)")

    api_choice = input(f"\nSelect API (1 or 2): ").strip()
    use_mock = (api_choice == '1')

    # Ask for starting balance
    balance_input = input(f"\nStarting balance (default ${config.PAPER_STARTING_BALANCE}): ").strip()
    starting_balance = float(balance_input) if balance_input else config.PAPER_STARTING_BALANCE

    # Create bot
    bot = PolymarketBot(use_mock=use_mock, starting_balance=starting_balance)

    while True:
        print(f"\n{'='*60}")
        print(f"MAIN MENU")
        print(f"{'='*60}")
        print(f"1. Run single scan")
        print(f"2. Run continuous (auto-scan)")
        print(f"3. Toggle auto-execute ({bot.auto_execute})")
        print(f"4. Show portfolio")
        print(f"5. Simulate market resolutions (for testing)")
        print(f"6. Save state")
        print(f"7. Load state")
        print(f"8. Exit")

        choice = input(f"\nSelect option: ").strip()

        if choice == '1':
            bot.run_scan()

        elif choice == '2':
            scan_interval = input(f"Scan interval in seconds (default {config.SCAN_INTERVAL}): ").strip()
            interval = int(scan_interval) if scan_interval else config.SCAN_INTERVAL
            bot.run_continuous(interval=interval)

        elif choice == '3':
            bot.set_auto_execute(not bot.auto_execute)

        elif choice == '4':
            bot.trader.print_portfolio()

        elif choice == '5':
            bot.simulate_resolutions()

        elif choice == '6':
            filename = input("Filename (default paper_trading_state.json): ").strip()
            filename = filename if filename else "paper_trading_state.json"
            bot.trader.save_state(filename)

        elif choice == '7':
            filename = input("Filename (default paper_trading_state.json): ").strip()
            filename = filename if filename else "paper_trading_state.json"
            bot.trader.load_state(filename)

        elif choice == '8':
            print(f"\n👋 Goodbye!")
            sys.exit(0)

        else:
            print(f"\n⚠️  Invalid option")


def quick_start():
    """Quick start with sensible defaults"""
    print(f"\n🚀 Quick Start Mode")
    print(f"Using: Mock API, $10k starting balance, Auto-execute ON")

    bot = PolymarketBot(use_mock=True, starting_balance=10000)
    bot.set_auto_execute(True)  # Enable auto-execute for quick mode

    print(f"\nRunning 5 test scans...")

    for i in range(5):
        bot.run_scan()
        time.sleep(2)

    bot.trader.print_portfolio()

    print(f"\n✅ Quick start complete!")
    print(f"\nTo run full bot, use: python bot.py")


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--quick':
            quick_start()
        elif sys.argv[1] == '--help':
            print("""
Polymarket Arbitrage Bot

Usage:
  python bot.py              # Interactive mode
  python bot.py --quick      # Quick test run
  python bot.py --help       # Show this help

The bot scans Polymarket for arbitrage opportunities and can execute
trades in paper trading mode (no real money).
            """)
    else:
        interactive_mode()
