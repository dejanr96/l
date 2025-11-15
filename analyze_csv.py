#!/usr/bin/env python3
"""
CSV Bot Trading Analyzer
Analyzes trading patterns from PolygonScan CSV export
"""

import csv
import sys
from datetime import datetime
from collections import defaultdict, Counter


class CSVBotAnalyzer:
    def __init__(self, csv_file, bot_address):
        self.csv_file = csv_file
        self.bot_address = bot_address.lower()
        self.transfers = []

    def load_csv(self):
        """Load CSV file exported from PolygonScan"""
        print(f"Loading CSV file: {self.csv_file}")

        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.transfers = list(reader)

            print(f"Loaded {len(self.transfers)} transactions\n")
            return True

        except FileNotFoundError:
            print(f"Error: File {self.csv_file} not found")
            print("\nTo download the CSV:")
            print("1. Visit https://polygonscan.com/tokentxns?a=" + self.bot_address)
            print("2. Scroll to bottom and click 'Download CSV Export'")
            print("3. Save as token_transfers.csv")
            return False
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False

    def analyze_tokens(self):
        """Analyze which tokens are being traded"""
        print(f"\n{'='*60}")
        print("TOKEN ANALYSIS")
        print(f"{'='*60}\n")

        tokens_in = defaultdict(lambda: {'count': 0, 'total': 0})
        tokens_out = defaultdict(lambda: {'count': 0, 'total': 0})

        for tx in self.transfers:
            # CSV format may vary, handle different column names
            token_symbol = tx.get('TokenSymbol', tx.get('Token Symbol', 'UNK'))
            token_name = tx.get('TokenName', tx.get('Token Name', ''))

            # Handle different CSV formats for addresses
            from_addr = tx.get('From', '').lower()
            to_addr = tx.get('To', '').lower()

            # Value handling
            value_str = tx.get('Value', tx.get('Quantity', '0'))
            try:
                # Remove any commas and convert to float
                value = float(value_str.replace(',', ''))
            except:
                value = 0

            token_id = f"{token_symbol}"
            if token_name and token_name != token_symbol:
                token_id += f" ({token_name})"

            if to_addr == self.bot_address:
                # Incoming
                tokens_in[token_id]['count'] += 1
                tokens_in[token_id]['total'] += value
            elif from_addr == self.bot_address:
                # Outgoing
                tokens_out[token_id]['count'] += 1
                tokens_out[token_id]['total'] += value

        print("TOKENS RECEIVED:")
        for token, data in sorted(tokens_in.items(), key=lambda x: x[1]['count'], reverse=True)[:20]:
            print(f"  {token:40} - {data['count']:4} transfers, Total: {data['total']:,.2f}")

        print("\nTOKENS SENT:")
        for token, data in sorted(tokens_out.items(), key=lambda x: x[1]['count'], reverse=True)[:20]:
            print(f"  {token:40} - {data['count']:4} transfers, Total: {data['total']:,.2f}")

        return tokens_in, tokens_out

    def analyze_trading_patterns(self):
        """Analyze trading patterns and timing"""
        print(f"\n{'='*60}")
        print("TRADING PATTERN ANALYSIS")
        print(f"{'='*60}\n")

        # Group by transaction hash
        tx_groups = defaultdict(list)
        for transfer in self.transfers:
            tx_hash = transfer.get('Txhash', transfer.get('TxHash', ''))
            if tx_hash:
                tx_groups[tx_hash].append(transfer)

        # Find swaps
        swaps = []
        for tx_hash, transfers in tx_groups.items():
            if len(transfers) >= 2:
                ins = [t for t in transfers if t.get('To', '').lower() == self.bot_address]
                outs = [t for t in transfers if t.get('From', '').lower() == self.bot_address]

                if ins and outs:
                    # Get timestamp
                    timestamp_str = transfers[0].get('UnixTimestamp', transfers[0].get('DateTime', ''))
                    try:
                        if timestamp_str.isdigit():
                            timestamp = int(timestamp_str)
                        else:
                            # Try parsing datetime string
                            dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                            timestamp = int(dt.timestamp())
                    except:
                        timestamp = 0

                    swaps.append({
                        'hash': tx_hash,
                        'timestamp': timestamp,
                        'tokens_in': ins,
                        'tokens_out': outs
                    })

        swaps.sort(key=lambda x: x['timestamp'], reverse=True)

        print(f"Identified {len(swaps)} potential swap transactions\n")

        # Analyze timing
        if swaps:
            timestamps = [s['timestamp'] for s in swaps if s['timestamp'] > 0]
            if len(timestamps) > 1:
                time_diffs = []
                for i in range(1, len(timestamps)):
                    time_diffs.append(timestamps[i-1] - timestamps[i])

                if time_diffs:
                    avg_time = sum(time_diffs) / len(time_diffs)
                    print(f"Average time between swaps: {avg_time / 60:.2f} minutes")
                    print(f"Min time between swaps: {min(time_diffs) / 60:.2f} minutes")
                    print(f"Max time between swaps: {max(time_diffs) / 3600:.2f} hours")

        # Show recent swaps
        print("\nRECENT SWAPS (last 15):")
        for swap in swaps[:15]:
            if swap['timestamp'] > 0:
                dt = datetime.fromtimestamp(swap['timestamp'])
                print(f"\n  {dt.strftime('%Y-%m-%d %H:%M:%S')} - Tx: {swap['hash'][:10]}...")
            else:
                print(f"\n  Tx: {swap['hash'][:10]}...")

            for token_out in swap['tokens_out']:
                symbol = token_out.get('TokenSymbol', token_out.get('Token Symbol', 'UNK'))
                value_str = token_out.get('Value', token_out.get('Quantity', '0'))
                try:
                    value = float(value_str.replace(',', ''))
                except:
                    value = 0
                print(f"    OUT: {value:,.4f} {symbol}")

            for token_in in swap['tokens_in']:
                symbol = token_in.get('TokenSymbol', token_in.get('Token Symbol', 'UNK'))
                value_str = token_in.get('Value', token_in.get('Quantity', '0'))
                try:
                    value = float(value_str.replace(',', ''))
                except:
                    value = 0
                print(f"    IN:  {value:,.4f} {symbol}")

        return swaps

    def identify_strategy(self, swaps, tokens_in, tokens_out):
        """Identify trading strategy patterns"""
        print(f"\n{'='*60}")
        print("STRATEGY IDENTIFICATION")
        print(f"{'='*60}\n")

        strategies = []

        # Analyze token diversity
        total_tokens = len(set(list(tokens_in.keys()) + list(tokens_out.keys())))
        print(f"Total unique tokens traded: {total_tokens}")

        if total_tokens <= 5:
            strategies.append(f"Focused strategy - only {total_tokens} different tokens")
        elif total_tokens > 20:
            strategies.append(f"Diverse strategy - trading {total_tokens} different tokens")

        # Analyze swap patterns
        if swaps:
            # Check for common pairs
            pairs = []
            for swap in swaps:
                out_tokens = set(t.get('TokenSymbol', '') for t in swap['tokens_out'])
                in_tokens = set(t.get('TokenSymbol', '') for t in swap['tokens_in'])
                pairs.append((frozenset(out_tokens), frozenset(in_tokens)))

            pair_counter = Counter(pairs)
            if pair_counter:
                most_common_pair, count = pair_counter.most_common(1)[0]
                percentage = (count / len(swaps)) * 100
                if percentage > 30:
                    strategies.append(f"Repetitive pair trading - one pair represents {percentage:.1f}% of swaps")

            # Analyze timing
            timestamps = [s['timestamp'] for s in swaps if s['timestamp'] > 0]
            if len(timestamps) > 1:
                time_diffs = [timestamps[i-1] - timestamps[i] for i in range(1, len(timestamps))]

                quick_trades = sum(1 for d in time_diffs if d < 60)
                if quick_trades > len(time_diffs) * 0.4:
                    strategies.append(f"High-frequency pattern - {quick_trades}/{len(time_diffs)} trades within 60s")

                very_quick = sum(1 for d in time_diffs if d < 10)
                if very_quick > len(time_diffs) * 0.2:
                    strategies.append(f"Possible MEV/frontrunning - {very_quick} trades within 10s of previous")

        # Analyze balance
        if tokens_in and tokens_out:
            # Check if similar tokens appear in both in and out
            common_tokens = set(tokens_in.keys()) & set(tokens_out.keys())
            if common_tokens:
                print(f"\nTokens both bought and sold: {len(common_tokens)}")
                for token in list(common_tokens)[:10]:
                    in_count = tokens_in[token]['count']
                    out_count = tokens_out[token]['count']
                    print(f"  {token}: IN {in_count} times, OUT {out_count} times")

                    if abs(in_count - out_count) / max(in_count, out_count) < 0.2:
                        strategies.append(f"Balanced trading on {token} - possible market making")

        print("\nIDENTIFIED PATTERNS:")
        if strategies:
            for strategy in strategies:
                print(f"  • {strategy}")
        else:
            print("  • No clear patterns identified from CSV data")
            print("  • Try using the API version for more detailed analysis")

        return strategies

    def generate_report(self):
        """Generate complete analysis report"""
        if not self.load_csv():
            return

        tokens_in, tokens_out = self.analyze_tokens()
        swaps = self.analyze_trading_patterns()
        strategies = self.identify_strategy(swaps, tokens_in, tokens_out)

        print(f"\n{'='*60}")
        print("ANALYSIS COMPLETE")
        print(f"{'='*60}\n")

        print("For more detailed analysis:")
        print("1. Get a PolygonScan API key (free)")
        print("2. Run: python3 analyze_bot.py")
        print("\nThis will provide:")
        print("  - Gas price analysis")
        print("  - Contract interaction details")
        print("  - More accurate strategy identification")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_csv.py <csv_file>")
        print("\nTo get the CSV file:")
        print("1. Visit https://polygonscan.com/tokentxns?a=0xeffcc79a8572940cee2238b44eac89f2c48fda88")
        print("2. Click 'Download CSV Export' at bottom of page")
        print("3. Run: python3 analyze_csv.py token_transfers.csv")
        sys.exit(1)

    csv_file = sys.argv[1]
    bot_address = "0xeffcc79a8572940cee2238b44eac89f2c48fda88"

    analyzer = CSVBotAnalyzer(csv_file, bot_address)
    analyzer.generate_report()


if __name__ == "__main__":
    main()
