#!/usr/bin/env python3
"""
Dump the full JSON of one market to see all available fields
"""

from polymarket_api import PolymarketAPI
import json

api = PolymarketAPI()
markets = api.get_hourly_crypto_markets()

if markets and len(markets) > 0:
    print("="*60)
    print("FULL MARKET JSON (First Market)")
    print("="*60)
    print(json.dumps(markets[0], indent=2))
else:
    print("No markets found")
