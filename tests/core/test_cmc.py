"""test cmc (coinmarketcap)"""

import os
from dotenv import load_dotenv
from btc_cycles.core.sources.cmc import CoinMarketCap

# from cryptocmd import CmcScraper


load_dotenv()


def test_CoinMarketCap():
    """test CoinMarketCap"""
    cmc = CoinMarketCap(api_key=os.getenv("CMC_API_KEY"))
    data = cmc.get_historical_data("BTC", "2020-01-01", "2020-01-02")
    assert isinstance(data, dict)
