#!/usr/bin/env python3
"""
Bot Trading Strategy Analyzer
Analyzes on-chain transactions to reverse engineer trading strategies
"""

import requests
import json
from datetime import datetime
from collections import defaultdict, Counter
import time

class BotAnalyzer:
    def __init__(self, address, api_key=None):
        self.address = address.lower()
        self.api_key = api_key or "YourApiKeyToken"  # Free tier works for basic analysis
        self.base_url = "https://api.polygonscan.com/api"
        self.transactions = []
        self.token_transfers = []
        self.internal_txs = []

    def fetch_token_transfers(self, start_block=0, end_block=99999999, page=1, offset=100):
        """Fetch ERC20 token transfer events"""
        print(f"Fetching token transfers (page {page})...")

        params = {
            'module': 'account',
            'action': 'tokentx',
            'address': self.address,
            'startblock': start_block,
            'endblock': end_block,
            'page': page,
            'offset': offset,
            'sort': 'desc',
            'apikey': self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params)
            print(f"  Response status: {response.status_code}")

            if response.status_code != 200:
                print(f"  HTTP Error: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return []

            data = response.json()

            if data['status'] == '1':
                return data['result']
            else:
                print(f"  API Error: {data.get('message', 'Unknown error')}")
                print(f"  Full response: {data}")
                return []
        except Exception as e:
            print(f"  Exception occurred: {e}")
            print(f"  Response text: {response.text[:200] if 'response' in locals() else 'No response'}")
            return []

    def fetch_normal_transactions(self, start_block=0, end_block=99999999, page=1, offset=100):
        """Fetch normal transactions"""
        print(f"Fetching normal transactions (page {page})...")

        params = {
            'module': 'account',
            'action': 'txlist',
            'address': self.address,
            'startblock': start_block,
            'endblock': end_block,
            'page': page,
            'offset': offset,
            'sort': 'desc',
            'apikey': self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params)
            print(f"  Response status: {response.status_code}")

            if response.status_code != 200:
                print(f"  HTTP Error: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return []

            data = response.json()

            if data['status'] == '1':
                return data['result']
            else:
                print(f"  API Error: {data.get('message', 'Unknown error')}")
                print(f"  Full response: {data}")
                return []
        except Exception as e:
            print(f"  Exception occurred: {e}")
            print(f"  Response text: {response.text[:200] if 'response' in locals() else 'No response'}")
            return []

    def fetch_internal_transactions(self, start_block=0, end_block=99999999, page=1, offset=100):
        """Fetch internal transactions"""
        print(f"Fetching internal transactions (page {page})...")

        params = {
            'module': 'account',
            'action': 'txlistinternal',
            'address': self.address,
            'startblock': start_block,
            'endblock': end_block,
            'page': page,
            'offset': offset,
            'sort': 'desc',
            'apikey': self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params)
            print(f"  Response status: {response.status_code}")

            if response.status_code != 200:
                print(f"  HTTP Error: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return []

            data = response.json()

            if data['status'] == '1':
                return data['result']
            else:
                print(f"  API returned status 0 (might be empty or rate limited)")
                return []
        except Exception as e:
            print(f"  Exception occurred: {e}")
            return []

    def fetch_all_data(self, max_pages=10):
        """Fetch all transaction data"""
        print(f"\n{'='*60}")
        print(f"Analyzing address: {self.address}")
        print(f"{'='*60}\n")

        # Fetch token transfers
        for page in range(1, max_pages + 1):
            transfers = self.fetch_token_transfers(page=page, offset=100)
            if not transfers:
                break
            self.token_transfers.extend(transfers)
            time.sleep(0.2)  # Rate limiting

        # Fetch normal transactions
        for page in range(1, max_pages + 1):
            txs = self.fetch_normal_transactions(page=page, offset=100)
            if not txs:
                break
            self.transactions.extend(txs)
            time.sleep(0.2)

        # Fetch internal transactions
        self.internal_txs = self.fetch_internal_transactions(page=1, offset=100)

        print(f"\nFetched {len(self.token_transfers)} token transfers")
        print(f"Fetched {len(self.transactions)} normal transactions")
        print(f"Fetched {len(self.internal_txs)} internal transactions\n")

    def analyze_tokens(self):
        """Analyze which tokens are being traded"""
        print(f"\n{'='*60}")
        print("TOKEN ANALYSIS")
        print(f"{'='*60}\n")

        tokens_in = defaultdict(lambda: {'count': 0, 'total': 0})
        tokens_out = defaultdict(lambda: {'count': 0, 'total': 0})

        for tx in self.token_transfers:
            token_name = tx.get('tokenName', 'Unknown')
            token_symbol = tx.get('tokenSymbol', 'UNK')
            token_address = tx.get('contractAddress', '')
            value = int(tx.get('value', 0))
            decimals = int(tx.get('tokenDecimal', 18))

            token_id = f"{token_symbol} ({token_name})"

            if tx['to'].lower() == self.address:
                # Incoming
                tokens_in[token_id]['count'] += 1
                tokens_in[token_id]['total'] += value / (10 ** decimals)
                tokens_in[token_id]['address'] = token_address
            elif tx['from'].lower() == self.address:
                # Outgoing
                tokens_out[token_id]['count'] += 1
                tokens_out[token_id]['total'] += value / (10 ** decimals)
                tokens_out[token_id]['address'] = token_address

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

        if not self.token_transfers:
            print("No token transfers to analyze")
            return

        # Group by transaction hash to find swaps
        tx_groups = defaultdict(list)
        for transfer in self.token_transfers:
            tx_hash = transfer['hash']
            tx_groups[tx_hash].append(transfer)

        swaps = []
        for tx_hash, transfers in tx_groups.items():
            if len(transfers) >= 2:
                # Likely a swap
                ins = [t for t in transfers if t['to'].lower() == self.address]
                outs = [t for t in transfers if t['from'].lower() == self.address]

                if ins and outs:
                    swaps.append({
                        'hash': tx_hash,
                        'timestamp': transfers[0]['timeStamp'],
                        'tokens_in': ins,
                        'tokens_out': outs
                    })

        print(f"Identified {len(swaps)} potential swap transactions\n")

        # Analyze timing
        if swaps:
            timestamps = [int(s['timestamp']) for s in swaps]
            time_diffs = []
            for i in range(1, len(timestamps)):
                time_diffs.append(timestamps[i-1] - timestamps[i])

            if time_diffs:
                avg_time = sum(time_diffs) / len(time_diffs)
                print(f"Average time between swaps: {avg_time / 60:.2f} minutes")
                print(f"Min time between swaps: {min(time_diffs) / 60:.2f} minutes")
                print(f"Max time between swaps: {max(time_diffs) / 3600:.2f} hours")

        # Show recent swaps
        print("\nRECENT SWAPS (last 10):")
        for swap in swaps[:10]:
            dt = datetime.fromtimestamp(int(swap['timestamp']))
            print(f"\n  {dt.strftime('%Y-%m-%d %H:%M:%S')} - Tx: {swap['hash'][:10]}...")

            for token_out in swap['tokens_out']:
                symbol = token_out.get('tokenSymbol', 'UNK')
                value = int(token_out.get('value', 0)) / (10 ** int(token_out.get('tokenDecimal', 18)))
                print(f"    OUT: {value:,.4f} {symbol}")

            for token_in in swap['tokens_in']:
                symbol = token_in.get('tokenSymbol', 'UNK')
                value = int(token_in.get('value', 0)) / (10 ** int(token_in.get('tokenDecimal', 18)))
                print(f"    IN:  {value:,.4f} {symbol}")

        return swaps

    def analyze_contracts_interacted(self):
        """Analyze which contracts/DEXs the bot interacts with"""
        print(f"\n{'='*60}")
        print("CONTRACT INTERACTION ANALYSIS")
        print(f"{'='*60}\n")

        contract_interactions = Counter()

        for tx in self.transactions:
            if tx['to']:
                contract_interactions[tx['to'].lower()] += 1

        print("TOP CONTRACTS INTERACTED WITH:")
        for contract, count in contract_interactions.most_common(15):
            print(f"  {contract}: {count} interactions")

        return contract_interactions

    def analyze_gas_patterns(self):
        """Analyze gas usage patterns"""
        print(f"\n{'='*60}")
        print("GAS PATTERN ANALYSIS")
        print(f"{'='*60}\n")

        gas_prices = []
        gas_used = []

        for tx in self.transactions:
            if tx.get('gasPrice'):
                gas_prices.append(int(tx['gasPrice']) / 1e9)  # Convert to Gwei
            if tx.get('gasUsed'):
                gas_used.append(int(tx['gasUsed']))

        if gas_prices:
            print(f"Average gas price: {sum(gas_prices)/len(gas_prices):.2f} Gwei")
            print(f"Min gas price: {min(gas_prices):.2f} Gwei")
            print(f"Max gas price: {max(gas_prices):.2f} Gwei")

        if gas_used:
            print(f"Average gas used: {sum(gas_used)/len(gas_used):,.0f}")
            print(f"Min gas used: {min(gas_used):,}")
            print(f"Max gas used: {max(gas_used):,}")

    def identify_strategy(self, swaps):
        """Attempt to identify the trading strategy"""
        print(f"\n{'='*60}")
        print("STRATEGY IDENTIFICATION")
        print(f"{'='*60}\n")

        strategies = []

        # Analyze swap patterns
        if swaps:
            # Check for arbitrage (quick back-and-forth trades)
            token_pairs = []
            for swap in swaps:
                out_tokens = set(t.get('tokenSymbol') for t in swap['tokens_out'])
                in_tokens = set(t.get('tokenSymbol') for t in swap['tokens_in'])
                token_pairs.append((frozenset(out_tokens), frozenset(in_tokens)))

            pair_counter = Counter(token_pairs)
            if len(pair_counter) > 0:
                most_common_pair, count = pair_counter.most_common(1)[0]
                if count > len(swaps) * 0.3:  # If one pair is >30% of trades
                    strategies.append(f"Focused trading on specific token pair (appears in {count}/{len(swaps)} swaps)")

            # Check timing for MEV/frontrunning
            timestamps = [int(s['timestamp']) for s in swaps]
            time_diffs = []
            for i in range(1, len(timestamps)):
                diff = timestamps[i-1] - timestamps[i]
                time_diffs.append(diff)

            if time_diffs:
                quick_trades = sum(1 for d in time_diffs if d < 60)  # Trades within 1 minute
                if quick_trades > len(time_diffs) * 0.5:
                    strategies.append(f"High-frequency trading detected ({quick_trades}/{len(time_diffs)} trades within 60s of previous)")

        # Analyze transaction patterns
        if len(self.transactions) > 0:
            failed_txs = sum(1 for tx in self.transactions if tx.get('isError') == '1')
            success_rate = (len(self.transactions) - failed_txs) / len(self.transactions) * 100
            print(f"Transaction success rate: {success_rate:.1f}%")

            if failed_txs > len(self.transactions) * 0.2:
                strategies.append(f"High failure rate ({failed_txs} failed) - possibly frontrunning/sniping attempts")

        print("\nIDENTIFIED PATTERNS:")
        for strategy in strategies:
            print(f"  • {strategy}")

        if not strategies:
            print("  • Unable to identify clear strategy from available data")
            print("  • Consider analyzing more transactions or checking contract code")

        return strategies

    def generate_report(self):
        """Generate complete analysis report"""
        self.fetch_all_data(max_pages=10)

        tokens_in, tokens_out = self.analyze_tokens()
        swaps = self.analyze_trading_patterns()
        contracts = self.analyze_contracts_interacted()
        self.analyze_gas_patterns()
        strategies = self.identify_strategy(swaps)

        print(f"\n{'='*60}")
        print("ANALYSIS COMPLETE")
        print(f"{'='*60}\n")

        # Save raw data
        output = {
            'address': self.address,
            'analysis_date': datetime.now().isoformat(),
            'token_transfers': self.token_transfers[:100],  # Save first 100
            'transactions': self.transactions[:100],
            'identified_strategies': strategies,
            'top_contracts': dict(contracts.most_common(10))
        }

        with open(f'bot_analysis_{self.address[:8]}.json', 'w') as f:
            json.dump(output, f, indent=2)

        print(f"Raw data saved to bot_analysis_{self.address[:8]}.json")


def main():
    # Target address
    address = "0xeffcc79a8572940cee2238b44eac89f2c48fda88"

    # You can get a free API key from polygonscan.com
    api_key = "YourApiKeyToken"  # Replace with your API key for better rate limits

    analyzer = BotAnalyzer(address, api_key)
    analyzer.generate_report()


if __name__ == "__main__":
    main()
