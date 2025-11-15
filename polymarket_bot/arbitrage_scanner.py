"""
Arbitrage Opportunity Scanner
Continuously scans markets for arbitrage opportunities
"""

import time
from typing import List, Dict
from datetime import datetime
import config
from polymarket_api import create_api_client

class ArbitrageScanner:
    def __init__(self, use_mock=False):
        self.api = create_api_client(use_mock=use_mock)
        self.opportunities = []
        self.scan_count = 0

    def scan_for_opportunities(self) -> List[Dict]:
        """Scan all target markets for arbitrage opportunities"""
        self.scan_count += 1
        opportunities = []

        # Get hourly crypto markets
        markets = self.api.get_hourly_crypto_markets()

        print(f"\n{'='*60}")
        print(f"Scan #{self.scan_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Scanning {len(markets)} markets...")
        print(f"{'='*60}")

        for market in markets:
            market_id = market['id']
            question = market['question']

            # Get current prices
            prices = self.api.get_market_prices(market_id)

            # Calculate arbitrage
            arb = self.api.calculate_arbitrage(prices)

            if arb['is_opportunity']:
                opportunity = {
                    'market_id': market_id,
                    'question': question,
                    'timestamp': datetime.now(),
                    'yes_price': arb['yes_price'],
                    'no_price': arb['no_price'],
                    'total_cost': arb['total_cost'],
                    'profit': arb['guaranteed_profit'],
                    'profit_pct': arb['profit_pct'],
                    'recommended_size': self._calculate_position_size(arb)
                }

                opportunities.append(opportunity)

                # Alert!
                self._print_opportunity(opportunity)

        if not opportunities:
            print(f"No arbitrage opportunities found in this scan.")
        else:
            print(f"\n✅ Found {len(opportunities)} arbitrage opportunities!")

        self.opportunities = opportunities
        return opportunities

    def _calculate_position_size(self, arb: Dict) -> int:
        """Calculate optimal position size based on profit and risk"""
        # Simple position sizing based on profit margin
        profit_pct = arb['profit_pct']

        if profit_pct >= 10:  # Huge opportunity
            return config.MAX_POSITION_SIZE
        elif profit_pct >= 5:  # Good opportunity
            return config.STANDARD_POSITION_SIZE
        elif profit_pct >= 3:  # Decent opportunity
            return 100
        else:  # Small opportunity
            return 50

    def _print_opportunity(self, opp: Dict):
        """Print opportunity in a nice format"""
        print(f"\n🔥 ARBITRAGE OPPORTUNITY FOUND!")
        print(f"   Market: {opp['question']}")
        print(f"   YES Price: ${opp['yes_price']:.3f}")
        print(f"   NO Price:  ${opp['no_price']:.3f}")
        print(f"   Total Cost: ${opp['total_cost']:.3f}")
        print(f"   Guaranteed Profit: ${opp['profit']:.3f} ({opp['profit_pct']:.2f}%)")
        print(f"   Recommended Size: {opp['recommended_size']} shares")
        print(f"   Expected Profit: ${opp['profit'] * opp['recommended_size']:.2f}")

    def scan_continuously(self, interval=None):
        """Continuously scan for opportunities"""
        interval = interval or config.SCAN_INTERVAL

        print(f"\n{'='*60}")
        print(f"Starting continuous scanning...")
        print(f"Scan interval: {interval} seconds")
        print(f"Min profit required: {config.MIN_ARBITRAGE_PROFIT * 100}¢")
        print(f"{'='*60}")

        try:
            while True:
                self.scan_for_opportunities()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\nStopping scanner...")
            print(f"Total scans performed: {self.scan_count}")


class MarketMakerScanner:
    """
    Scans for market making opportunities
    Places limit orders at multiple price levels
    """

    def __init__(self, api):
        self.api = api

    def find_market_making_opportunities(self, market_id: str) -> List[Dict]:
        """Find optimal levels to place market making orders"""
        prices = self.api.get_market_prices(market_id)

        opportunities = []

        # Place orders at various levels on both sides
        for level in config.SPREAD_LEVELS:
            # YES side
            yes_opp = {
                'market_id': market_id,
                'side': 'YES',
                'price': level,
                'size': config.MARKET_MAKING_SIZE,
                'type': 'market_making'
            }
            opportunities.append(yes_opp)

            # NO side
            no_opp = {
                'market_id': market_id,
                'side': 'NO',
                'price': level,
                'size': config.MARKET_MAKING_SIZE,
                'type': 'market_making'
            }
            opportunities.append(no_opp)

        return opportunities


def main():
    """Test the scanner"""
    # Use mock API since real one is blocked
    scanner = ArbitrageScanner(use_mock=True)

    # Run a single scan
    print("Running test scan...")
    opportunities = scanner.scan_for_opportunities()

    if opportunities:
        print(f"\n{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(f"Total opportunities: {len(opportunities)}")
        total_potential = sum(o['profit'] * o['recommended_size'] for o in opportunities)
        print(f"Total potential profit: ${total_potential:.2f}")

    # Optionally run continuous scanning
    # scanner.scan_continuously(interval=10)


if __name__ == "__main__":
    main()
