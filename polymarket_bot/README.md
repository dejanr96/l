# 🤖 Polymarket Arbitrage Bot

**An automated trading bot that replicates @FirstOrder's $345k+ strategy**

This bot scans Polymarket prediction markets for arbitrage opportunities and executes risk-free trades by buying both sides of binary markets when the total cost is less than $1.

## 🎯 Strategy Overview

**What @FirstOrder Does:**
- Trades hourly crypto "Up or Down" markets on Polymarket
- Executes **arbitrage**: buying BOTH YES and NO when total < $1.00
- **Guaranteed profit** regardless of outcome
- Made $345,544 profit in 5 months (June-Nov 2025)
- 11,065 predictions at ~70 trades/day

**How Arbitrage Works:**

```
Normal market: YES at 50¢ + NO at 50¢ = $1.00 (no profit)

Arbitrage opportunity:
- YES at 45¢
- NO at 48¢
- Total cost: 93¢
- Payout: $1.00 (guaranteed, one side wins)
- Profit: 7¢ (7.5% return)

With 100 shares:
- Cost: $93
- Payout: $100
- Profit: $7 guaranteed!
```

## 📁 Files

- **`config.py`** - Bot configuration and settings
- **`polymarket_api.py`** - Polymarket API client + Mock API for testing
- **`arbitrage_scanner.py`** - Scans markets for arbitrage opportunities
- **`paper_trader.py`** - Paper trading engine (simulates real trades)
- **`bot.py`** - Main bot (ties everything together)
- **`dashboard.py`** - Monitoring and reporting

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd polymarket_bot
pip install -r requirements.txt
```

### 2. Run Quick Test

```bash
python bot.py --quick
```

This will:
- Use Mock API (generates fake opportunities)
- Run 5 test scans
- Show paper trading results
- No internet required!

### 3. Interactive Mode

```bash
python bot.py
```

Menu options:
1. **Run single scan** - Scan once for opportunities
2. **Run continuous** - Auto-scan every N seconds
3. **Toggle auto-execute** - Auto-execute trades or manual approval
4. **Show portfolio** - View current positions and P&L
5. **Simulate market resolutions** - Close positions (for testing)
6. **Save/Load state** - Persist trading history

## 🎮 Usage Modes

### Mode 1: Manual Review (Safest)

```python
python bot.py
# Select: Mock API
# Select: Starting balance $10,000
# Choose option 1: Run single scan
# Review opportunities
# Choose Y/N to execute each trade
```

**Best for:** Learning the strategy, testing

### Mode 2: Auto-Execute (Faster)

```python
python bot.py
# Choose option 3: Toggle auto-execute (enable)
# Choose option 2: Run continuous
# Bot will automatically execute all profitable trades
```

**Best for:** Simulated trading at scale

### Mode 3: Live Monitoring

```python
python dashboard.py  # Run separately
# Watch real-time performance
# Updates every 5 seconds
```

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Trading
MIN_ARBITRAGE_PROFIT = 0.02  # Min 2¢ profit required
MAX_POSITION_SIZE = 500      # Max shares per position
STANDARD_POSITION_SIZE = 151 # @FirstOrder's standard size

# Risk Management
MAX_TOTAL_EXPOSURE = 10000   # Max $10k total
MAX_PER_MARKET = 3000        # Max $3k per market

# Scanning
SCAN_INTERVAL = 5            # Scan every 5 seconds
TARGET_TOKENS = ['Bitcoin', 'Ethereum', 'Solana', 'XRP']

# Paper Trading
PAPER_STARTING_BALANCE = 10000  # Start with $10k virtual
```

## 📊 Example Output

```
============================================================
🤖 Polymarket Arbitrage Bot
============================================================
Mode: PAPER TRADING
API: MOCK (Testing)
Starting Balance: $10,000.00
Min Arbitrage Profit: 2¢
============================================================

============================================================
Scan #1 - 2025-11-15 16:45:23
============================================================
Scanning 20 markets...

🔥 ARBITRAGE OPPORTUNITY FOUND!
   Market: Bitcoin Up or Down - November 15, 4PM ET
   YES Price: $0.450
   NO Price:  $0.480
   Total Cost: $0.930
   Guaranteed Profit: $0.070 (7.53%)
   Recommended Size: 151 shares
   Expected Profit: $10.57

✅ ARBITRAGE EXECUTED (Paper Trading)
   Market: Bitcoin Up or Down - November 15, 4PM ET
   Bought 151 YES @ $0.4522 = $68.29
   Bought 151 NO @ $0.4824 = $72.84
   Total Cost: $141.13
   Guaranteed Profit: $9.87
   New Balance: $9,858.87

============================================================
PORTFOLIO SUMMARY
============================================================
Starting Balance:    $10,000.00
Current Balance:     $9,858.87

Open Positions:      1
  Total Value:       $141.13
  Expected Profit:   $9.87

Total Profit:        $9.87
Return:              0.10%

Total Trades:        2
Win Rate:            0.0%
============================================================
```

## 🧪 Testing Flow

1. **Quick Test (1 minute)**
   ```bash
   python bot.py --quick
   ```
   Validates all components work

2. **Single Scan Test (2 minutes)**
   ```bash
   python bot.py
   # Option 1: Run single scan
   # Review opportunities, execute 1-2 trades
   ```

