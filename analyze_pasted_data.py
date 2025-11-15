#!/usr/bin/env python3
"""
Analyze bot strategy from pasted transaction data
Accepts various formats: CSV, JSON, or simple paste from PolygonScan
"""

import sys
import json
import re
from datetime import datetime
from collections import Counter, defaultdict

def parse_pasted_text(text):
    """Parse various formats of pasted transaction data"""
    transactions = []

    lines = text.strip().split('\n')

    for line in lines:
        if not line.strip() or 'Txn Hash' in line or '---' in line:
            continue

        # Try to extract transaction data
        # Format: hash, block, age, from, to, token, amount
        parts = re.split(r'[,\t|]+', line.strip())

        if len(parts) >= 6:
            tx = {
                'hash': parts[0].strip(),
                'block': parts[1].strip() if len(parts) > 1 else '',
                'age': parts[2].strip() if len(parts) > 2 else '',
                'from': parts[3].strip() if len(parts) > 3 else '',
                'to': parts[4].strip() if len(parts) > 4 else '',
                'token': parts[5].strip() if len(parts) > 5 else '',
                'amount': parts[6].strip() if len(parts) > 6 else '0'
            }
            transactions.append(tx)

    return transactions

def analyze_pasted_transactions(transactions, bot_address):
    """Analyze pasted transaction data"""

    if not transactions:
        print("No valid transactions found in input")
        return

    print(f"\n{'='*60}")
    print(f"ANALYZING {len(transactions)} TRANSACTIONS")
    print(f"{'='*60}\n")

    bot_address = bot_address.lower()

    # Token analysis
    tokens_in = Counter()
    tokens_out = Counter()

    for tx in transactions:
        token = tx.get('token', 'UNKNOWN')
        to_addr = tx.get('to', '').lower()
        from_addr = tx.get('from', '').lower()

        if bot_address in to_addr:
            tokens_in[token] += 1
        elif bot_address in from_addr:
            tokens_out[token] += 1

    print("TOKENS RECEIVED:")
    for token, count in tokens_in.most_common(10):
        print(f"  {token}: {count} times")

    print("\nTOKENS SENT:")
    for token, count in tokens_out.most_common(10):
        print(f"  {token}: {count} times")

    # Check for arbitrage
    common_tokens = set(tokens_in.keys()) & set(tokens_out.keys())
    if common_tokens:
        print(f"\nTOKENS BOTH BOUGHT AND SOLD: {len(common_tokens)}")
        print("  → Likely ARBITRAGE or MARKET MAKING")
        for token in list(common_tokens)[:5]:
            print(f"    {token}: IN {tokens_in[token]}x, OUT {tokens_out[token]}x")

    # Block analysis
    blocks = [tx.get('block', '') for tx in transactions if tx.get('block')]
    unique_blocks = len(set(blocks))

    print(f"\nTIMING ANALYSIS:")
    print(f"  Transactions: {len(transactions)}")
    print(f"  Unique blocks: {unique_blocks}")
    if unique_blocks > 0:
        avg_txs_per_block = len(transactions) / unique_blocks
        print(f"  Avg txs per block: {avg_txs_per_block:.2f}")
        if avg_txs_per_block > 1.5:
            print("  → HIGH-FREQUENCY: Multiple txs per block detected")

    # Strategy guess
    print(f"\n{'='*60}")
    print("LIKELY STRATEGY")
    print(f"{'='*60}\n")

    if common_tokens and len(common_tokens) <= 3:
        print("✓ ARBITRAGE BOT")
        print("  Evidence:")
        print("  - Same tokens bought and sold")
        print("  - Focused on 1-3 token pairs")
        print("\n  How it works:")
        print("  - Finds price differences between DEXs")
        print("  - Buys on cheaper DEX, sells on expensive one")
        print("  - Profits from the spread")

    elif len(set(tokens_in.keys())) > 10:
        print("✓ MEV/FRONTRUNNING or SNIPING BOT")
        print("  Evidence:")
        print("  - Many different tokens")
        print("  - Diverse trading activity")
        print("\n  How it works:")
        print("  - Monitors mempool for profitable opportunities")
        print("  - Frontruns large swaps or snipes new tokens")
        print("  - Uses high gas to win transactions")

    elif avg_txs_per_block > 1.5:
        print("✓ SANDWICH/MEV BOT")
        print("  Evidence:")
        print("  - Multiple transactions per block")
        print("\n  How it works:")
        print("  - Sees large pending swap")
        print("  - Places buy order before (frontrun)")
        print("  - Places sell order after (backrun)")
        print("  - Profits from victim's slippage")

    else:
        print("✓ GENERAL TRADING BOT")
        print("  Strategy unclear from limited data")
        print("  Could be: Market making, grid trading, or DCA")

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║  BOT TRANSACTION ANALYZER - Paste Data Mode              ║
╚══════════════════════════════════════════════════════════╝

How to use:
1. Go to PolygonScan token transfers page
2. Copy 10-20 transactions (Ctrl+C)
3. Save to a file: data.txt
4. Run: python3 analyze_pasted_data.py data.txt

Or paste data when prompted below.
""")

    bot_address = "0xeffcc79a8572940cee2238b44eac89f2c48fda88"

    # Check for file input
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as f:
                data = f.read()
            print(f"Loaded data from {filename}\n")
        except:
            print(f"Error reading file: {filename}")
            return
    else:
        print("Paste transaction data below (Ctrl+D when done):")
        print("-" * 60)
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            data = '\n'.join(lines)

    # Try to parse as JSON first
    try:
        json_data = json.loads(data)
        if isinstance(json_data, list):
            transactions = json_data
        else:
            transactions = parse_pasted_text(data)
    except:
        transactions = parse_pasted_text(data)

    analyze_pasted_transactions(transactions, bot_address)

if __name__ == "__main__":
    main()
