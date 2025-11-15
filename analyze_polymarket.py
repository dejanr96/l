#!/usr/bin/env python3
"""
Polymarket Trading Strategy Analyzer
Analyzes prediction market trading patterns and strategies
"""

import requests
import json
from datetime import datetime
from collections import defaultdict, Counter

class PolymarketAnalyzer:
    def __init__(self, address):
        self.address = address.lower()
        self.base_url = "https://gamma-api.polymarket.com"
        self.clob_api = "https://clob.polymarket.com"

    def get_user_profile(self):
        """Get user profile and stats"""
        print(f"\n{'='*60}")
        print(f"POLYMARKET TRADER ANALYSIS")
        print(f"{'='*60}\n")
        print(f"Address: {self.address}")

        # Try to get user data
        try:
            # Get user's markets
            url = f"{self.clob_api}/positions"
            params = {'user': self.address}
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                positions = response.json()
                print(f"\n✓ Found {len(positions)} positions")
                return positions
            else:
                print(f"Status: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def get_order_history(self):
        """Get order history for the user"""
        try:
            url = f"{self.clob_api}/orders"
            params = {'maker': self.address}
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                orders = response.json()
                print(f"✓ Found {len(orders)} orders")
                return orders
            else:
                print(f"Order history status: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_trades(self):
        """Get trade history"""
        try:
            url = f"{self.clob_api}/trades"
            params = {'maker': self.address}
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                trades = response.json()
                print(f"✓ Found {len(trades)} trades")
                return trades
            else:
                print(f"Trades status: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def analyze_positions(self, positions):
        """Analyze current positions"""
        if not positions:
            return

        print(f"\n{'='*60}")
        print("POSITION ANALYSIS")
        print(f"{'='*60}\n")

        total_value = 0
        markets = []

        for pos in positions:
            market = pos.get('market', 'Unknown')
            outcome = pos.get('outcome', 'Unknown')
            size = float(pos.get('size', 0))
            value = float(pos.get('value', 0))

            markets.append(market)
            total_value += value

            print(f"\nMarket: {market}")
            print(f"  Outcome: {outcome}")
            print(f"  Size: {size:.2f}")
            print(f"  Value: ${value:.2f}")

        print(f"\nTotal portfolio value: ${total_value:.2f}")
        print(f"Number of markets: {len(set(markets))}")

    def analyze_trading_pattern(self, trades):
        """Analyze trading patterns and strategy"""
        if not trades:
            return

        print(f"\n{'='*60}")
        print("TRADING PATTERN ANALYSIS")
        print(f"{'='*60}\n")

        # Analyze by market category
        categories = Counter()
        sides = Counter()
        total_volume = 0

        for trade in trades:
            market = trade.get('market', 'Unknown')
            side = trade.get('side', 'unknown')
            size = float(trade.get('size', 0))
            price = float(trade.get('price', 0))

            categories[market] += 1
            sides[side] += 1
            total_volume += size * price

        print(f"Total trading volume: ${total_volume:.2f}")
        print(f"\nMost traded markets:")
        for market, count in categories.most_common(10):
            print(f"  {market}: {count} trades")

        print(f"\nTrading sides:")
        for side, count in sides.items():
            print(f"  {side}: {count} trades")

    def identify_strategy(self, positions, trades):
        """Identify likely trading strategy"""
        print(f"\n{'='*60}")
        print("STRATEGY IDENTIFICATION")
        print(f"{'='*60}\n")

        strategies = []

        if not positions and not trades:
            print("Unable to identify strategy - no data available")
            return strategies

        # Analyze position diversity
        if positions:
            unique_markets = len(set(p.get('market', '') for p in positions))

            if unique_markets > 20:
                strategies.append("Diversified portfolio - betting on many markets")
            elif unique_markets < 5:
                strategies.append("Focused strategy - specializing in few markets")

        # Analyze trade frequency
        if trades:
            if len(trades) > 100:
                strategies.append("High-frequency trader - very active")
            elif len(trades) < 10:
                strategies.append("Low-frequency trader - selective bets")

        print("IDENTIFIED PATTERNS:")
        if strategies:
            for strategy in strategies:
                print(f"  • {strategy}")
        else:
            print("  • Strategy unclear from available data")

        return strategies

def analyze_polymarket_from_polygonscan(address):
    """Guide for analyzing Polymarket activity via PolygonScan"""
    print(f"\n{'='*60}")
    print("POLYMARKET ANALYSIS VIA POLYGONSCAN")
    print(f"{'='*60}\n")

    print("Since Polymarket runs on Polygon, analyze on-chain activity:\n")

    print("1. Visit PolygonScan:")
    print(f"   https://polygonscan.com/address/{address}\n")

    print("2. Look for Polymarket contract interactions:")
    print("   Common Polymarket contracts:")
    print("   - CTF Exchange: 0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E")
    print("   - Conditional Tokens: 0x4D97DCd97eC945f40cF65F87097ACe5EA0476045")
    print("   - USDC (for bets): 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174\n")

    print("3. What to look for in Token Transfers:")
    print("   - USDC OUT → Placing bets")
    print("   - USDC IN → Winning payouts or position sales")
    print("   - CTF tokens → Conditional token positions\n")

    print("4. Trading patterns:")
    print("   - High USDC volume → Large bettor")
    print("   - Frequent small bets → Market making or arbitrage")
    print("   - Large single bets → Conviction plays")
    print("   - Quick in/out → Arbitrage or short-term trading\n")

    print("5. Strategy indicators:")
    print("   - Many different CTF tokens → Diversified across markets")
    print("   - Few tokens, high volume → Focused on specific events")
    print("   - Quick flips → Trading on odds changes, not event outcomes")
    print("   - Long holds → Conviction-based betting on actual events\n")

def main():
    address = "0xeffcc79a8572940cee2238b44eac89f2c48fda88"

    print("""
╔══════════════════════════════════════════════════════════╗
║     POLYMARKET PREDICTION MARKET STRATEGY ANALYZER       ║
╚══════════════════════════════════════════════════════════╝
""")

    print("Polymarket is a prediction market platform where users bet on")
    print("future events using USDC on the Polygon network.\n")

    analyzer = PolymarketAnalyzer(address)

    # Try to get data from Polymarket API
    positions = analyzer.get_user_profile()
    trades = analyzer.get_trades()

    if positions or trades:
        analyzer.analyze_positions(positions)
        analyzer.analyze_trading_pattern(trades)
        analyzer.identify_strategy(positions, trades)
    else:
        print("\n⚠️ Unable to fetch data from Polymarket API")
        print("Falling back to PolygonScan analysis guide...\n")
        analyze_polymarket_from_polygonscan(address)

    print(f"\n{'='*60}")
    print("NEXT STEPS")
    print(f"{'='*60}\n")

    print("For manual analysis:")
    print("1. Visit the Polymarket profile:")
    print("   https://polymarket.com/@FirstOrder")
    print("\n2. Check PolygonScan for on-chain activity:")
    print(f"   https://polygonscan.com/address/{address}")
    print("\n3. Look for:")
    print("   - Which markets they bet on (sports, politics, crypto?)")
    print("   - Average bet sizes")
    print("   - Win rate (if visible)")
    print("   - Time patterns (when they place bets)")
    print("   - Quick flips vs long holds")

if __name__ == "__main__":
    main()