3. **Continuous Test (10 minutes)**
   ```bash
   python bot.py
   # Option 2: Run continuous (60 second interval)
   # Let it run for 10 scans
   # Option 4: Show portfolio
   ```

4. **Resolution Test**
   ```bash
   # After building positions
   # Option 5: Simulate market resolutions
   # See profits realized
   ```

## 📈 Performance Tracking

The bot tracks:
- **Realized Profit** - From closed positions
- **Unrealized Profit** - From open positions
- **Total Return %** - Overall performance
- **Win Rate** - Percentage of profitable trades
- **Trade History** - All executed trades

All data is saved to `paper_trading_state.json` and can be loaded on restart.

## 🔄 Going from Paper → Live Trading

**Current:** Paper trading only (no real money)

**To enable live trading:**

1. **Get Polymarket Account**
   - Sign up at polymarket.com
   - Fund with USDC on Polygon
   - Get API credentials

2. **Update config.py**
   ```python
   PAPER_TRADING = False  # DANGER: Real money!
   WALLET_ADDRESS = "0xYourAddress"
   PRIVATE_KEY = "your_key"  # Store securely!
   ```

3. **Implement wallet integration**
   - Edit `polymarket_api.py`
   - Implement `place_order()` for real trades
   - Use Polymarket SDK or web3.py

4. **Start SMALL**
   - Test with $100-$500 first
   - Verify executions work
   - Scale up gradually

## ⚠️ Important Notes

### Paper Trading (Current Mode)
- ✅ No risk
- ✅ Tests strategy logic
- ✅ Learns the system
- ⚠️ Doesn't account for:
  - Order book liquidity
  - Slippage on large orders
  - Gas fees
  - Failed transactions

### Live Trading (Not Implemented)
- ⚠️ Real money at risk
- ⚠️ Polymarket regulations vary by country
- ⚠️ Need proper wallet security
- ⚠️ Tax implications
- ⚠️ Platform limits and liquidity

### API Limitations

If real API is blocked, use Mock API:
```python
# In config.py or when prompted
use_mock = True
```

Mock API generates realistic fake opportunities for testing.

## 🎓 Learning from @FirstOrder

**Key Insights:**

1. **Volume Over Edge**
   - Small 2-7% profits
   - Executed 70+ times per day
   - Compounds to massive returns

2. **Market Making**
   - Small orders ($5-$20) at many price levels
   - Earns spreads when filled
   - Low risk, consistent income

3. **24/7 Operation**
   - Automated bot (obvious from 2AM-4AM trades)
   - Never misses opportunities
   - Instant execution

4. **Risk Management**
   - Consistent position sizes
   - Diversified across BTC/ETH/SOL/XRP
   - Both sides covered (zero directional risk)

5. **Hourly Markets**
   - Less competition than daily markets
   - More frequent opportunities
   - Quick resolution (profits realized fast)

## 🛠️ Customization Ideas

**Strategy Enhancements:**

1. **Add Price Prediction**
   - Technical indicators for better entries
   - Only arb when TA confirms direction
   - Higher confidence = larger size

2. **Market Making Focus**
   - Place limit orders at multiple levels
   - Earn spreads instead of just arb
   - Requires real Polymarket API

3. **Multi-Market Arbitrage**
   - Compare Polymarket vs other prediction markets
   - Cross-platform arbitrage

4. **Dynamic Position Sizing**
   - Kelly Criterion for optimal sizing
   - Scale size based on profit %
   - Reduce size as bankroll decreases

5. **Add Discord/Telegram Alerts**
   - Real-time notifications
   - Mobile monitoring

## 📚 Resources

- **Polymarket:** https://polymarket.com
- **Polymarket Docs:** https://docs.polymarket.com
- **Polymarket API:** https://docs.polymarket.com/api
- **@FirstOrder Profile:** https://polymarket.com/@FirstOrder

## 🐛 Troubleshooting

**"API blocked" or "403 Forbidden"**
→ Use Mock API mode (already configured)

**"Insufficient balance"**
→ Increase `PAPER_STARTING_BALANCE` in config.py

**"No opportunities found"**
→ If using Mock API, this is rare but possible
→ Try multiple scans or adjust `MIN_ARBITRAGE_PROFIT`

**Import errors**
→ Make sure you're in polymarket_bot directory
→ Run `pip install -r requirements.txt`

## 📈 Expected Results

**With Mock API (Testing):**
- 20-30% of scans find opportunities
- 2-8% profit per opportunity
- Expected: $50-200 profit per day (simulated)

**With Real API (When implemented):**
- Opportunities are rarer (market efficient)
- Maybe 1-5% of markets have arbitrage
- But when found, profits are real
- Expected: Highly variable, depends on market conditions

**@FirstOrder's actual results:**
- $345,544 profit in 5 months
- ~$69k/month average
- With significant capital ($50k+?)

## 🎯 Next Steps

1. **Run the bot** - Get comfortable with paper trading
2. **Understand the strategy** - Study each arbitrage opportunity
3. **Analyze performance** - Track what works best
4. **Optimize parameters** - Tune min profit, position sizes
5. **Consider live trading** - Only after thorough testing!

## 📞 Support

This bot is for educational purposes. Trade at your own risk!

---

**Built by reverse engineering @FirstOrder's $345k Polymarket strategy** 🚀
