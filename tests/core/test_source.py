import pytest

from btc_cycles.core.sources.source import DataSourceError, Source


def test_cryptocompare_no_data_raises(mocker):
    # the library returns None on API errors (e.g. quota exhausted)
    mocker.patch(
        "cryptocompare.get_historical_price_day_from", return_value=None
    )
    with pytest.raises(DataSourceError, match="no data returned"):
        Source("cryptocompare").get_data("BTC", "USD")
