# Manual Bot Strategy Analysis Guide

Since automated scraping is blocked, here's how to manually reverse engineer the bot strategy by inspecting the blockchain directly.

## 🔍 Step-by-Step Manual Investigation

### Step 1: Open PolygonScan
Visit: https://polygonscan.com/address/0xeffcc79a8572940cee2238b44eac89f2c48fda88

### Step 2: Check if it's a Contract or EOA (Wallet)

**Look at the top of the page:**

- **If you see "Contract"** → It's a smart contract bot
  - Click on "Contract" tab
  - Check if source code is verified
  - If verified: Read the code to understand logic
  - Look for function names like: `swap`, `arbitrage`, `snipe`, `flashloan`

- **If it's just an address** → It's an EOA (Externally Owned Account)
  - Someone or a script controls this wallet
  - Strategy is in off-chain code

### Step 3: Analyze Token Transfers Tab

**Click "Token Transfers (ERC-20)" tab**

Answer these questions by looking at the first 20-30 transactions:

#### Question 1: What tokens appear most frequently?
Count how many times you see each token symbol.

Example:
```
USDC: 25 times
WMATIC: 25 times
WETH: 15 times
OTHER: 2 times
```

**What this tells you:**
- If 2-3 tokens dominate → **Focused strategy** (likely arbitrage on specific pair)
- If many different tokens → **Generalist strategy** (MEV, sniping, or diverse trading)

#### Question 2: Are the same tokens being bought AND sold?
Look for tokens that appear in both "From" and "To" columns.

Example:
```
Transaction 1: OUT - 100 USDC
Transaction 2: IN  - 50 WMATIC
Transaction 3: OUT - 50 WMATIC
Transaction 4: IN  - 105 USDC
```

**What this tells you:**
- Same tokens both ways → **Arbitrage or market making**
- Only buying or only selling specific tokens → **Directional trading** or **sniping**

#### Question 3: What's the timing pattern?

Look at the "Age" column. Are transactions:
- **Seconds apart?** → High-frequency, MEV, or arbitrage
- **Minutes apart?** → Moderate frequency trading
- **Hours/Days apart?** → Slower strategy, possibly DCA or grid

#### Question 4: Are transactions grouped in the same block?

Click on a few transaction hashes and check the "Block" number.

If multiple transactions in same block:
- **Different blocks** → Normal trading
- **Same block** → Atomic swaps, flash loans, or sandwich attacks

### Step 4: Analyze Normal Transactions Tab

**Click "Transactions" tab** (not Token Transfers)

#### Check the "To" column - Which contracts are being called?

Common Polygon DEX routers:

| Contract Address | DEX | Strategy Hint |
|-----------------|-----|---------------|
| `0xa5E0829C...` | QuickSwap Router | Popular DEX |
| `0x1b02dA8C...` | SushiSwap Router | Arbitrage opportunity |
| `0xE592427A...` | Uniswap V3 Router | Advanced strategies |
| `0xBA122222...` | Balancer Vault | Complex multi-asset |
| `0xDEF171Fe...` | Paraswap | Aggregator usage |

**What this tells you:**
- **One DEX only** → Simple swapping or specific pool focus
- **Multiple DEXs** → **ARBITRAGE LIKELY**
- **Aggregators (Paraswap, 1inch)** → Trying to get best prices

#### Check Gas Prices

Look at the "Txn Fee" column and click on a few transactions to see gas details.

**Low gas (30-50 Gwei):**
- Not time-critical
- Likely: Grid trading, DCA, or market making

**Medium gas (50-100 Gwei):**
- Normal priority
- Likely: Regular arbitrage or trading

**High gas (100-500 Gwei):**
- Time-critical
- Likely: **MEV/Frontrunning** or competitive sniping

**Extremely high (500+ Gwei):**
- **Definitely MEV** or trying to win token launch snipes

#### Check Transaction Status

Count how many show "Success" vs "Failed"

**High success rate (>90%):**
- Well-tested strategy
- Likely: Established arbitrage or trading bot

**Medium success (70-90%):**
- Competitive environment
- Likely: MEV but not always winning

**Low success (<70%):**
- **Very competitive MEV**
- Losing most auctions but profitable when wins

### Step 5: Deep Dive on ONE Transaction

Pick any transaction from Token Transfers, click the hash, and analyze in detail:

**1. Look at "Tokens Transferred" section:**

