"""
Polymarket API Client
Handles all interactions with Polymarket APIs
"""

import requests
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import config

class PolymarketAPI:
    def __init__(self):
        self.clob_url = config.CLOB_API_URL
        self.gamma_url = config.GAMMA_API_URL
        self.strapi_url = config.STRAPI_API_URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
        })

    def get_markets(self, active_only=True) -> List[Dict]:
        """Get all available markets"""
        try:
            # Try CLOB API first
            response = self.session.get(f"{self.clob_url}/markets", timeout=10)
            if response.status_code == 200:
                try:
                    data = response.json()
                except:
                    print(f"⚠️  CLOB API returned non-JSON response")
                    data = None

                if data is None:
                    markets = []
                elif isinstance(data, list):
                    print(f"🔍 DEBUG: CLOB API returned list with {len(data)} items")
                    markets = data
                elif isinstance(data, dict):
                    # Try common keys where markets might be stored
                    print(f"🔍 DEBUG: CLOB API returned dict with keys: {list(data.keys())[:10]}")

                    markets = (data.get('data') or
                              data.get('markets') or
                              data.get('results') or
                              data.get('items') or [])

                    if isinstance(markets, list):
                        print(f"🔍 DEBUG: Extracted {len(markets)} markets from dict")
                    else:
                        print(f"⚠️  CLOB API dict has no markets list. Keys: {list(data.keys())[:5]}")
                        print(f"🔍 DEBUG: Trying to inspect dict values...")
                        for key, value in list(data.items())[:3]:
                            print(f"   '{key}': {type(value)} - {str(value)[:50] if not isinstance(value, (list, dict)) else f'len={len(value) if isinstance(value, (list, dict)) else 0}'}")
                        markets = []
                else:
                    print(f"⚠️  CLOB API returned unexpected format: {type(data)}")
                    markets = []

                # Filter active markets
                if markets and active_only:
                    before_filter = len(markets)
                    markets = [m for m in markets if isinstance(m, dict) and m.get('active', False)]
                    print(f"🔍 DEBUG: Filtered {before_filter} → {len(markets)} active markets")

                if markets:
                    print(f"✅ CLOB API: Returning {len(markets)} markets")
                else:
                    print(f"⚠️  CLOB API: No markets found")

                return markets
            elif response.status_code == 403:
                print(f"⚠️  CLOB API blocked (403 Forbidden)")
            else:
                print(f"⚠️  CLOB API error: {response.status_code}")
        except Exception as e:
            print(f"Error fetching markets from CLOB: {e}")

        # Try Gamma API as fallback
        try:
            response = self.session.get(f"{self.gamma_url}/markets", timeout=10)
            if response.status_code == 200:
                try:
                    data = response.json()
                except:
                    print(f"⚠️  Gamma API returned non-JSON response")
                    return []

                if isinstance(data, list):
                    print(f"🔍 DEBUG: Gamma API returned list with {len(data)} items")
                    return data
                elif isinstance(data, dict):
                    print(f"🔍 DEBUG: Gamma API returned dict with keys: {list(data.keys())[:10]}")

                    # Try common keys where markets might be stored
                    markets = (data.get('data') or
                              data.get('markets') or
                              data.get('results') or
                              data.get('items') or [])

                    if isinstance(markets, list):
                        print(f"✅ Gamma API: Returning {len(markets)} markets")
                        return markets
                    else:
                        print(f"⚠️  Gamma API dict has no markets list. Keys: {list(data.keys())[:5]}")
                        print(f"🔍 DEBUG: Trying to inspect dict values...")
                        for key, value in list(data.items())[:3]:
                            print(f"   '{key}': {type(value)} - {str(value)[:50] if not isinstance(value, (list, dict)) else f'len={len(value) if isinstance(value, (list, dict)) else 0}'}")
                        return []
                else:
                    print(f"⚠️  Gamma API returned unexpected format: {type(data)}")
                    return []
            elif response.status_code == 403:
                print(f"⚠️  Gamma API blocked (403 Forbidden)")
                print(f"💡 APIs are blocked. Use Mock API instead: PolymarketBot(use_mock=True)")
            else:
                print(f"⚠️  Gamma API error: {response.status_code}")
        except Exception as e:
            print(f"Error fetching markets from Gamma: {e}")

        return []

    def get_hourly_crypto_markets(self) -> List[Dict]:
        """Get hourly Up/Down crypto markets (our target)"""
        all_markets = self.get_markets()

        hourly_markets = []
        for market in all_markets:
            question = market.get('question', '').lower()

            # Check if it's a crypto up/down hourly market
            is_crypto = any(token.lower() in question for token in config.TARGET_TOKENS)
            is_updown = 'up or down' in question
            is_hourly = any(time in question for time in ['am et', 'pm et'])

            if is_crypto and is_updown and is_hourly:
                hourly_markets.append(market)

        return hourly_markets

    def get_orderbook(self, market_id: str) -> Dict:
        """Get order book for a specific market"""
        try:
            response = self.session.get(
                f"{self.clob_url}/book",
                params={'market': market_id},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching orderbook for {market_id}: {e}")

        return {'bids': [], 'asks': []}

    def get_market_prices(self, market_id: str) -> Dict:
        """Get current best bid/ask prices for YES and NO"""
        orderbook = self.get_orderbook(market_id)

        # In Polymarket, there are usually two outcomes: YES and NO
        # For "Up or Down" markets: UP = YES, DOWN = NO

        bids = orderbook.get('bids', [])
        asks = orderbook.get('asks', [])

        # Best bid = highest price someone will buy at
        # Best ask = lowest price someone will sell at

        best_bid_yes = float(bids[0]['price']) if bids else 0.5
        best_ask_yes = float(asks[0]['price']) if asks else 0.5

        # NO price is complement of YES (approximately)
        # If YES is 70¢, NO should be around 30¢
        best_bid_no = 1.0 - best_ask_yes
        best_ask_no = 1.0 - best_bid_yes

        return {
            'yes_bid': best_bid_yes,
            'yes_ask': best_ask_yes,
            'no_bid': best_bid_no,
            'no_ask': best_ask_no,
            'timestamp': time.time()
        }

    def calculate_arbitrage(self, prices: Dict) -> Dict:
        """Calculate if arbitrage opportunity exists"""
        # To lock in profit, we buy YES and NO
        # Cost = YES ask price + NO ask price
        # Payout = $1 (guaranteed, one side wins)
        # Profit = $1 - Cost

        yes_cost = prices['yes_ask']
        no_cost = prices['no_ask']
        total_cost = yes_cost + no_cost

        profit = 1.0 - total_cost
        profit_pct = (profit / total_cost) * 100 if total_cost > 0 else 0

        return {
            'total_cost': total_cost,
            'guaranteed_profit': profit,
            'profit_pct': profit_pct,
            'is_opportunity': profit >= config.MIN_ARBITRAGE_PROFIT,
            'yes_price': yes_cost,
            'no_price': no_cost
        }

    def place_order(self, market_id: str, side: str, price: float, size: int, paper_trading=True):
        """
        Place an order (PAPER TRADING by default)

        Args:
            market_id: Market identifier
            side: 'YES' or 'NO' (or 'UP'/'DOWN')
            price: Price in dollars (0.0 to 1.0)
            size: Number of shares
            paper_trading: If True, simulate order (no real trade)
        """
        if paper_trading or config.PAPER_TRADING:
            # Simulate order
            order = {
                'market_id': market_id,
                'side': side,
                'price': price,
                'size': size,
                'total_cost': price * size,
                'timestamp': time.time(),
                'status': 'filled',  # Assume immediate fill in paper trading
                'order_id': f"paper_{int(time.time() * 1000)}"
            }
            return order
        else:
            # Real trading (NOT IMPLEMENTED - requires wallet integration)
            raise NotImplementedError("Real trading not implemented yet - use paper trading!")

    def get_market_resolution_time(self, market: Dict) -> Optional[datetime]:
        """Get when the market resolves"""
        # Parse from question (e.g., "November 15, 4PM ET")
        question = market.get('question', '')

        # This is simplified - would need proper parsing
        # For now, assume hourly markets resolve on the hour
        return datetime.now() + timedelta(hours=1)

    def is_market_closing_soon(self, market: Dict, minutes: int = 5) -> bool:
        """Check if market is closing within N minutes"""
        resolution_time = self.get_market_resolution_time(market)
        if not resolution_time:
            return False

        time_until_close = resolution_time - datetime.now()
        return time_until_close.total_seconds() < (minutes * 60)

    def get_market_info(self, market_id: str) -> Optional[Dict]:
        """Get detailed market information"""
        try:
            response = self.session.get(
                f"{self.gamma_url}/markets/{market_id}",
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching market info: {e}")

        return None


# Simplified mock for testing when APIs are blocked
class MockPolymarketAPI(PolymarketAPI):
    """Mock API for testing when real API is blocked"""

    def __init__(self):
        super().__init__()
        self.mock_markets = self._generate_mock_markets()

    def _generate_mock_markets(self) -> List[Dict]:
        """Generate realistic mock markets based on FirstOrder's activity"""
        import random

        markets = []
        tokens = ['Bitcoin', 'Ethereum', 'Solana', 'XRP']
        hours = list(range(0, 24))

        for token in tokens:
            for hour in hours[:5]:  # Just a few hours for testing
                ampm = 'AM' if hour < 12 else 'PM'
                display_hour = hour if hour <= 12 else hour - 12
                if display_hour == 0:
                    display_hour = 12

                market_id = f"{token.lower()}_updown_{hour}"

                markets.append({
                    'id': market_id,
                    'question': f"{token} Up or Down - November 15, {display_hour}{ampm} ET",
                    'active': True,
                    'token': token
                })

        return markets

    def get_markets(self, active_only=True) -> List[Dict]:
        """Return mock markets"""
        return self.mock_markets if active_only else self.mock_markets

    def get_hourly_crypto_markets(self) -> List[Dict]:
        """Return mock hourly crypto markets"""
        return self.mock_markets

    def get_market_prices(self, market_id: str) -> Dict:
        """Generate mock prices with occasional arbitrage opportunities"""
        import random

        # 80% of time: efficient market (no arb)
        # 20% of time: arbitrage opportunity

        if random.random() < 0.8:
            # Efficient market
            yes_price = random.uniform(0.3, 0.7)
            no_price = 1.0 - yes_price + random.uniform(-0.02, 0.02)  # Small inefficiency
        else:
            # Arbitrage opportunity!
            yes_price = random.uniform(0.4, 0.6)
            no_price = random.uniform(0.3, 0.5)
            # Ensure total < 1.0
            if yes_price + no_price >= 0.98:
                no_price = 0.98 - yes_price - random.uniform(0.02, 0.08)

        return {
            'yes_bid': yes_price - 0.01,
            'yes_ask': yes_price,
            'no_bid': no_price - 0.01,
            'no_ask': no_price,
            'timestamp': time.time()
        }


# Factory function
def create_api_client(use_mock=False) -> PolymarketAPI:
    """Create appropriate API client"""
    if use_mock:
        print("⚠️ Using MOCK API for testing")
        return MockPolymarketAPI()
    else:
        return PolymarketAPI()
