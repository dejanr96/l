"""
Monitoring Dashboard
Real-time visualization of bot performance
"""

import time
import os
from datetime import datetime
from paper_trader import PaperTradingEngine
from arbitrage_scanner import ArbitrageScanner

class Dashboard:
    def __init__(self, trader: PaperTradingEngine, scanner: ArbitrageScanner):
        self.trader = trader
        self.scanner = scanner

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display(self):
        """Display full dashboard"""
        self.clear_screen()

        summary = self.trader.get_portfolio_summary()

        print(f"\n{'='*80}")
        print(f"  🤖 POLYMARKET ARBITRAGE BOT - LIVE DASHBOARD")
        print(f"{'='*80}")

        # Header with time
        print(f"\n  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  🔄 Scan #{self.scanner.scan_count}")

        # Balance Section
        print(f"\n{'─'*80}")
        print(f"  💰 BALANCE")
        print(f"{'─'*80}")
        print(f"  Starting:  ${summary['starting_balance']:>12,.2f}")
        print(f"  Current:   ${summary['current_balance']:>12,.2f}")
        print(f"  Available: ${summary['current_balance']:>12,.2f}")

        # Profit Section
        print(f"\n{'─'*80}")
        print(f"  📈 PROFIT & LOSS")
        print(f"{'─'*80}")
        print(f"  Realized:    ${summary['realized_profit']:>10,.2f}")
        print(f"  Unrealized:  ${summary['unrealized_profit']:>10,.2f}")
        print(f"  Total:       ${summary['total_profit']:>10,.2f}")
        print(f"  Return:      {summary['total_return_pct']:>10.2f}%")

        # Positions Section
        print(f"\n{'─'*80}")
        print(f"  📊 POSITIONS")
        print(f"{'─'*80}")
        print(f"  Open:        {summary['open_positions']:>10}")
        print(f"  Value:       ${summary['open_positions_value']:>10,.2f}")
        print(f"  Expected P:  ${summary['open_positions_expected_profit']:>10,.2f}")
        print(f"  Closed:      {summary['closed_positions']:>10}")

        # Trading Stats
        print(f"\n{'─'*80}")
        print(f"  📉 TRADING STATS")
        print(f"{'─'*80}")
        print(f"  Total Trades: {summary['total_trades']:>9}")
        print(f"  Wins:         {summary['win_count']:>9}")
        print(f"  Losses:       {summary['loss_count']:>9}")
        print(f"  Win Rate:     {summary['win_rate']:>8.1f}%")

        # Recent Positions
        if self.trader.positions:
            print(f"\n{'─'*80}")
            print(f"  🔥 OPEN POSITIONS (Last 5)")
            print(f"{'─'*80}")

            for position in self.trader.positions[-5:]:
                profit = position['guaranteed_profit']
                profit_pct = position['profit_pct']
                size = position['size']

                # Truncate question
                question = position['question'][:50]

                print(f"  • {question}")
                print(f"    Size: {size} | Cost: ${position['total_cost']:.2f} | " +
                      f"Profit: ${profit:.2f} ({profit_pct:.1f}%)")

        # Recent Opportunities
        if self.scanner.opportunities:
            print(f"\n{'─'*80}")
            print(f"  🎯 LATEST OPPORTUNITIES")
            print(f"{'─'*80}")

            for opp in self.scanner.opportunities[:3]:
                question = opp['question'][:50]
                profit = opp['profit']
                profit_pct = opp['profit_pct']

                print(f"  • {question}")
                print(f"    Profit: ${profit:.3f} ({profit_pct:.2f}%) | " +
                      f"Size: {opp['recommended_size']} shares")

        print(f"\n{'='*80}")
        print(f"  Press Ctrl+C to stop")
        print(f"{'='*80}\n")

    def run_live(self, update_interval=5):
        """Run live updating dashboard"""
        try:
            while True:
                self.display()
                time.sleep(update_interval)
        except KeyboardInterrupt:
            print(f"\n\n  Dashboard stopped.")


def create_simple_report(trader: PaperTradingEngine) -> str:
    """Create a simple text report"""
    summary = trader.get_portfolio_summary()

    report = f"""
╔══════════════════════════════════════════════════════════╗
║        POLYMARKET BOT - PERFORMANCE REPORT              ║
╚══════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BALANCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Starting Balance:    ${summary['starting_balance']:>12,.2f}
Current Balance:     ${summary['current_balance']:>12,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROFIT & LOSS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Realized Profit:     ${summary['realized_profit']:>12,.2f}
Unrealized Profit:   ${summary['unrealized_profit']:>12,.2f}
Total Profit:        ${summary['total_profit']:>12,.2f}
Total Return:        {summary['total_return_pct']:>11.2f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POSITIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Open Positions:      {summary['open_positions']:>12}
Open Value:          ${summary['open_positions_value']:>12,.2f}
Expected Profit:     ${summary['open_positions_expected_profit']:>12,.2f}
Closed Positions:    {summary['closed_positions']:>12}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRADING STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Trades:        {summary['total_trades']:>12}
Winning Trades:      {summary['win_count']:>12}
Losing Trades:       {summary['loss_count']:>12}
Win Rate:            {summary['win_rate']:>11.1f}%

╚══════════════════════════════════════════════════════════╝
"""
    return report


def save_report(trader: PaperTradingEngine, filename="bot_report.txt"):
    """Save performance report to file"""
    report = create_simple_report(trader)

    with open(filename, 'w') as f:
        f.write(report)

    print(f"\n📊 Report saved to {filename}")


if __name__ == "__main__":
    # Test the dashboard with mock data
    from paper_trader import PaperTradingEngine

    trader = PaperTradingEngine(10000)

    # Create mock position
    mock_position = {
        'position_id': 'test1',
        'market_id': 'btc_test',
        'question': 'Bitcoin Up or Down - November 15, 4PM ET',
        'type': 'arbitrage',
        'total_cost': 93,
        'size': 100,
        'guaranteed_profit': 7,
        'profit_pct': 7.5,
        'opened_at': datetime.now(),
        'status': 'open'
    }

    trader.positions.append(mock_position)

    # Generate report
    report = create_simple_report(trader)
    print(report)

    save_report(trader, "test_report.txt")
