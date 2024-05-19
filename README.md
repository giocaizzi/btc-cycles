# btc-cycles

[![Update chart](https://github.com/giocaizzi/btc-cycles/actions/workflows/run.yml/badge.svg)](https://github.com/giocaizzi/btc-cycles/actions/workflows/run.yml)

> ❗ The chart is updated everyday at 5 AM UTC.

![Bitcoin](https://github.com/giocaizzi/btc-cycles/blob/main/bitcoin.png)

---

- Bitcoin price data is fetched, as default, from [coinmarketcap](https://www.coinmarketcap.com) which returns limited amount of data points. Specify different `source` (like [coincompare](https://www.cryptocompare.com/)) with relative `api_key` to fetch the whole historical dataset from the specified source.
- Cycles are computed considering _past halving dates_ and the _expected future halving date_ fetched from [watchguru](https://watcher.guru/bitcoin-halving)

## Documentation

See this [notebook](https://github.com/giocaizzi/btc-cycles/bitcoin.ipynb).
