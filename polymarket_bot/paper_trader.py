"""
Paper Trading Engine
Simulates real trading without risking actual money
"""

import time
import json
from typing import Dict, List
from datetime import datetime
from collections import defaultdict
import config

class PaperTradingEngine:
    def __init__(self, starting_balance=None):
        self.starting_balance = starting_balance or config.PAPER_STARTING_BALANCE
        self.balance = self.starting_balance
        self.positions = []  # Open positions
        self.closed_positions = []  # Historical positions
        self.trades = []  # All trades
        self.pnl_history = []

    def execute_arbitrage(self, opportunity: Dict) -> Dict:
        """Execute an arbitrage trade (buy both YES and NO)"""
        market_id = opportunity['market_id']
        size = opportunity['recommended_size']
        yes_price = opportunity['yes_price']
        no_price = opportunity['no_price']

        # Calculate costs with slippage
        slippage = config.PAPER_SLIPPAGE
        yes_cost = yes_price * (1 + slippage) * size
        no_cost = no_price * (1 + slippage) * size
        total_cost = yes_cost + no_cost

        # Check if we have enough balance
        if total_cost > self.balance:
            return {
                'success': False,
                'error': 'Insufficient balance',
                'required': total_cost,
                'available': self.balance
            }

        # Execute trades
        yes_trade = {
            'market_id': market_id,
            'question': opportunity['question'],
            'side': 'YES',
            'price': yes_price * (1 + slippage),
            'size': size,
            'cost': yes_cost,
            'timestamp': datetime.now(),
            'trade_id': f"trade_{len(self.trades) + 1}"
        }

        no_trade = {
            'market_id': market_id,
            'question': opportunity['question'],
            'side': 'NO',
            'price': no_price * (1 + slippage),
            'size': size,
            'cost': no_cost,
            'timestamp': datetime.now(),
            'trade_id': f"trade_{len(self.trades) + 2}"
        }

        # Update balance
        self.balance -= total_cost

        # Record trades
        self.trades.append(yes_trade)
        self.trades.append(no_trade)

        # Create arbitrage position
        position = {
            'position_id': f"arb_{len(self.positions) + 1}",
            'market_id': market_id,
            'question': opportunity['question'],
            'type': 'arbitrage',
            'yes_trade': yes_trade,
            'no_trade': no_trade,
            'total_cost': total_cost,
            'size': size,
            'guaranteed_profit': (size - total_cost),  # $1 per share payout
            'profit_pct': ((size - total_cost) / total_cost) * 100,
            'opened_at': datetime.now(),
            'status': 'open'
        }

        self.positions.append(position)

        print(f"\n✅ ARBITRAGE EXECUTED (Paper Trading)")
        print(f"   Market: {opportunity['question']}")
        print(f"   Bought {size} YES @ ${yes_trade['price']:.4f} = ${yes_cost:.2f}")
        print(f"   Bought {size} NO @ ${no_trade['price']:.4f} = ${no_cost:.2f}")
        print(f"   Total Cost: ${total_cost:.2f}")
        print(f"   Guaranteed Profit: ${position['guaranteed_profit']:.2f}")
        print(f"   New Balance: ${self.balance:.2f}")

        return {
            'success': True,
            'position': position,
            'balance': self.balance
        }

    def simulate_market_resolution(self, market_id: str, outcome: str):
        """Simulate a market resolving (YES or NO wins)"""
        # Find all positions for this market
        market_positions = [p for p in self.positions if p['market_id'] == market_id and p['status'] == 'open']

        for position in market_positions:
            if position['type'] == 'arbitrage':
                # For arbitrage, we win on one side and lose on the other
                # But guaranteed profit because we bought both
                size = position['size']
                total_cost = position['total_cost']
                payout = size * 1.0  # $1 per share

                profit = payout - total_cost
                profit_pct = (profit / total_cost) * 100

                # Close position
                position['status'] = 'closed'
                position['closed_at'] = datetime.now()
                position['outcome'] = outcome
                position['payout'] = payout
                position['profit'] = profit
                position['profit_pct'] = profit_pct

                # Update balance
                self.balance += payout

                # Move to closed positions
                self.closed_positions.append(position)
                self.positions.remove(position)

                # Record P&L
                self.pnl_history.append({
                    'timestamp': datetime.now(),
                    'position_id': position['position_id'],
                    'profit': profit,
                    'balance': self.balance
                })

                print(f"\n💰 POSITION CLOSED")
                print(f"   Market: {position['question']}")
                print(f"   Outcome: {outcome}")
                print(f"   Payout: ${payout:.2f}")
                print(f"   Profit: ${profit:.2f} ({profit_pct:.2f}%)")
                print(f"   New Balance: ${self.balance:.2f}")

    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio status"""
        open_positions_value = sum(p['total_cost'] for p in self.positions)
        open_positions_profit = sum(p['guaranteed_profit'] for p in self.positions)

        realized_profit = sum(p.get('profit', 0) for p in self.closed_positions)

        total_trades = len(self.trades)
        win_count = len([p for p in self.closed_positions if p.get('profit', 0) > 0])
        loss_count = len([p for p in self.closed_positions if p.get('profit', 0) <= 0])

        return {
            'starting_balance': self.starting_balance,
            'current_balance': self.balance,
            'open_positions': len(self.positions),
            'open_positions_value': open_positions_value,
            'open_positions_expected_profit': open_positions_profit,
            'closed_positions': len(self.closed_positions),
            'realized_profit': realized_profit,
            'unrealized_profit': open_positions_profit,
            'total_profit': realized_profit + open_positions_profit,
            'total_return_pct': ((realized_profit + open_positions_profit) / self.starting_balance) * 100,
            'total_trades': total_trades,
            'win_count': win_count,
            'loss_count': loss_count,
            'win_rate': (win_count / len(self.closed_positions) * 100) if self.closed_positions else 0
        }

    def print_portfolio(self):
        """Print portfolio summary"""
        summary = self.get_portfolio_summary()

        print(f"\n{'='*60}")
        print(f"PORTFOLIO SUMMARY")
        print(f"{'='*60}")
        print(f"Starting Balance:    ${summary['starting_balance']:,.2f}")
        print(f"Current Balance:     ${summary['current_balance']:,.2f}")
        print(f"")
        print(f"Open Positions:      {summary['open_positions']}")
        print(f"  Total Value:       ${summary['open_positions_value']:,.2f}")
        print(f"  Expected Profit:   ${summary['open_positions_expected_profit']:,.2f}")
        print(f"")
        print(f"Closed Positions:    {summary['closed_positions']}")
        print(f"  Realized Profit:   ${summary['realized_profit']:,.2f}")
        print(f"")
        print(f"Total Profit:        ${summary['total_profit']:,.2f}")
        print(f"Return:              {summary['total_return_pct']:.2f}%")
        print(f"")
        print(f"Total Trades:        {summary['total_trades']}")
        print(f"Win Rate:            {summary['win_rate']:.1f}%")
        print(f"{'='*60}")

    def save_state(self, filename="paper_trading_state.json"):
        """Save trading state to file"""
        state = {
            'starting_balance': self.starting_balance,
            'balance': self.balance,
            'positions': self.positions,
            'closed_positions': self.closed_positions,
            'trades': self.trades,
            'pnl_history': self.pnl_history,
            'summary': self.get_portfolio_summary()
        }

        # Convert datetime objects to strings
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        with open(filename, 'w') as f:
            json.dump(state, f, indent=2, default=serialize_datetime)

        print(f"\n💾 State saved to {filename}")

    def load_state(self, filename="paper_trading_state.json"):
        """Load trading state from file"""
        try:
            with open(filename, 'r') as f:
                state = json.load(f)

            self.starting_balance = state['starting_balance']
            self.balance = state['balance']
            self.positions = state['positions']
            self.closed_positions = state['closed_positions']
            self.trades = state['trades']
            self.pnl_history = state['pnl_history']

            print(f"\n📂 State loaded from {filename}")
            return True
        except FileNotFoundError:
            print(f"\n⚠️ No saved state found at {filename}")
            return False


def test_paper_trading():
    """Test the paper trading engine"""
    print("\n🧪 Testing Paper Trading Engine\n")

    # Create engine
    engine = PaperTradingEngine(starting_balance=10000)

    # Create a mock arbitrage opportunity
    mock_opportunity = {
        'market_id': 'btc_test_1',
        'question': 'Bitcoin Up or Down - Test Market',
        'yes_price': 0.45,
        'no_price': 0.48,
        'total_cost': 0.93,
        'profit': 0.07,
        'profit_pct': 7.5,
        'recommended_size': 100
    }

    # Execute arbitrage
    result = engine.execute_arbitrage(mock_opportunity)

    # Show portfolio
    engine.print_portfolio()

    # Simulate market resolution
    print("\n⏰ Simulating market resolution...")
    engine.simulate_market_resolution('btc_test_1', 'YES')

    # Show final portfolio
    engine.print_portfolio()

    # Save state
    engine.save_state("test_state.json")


if __name__ == "__main__":
    test_paper_trading()