Count the token movements. Example:

```
OUT: 1000 USDC (from bot address)
 IN:  0.5 WETH  (to bot address)
OUT:  0.5 WETH  (from bot address)
 IN:  1020 USDC (to bot address)
```

**This pattern = ARBITRAGE**
- Swapped USDC → WETH → USDC
- Made 20 USDC profit (minus gas)

**2. Click on "Input Data" (if contract call):**

Look for function names:
- `swapExactTokensForTokens` → Simple DEX swap
- `swapExactETHForTokens` → Using native MATIC
- `flashLoan` → **Flash loan arbitrage**
- `multicall` → **Batch operations** (advanced)
- `snipe` or `buy` → **Sniping bot**

**3. Check "Internal Transactions":**

If you see internal txs, the bot might be:
- Using flash loans
- Calling multiple contracts
- More sophisticated strategy

### Step 6: Timeline Analysis

**Go back to Token Transfers, look at the last 24 hours:**

How many transactions in 24 hours?
- **100+** → High-frequency bot
- **10-50** → Active trading bot
- **1-10** → Slow/selective strategy
- **0** → Bot might be inactive

**When are transactions happening?**
- **Random times** → Reactive (waiting for opportunities)
- **Regular intervals** → Scheduled (DCA, grid)
- **Clusters of activity** → Event-driven (new tokens, high volatility)

## 🎯 Pattern Recognition

### Pattern A: Arbitrage Bot
```
✓ Same 2-3 tokens repeatedly
✓ Multiple DEXs in "To" column
✓ Trades seconds apart
✓ High success rate
✓ Balanced in/out
```

### Pattern B: MEV Frontrunner
```
✓ Various tokens
✓ Very high gas prices
✓ Many failed transactions
✓ Same-block transactions
✓ Sandwich pattern (3 txs in sequence)
```

### Pattern C: Sniper Bot
```
✓ Many different tokens
✓ Buys immediately after new pairs
✓ Extremely high gas
✓ Quick sell after (hours/days later)
✓ Low success rate
```

### Pattern D: Market Maker
```
✓ Same tokens in/out frequently
✓ Regular timing
✓ Lower gas prices
✓ Very high success rate
✓ Balanced amounts
```

### Pattern E: Grid/DCA Bot
```
✓ Same direction trades (mostly buying)
✓ Regular time intervals
✓ Similar amounts each time
✓ Low gas (not urgent)
✓ Normal success rate
```

## 📊 Quick Analysis Checklist

Copy this and fill it out while browsing PolygonScan:

```
BOT ANALYSIS WORKSHEET
======================

Address Type: [ ] Contract [ ] EOA

Top 3 Tokens Traded:
1. ________________
2. ________________
3. ________________

Transaction Frequency: [ ] Seconds [ ] Minutes [ ] Hours [ ] Days

Most Used DEX Contracts:
1. ________________
2. ________________

Average Gas Price: _________ Gwei
Gas Range: _____ to _____ Gwei

Success Rate: _____%

Same Block Transactions: [ ] Yes [ ] No

Flash Loans Used: [ ] Yes [ ] No [ ] Unknown

Tokens Both Bought & Sold: [ ] Yes [ ] No

Pattern Identified:
[ ] Arbitrage
[ ] MEV/Frontrunning
[ ] Sniping
[ ] Market Making
[ ] Grid/DCA
[ ] Unknown

Notes:
_________________________________
_________________________________
_________________________________
```

## 🔥 What to Share With Me

After your manual analysis, share:

1. **The filled worksheet above**
2. **2-3 example transaction hashes** that seem representative
3. **Any patterns you noticed** that seem unusual
4. **Screenshots** if something is confusing

Then I can:
- Confirm your hypothesis
- Provide deeper analysis
- Explain the strategy in detail
- Suggest how to replicate it (if legal/ethical)

## Alternative: Paste Transaction Data

If you want, you can:
1. Copy 10-20 recent transactions from PolygonScan
2. Paste them into a text file
3. I'll create a parser to analyze it

Just copy the data in this format:
```
Txn Hash | Block | Age | From | To | Token | Amount
0x123... | 12345 | 1 min | 0xabc.. | 0xdef.. | USDC | 100
```

---

**The goal**: Identify the CORE STRATEGY so you understand:
- What opportunities the bot is exploiting
- How it makes money
- Whether it's simple or sophisticated
- If you could build something similar
