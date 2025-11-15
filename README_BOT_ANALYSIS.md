# Bot Trading Strategy Analyzer

This toolkit helps you reverse engineer trading bot strategies by analyzing on-chain transactions.

## Target Bot Address

`0xeffcc79a8572940cee2238b44eac89f2c48fda88`

## Method 1: Using PolygonScan API (Recommended)

### Setup

1. Get a free API key from PolygonScan:
   - Visit https://polygonscan.com/register
   - Create an account
   - Go to https://polygonscan.com/myapikey
   - Create a new API key

2. Edit `analyze_bot.py` and replace `YourApiKeyToken` with your actual API key:
   ```python
   api_key = "YOUR_ACTUAL_API_KEY_HERE"
   ```

3. Run the analysis:
   ```bash
   python3 analyze_bot.py
   ```

### What the Script Analyzes

- **Token Transfers**: Which tokens are being traded
- **Trading Patterns**: Frequency, timing, and swap identification
- **Contract Interactions**: Which DEXs/protocols are being used
- **Gas Patterns**: Gas usage and pricing strategies
- **Strategy Identification**: Attempts to identify:
  - Arbitrage trading
  - High-frequency trading
  - Frontrunning/MEV
  - Sniping attempts
  - Focused pair trading

## Method 2: Manual CSV Analysis

If you can't use the API, you can manually download data:

1. Visit https://polygonscan.com/address/0xeffcc79a8572940cee2238b44eac89f2c48fda88
2. Click on "Token Transfers (ERC-20)" tab
3. Click "Download CSV Export" (bottom of page)
4. Save the file as `token_transfers.csv`
5. Run: `python3 analyze_csv.py token_transfers.csv`

## Method 3: Using Web3.py (Direct Blockchain)

For complete analysis without relying on PolygonScan, you can query the blockchain directly:

1. Get a Polygon RPC endpoint (Alchemy, Infura, QuickNode, or public)
2. Use the `web3_analyzer.py` script (coming soon)

## Understanding the Output

### Token Analysis
Shows which tokens the bot is trading most frequently, both incoming and outgoing.

### Trading Patterns
- **Swaps**: Transactions where tokens are exchanged
- **Timing**: How frequently trades occur
- **Recent Activity**: Last 10 swaps with details

### Contract Interactions
Lists the smart contracts the bot interacts with most often. Common addresses:
- QuickSwap Router: `0xa5e0829caced8ffdd4de3c43696c57f7d7a678ff`
- SushiSwap Router: `0x1b02da8cb0d097eb8d57a175b88c7d8b47997506`
- Uniswap V3: Various pool addresses

### Strategy Patterns
The script attempts to identify:
- **Focused trading**: If the bot specializes in specific token pairs
- **High-frequency**: If trades happen in rapid succession
- **Frontrunning**: High failure rate with quick successive trades
- **Arbitrage**: Quick buy-sell cycles of same tokens

## Common Bot Strategies

### 1. Arbitrage Bots
- Trade the same token pairs repeatedly
- Quick execution (seconds between trades)
- Use multiple DEXs
- Look for: Same tokens in/out, different DEXs

### 2. MEV/Frontrunning Bots
- High gas prices
- Many failed transactions
- Trades right before/after large swaps
- Look for: High failure rate, varied gas prices

### 3. Sniper Bots
- Trade immediately when new tokens are listed
- Very high gas prices
- Trade early in token's lifecycle
- Look for: Trades on newly created pairs

### 4. Market Making Bots
- Provide liquidity to pools
- Regular, consistent trading patterns
- Both sides of pairs
- Look for: Balanced in/out, regular intervals

### 5. Trend Following Bots
- Follow price momentum
- Increasing position sizes
- Hold for longer periods
- Look for: Directional trades, varying amounts

## Next Steps

After identifying the strategy:

1. **Study the contracts** the bot interacts with
2. **Analyze successful vs failed** transactions
3. **Check timing patterns** against market events
4. **Review gas strategies** for competitiveness
5. **Look at profitability** (requires price data analysis)

## Advanced Analysis

For deeper insights:
- Analyze the bot's contract code (if it's a smart contract)
- Track profitability by matching buys/sells
- Compare timing against major market events
- Study gas strategies in detail
- Look for patterns in mempool activity

## Limitations

- Only shows on-chain activity (not private transactions)
- Can't see failed mempool transactions
- Timing accuracy limited to block timestamps
- Can't determine exact profitability without price feeds
- Some MEV strategies happen in flashbots/private pools

## Resources

- PolygonScan: https://polygonscan.com
- QuickSwap Analytics: https://info.quickswap.exchange
- SushiSwap Analytics: https://analytics.sushi.com
- DexScreener: https://dexscreener.com
