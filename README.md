# Polymarket Trader Strategy Analysis

Analysis toolkit for reverse engineering trading strategies on Polymarket prediction markets.

## Target

**Trader:** [@FirstOrder](https://polymarket.com/@FirstOrder)
**Address:** `0xeffcc79a8572940cee2238b44eac89f2c48fda88`
**Platform:** Polymarket (prediction market on Polygon)

## Quick Start

### 1. Read the Guide (5 minutes)
```bash
cat POLYMARKET_STRATEGY_GUIDE.md
```

### 2. Visit the Profile
- **Polymarket:** https://polymarket.com/@FirstOrder
- **PolygonScan:** https://polygonscan.com/address/0xeffcc79a8572940cee2238b44eac89f2c48fda88

### 3. Run the Analyzer
```bash
python3 analyze_polymarket.py
```

## Files

### Main Analysis Tools
- **`POLYMARKET_STRATEGY_GUIDE.md`** - Complete strategy analysis guide
- **`POLYMARKET_ANALYSIS_SUMMARY.md`** - Quick reference and next steps
- **`analyze_polymarket.py`** - Automated analyzer

### Supporting Tools (for on-chain analysis)
- **`analyze_bot.py`** - View USDC flows (requires PolygonScan API key)
- **`analyze_csv.py`** - Analyze exported transaction CSVs
- **`analyze_pasted_data.py`** - Analyze pasted transaction data
- **`manual_analysis_guide.md`** - On-chain analysis guide

### Documentation
- **`README_BOT_ANALYSIS.md`** - General bot analysis guide
- **`BOT_ANALYSIS_SUMMARY.md`** - Original DEX bot guide
- **`NEXT_STEPS.md`** - Original analysis paths

## What is Polymarket?

Polymarket is a **prediction market** where users bet on future events using USDC:

- **Not token trading** - Betting on real-world outcomes
- **Binary markets** - Yes/No questions about events
- **Odds-based** - Prices represent probability (40¢ = 40% chance)
- **On Polygon** - All activity is on-chain and visible

## Common Strategies

1. **Information Edge** - Better analysis/data than market
2. **Market Making** - Provide liquidity, earn spreads
3. **Arbitrage** - Exploit pricing inefficiencies
4. **Odds Trading** - Trade on volatility, not outcomes
5. **Contrarian** - Bet against overreactions
6. **Hedging** - Risk management for real-world exposure

## Quick Analysis Checklist

Visit the profile and answer:

- [ ] What's their total volume?
- [ ] Which categories do they trade? (politics, sports, crypto)
- [ ] Average bet size?
- [ ] How often do they trade?
- [ ] Do they hold until resolution or trade early?
- [ ] Are transactions automated (regular patterns)?

## Key Polymarket Contracts

Look for these on PolygonScan:

| Contract | Address | Purpose |
|----------|---------|---------|
| CTF Exchange | `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E` | Main trading |
| Conditional Tokens | `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045` | Positions |
| USDC | `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` | Bet currency |

## Dependencies

```bash
pip install -r requirements.txt
```

Or just:
```bash
pip install requests
```

## Example Usage

### Automated Analysis
```bash
python3 analyze_polymarket.py
```

### Manual Analysis
1. Read `POLYMARKET_STRATEGY_GUIDE.md`
2. Visit profile: https://polymarket.com/@FirstOrder
3. Check PolygonScan: https://polygonscan.com/address/0xeffcc79a8572940cee2238b44eac89f2c48fda88
4. Fill out the analysis checklist in the guide

### CSV Analysis (if you download data)
```bash
python3 analyze_csv.py polymarket_transactions.csv
```

## Understanding Results

### Profitability
```
Net USDC IN - USDC OUT = Profit
```

Watch for:
- More USDC IN than OUT = Profitable
- Regular patterns = Likely automated
- Large positions = High conviction or market making
- Quick flips = Trading odds, not outcomes

### Strategy Identification

**Information Edge:**
- Large bets on specific categories
- Long hold times
- Early market entry

**Market Making:**
- Both YES and NO positions
- High frequency
- Many markets

**Arbitrage:**
- Very quick in/out
- Small margins
- High volume

## Next Steps

After analysis, you'll know:

1. **Their strategy type**
2. **Their market focus**
3. **Their scale/profitability**
4. **Their edge** (what makes them successful)
5. **Automation level**
6. **Replicability**

## Resources

- **Polymarket:** https://polymarket.com
- **Polymarket Docs:** https://docs.polymarket.com
- **PolygonScan:** https://polygonscan.com
- **Prediction Markets Guide:** https://en.wikipedia.org/wiki/Prediction_market

## Questions?

See `POLYMARKET_STRATEGY_GUIDE.md` for:
- Step-by-step analysis walkthrough
- 6 common strategy types explained
- Strategy decoder decision tree
- Profitability estimation
- Risk assessment

## License

Educational purposes only. Prediction market regulations vary by jurisdiction.

---

**Start here:** Open `POLYMARKET_ANALYSIS_SUMMARY.md` for a quick overview!
