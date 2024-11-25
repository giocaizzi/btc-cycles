"""CryptoCompare source"""

import cryptocompare
import pandas as pd

from btc_cycles.core.sources.base import START, Source


class CryptoCompare(Source):
    """CryptoCompare class

    Class to get historical OHLC data from CryptoCompare API.
    """

    def get_data(self, coin: str, fiat: str) -> pd.DataFrame:
        """Get historical OHLC data

        Args:
            coin (str): coin symbol
            fiat (str): currency symbol

        Returns:
            DataFrame: historical OHLC data
        """
        try:
            cryptocompare.cryptocompare._set_api_key_parameter(self.api_key)
            data = cryptocompare.get_historical_price_day_from(
                coin=coin, currency=fiat, fromTs=START
            )
            data = pd.DataFrame(data)
            data["time"] = pd.to_datetime(data["time"], unit="s")
            data.rename({"time": "Date", "close": "Close"}, axis=1, inplace=True)
            return data[["Date", "Close"]]
        except Exception as e:
            raise ValueError(f"Error getting data from 'cryptocompare' source: {e}")
