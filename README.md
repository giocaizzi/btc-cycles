# btc-cycles

[![Update chart](https://github.com/giocaizzi/btc-cycles/actions/workflows/run.yml/badge.svg)](https://github.com/giocaizzi/btc-cycles/actions/workflows/run.yml)

---

> ❗ This chart is updated everyday at 5 AM UTC.

![Bitcoin](https://github.com/giocaizzi/btc-cycles/blob/main/bitcoin.png)

---

## Deprecation warning

> ⚠️ Since v0.3, as _CoinmarketCap v1 API has been deprecated_, **all working sources require an API key** to fetch data. The legacy free *(but broken!)* source `coinmarketcap-free` is however still available, hoping for a workaround is found ([see here](https://github.com/guptarohit/cryptoCMD/issues/86)).

## Install

```bash
pip install btc-cycles
```

## Usage

- **Bitcoin price** data is fetched from a set of available sources, such as:

  - [`coinmarketcap`](https://www.coinmarketcap.com), requires **paid** `api_key`.
  - [`coincompare`](https://www.cryptocompare.com/), requires **free-tier** `api_key`.
  - [`coinmarketcap-free`](https://www.coinmarketcap.com): free *(but broken!)* legacy source, available hoping for a workaround,  ([see here](https://github.com/guptarohit/cryptoCMD/issues/86))

- **Cycles** are computed considering _past halving dates_ and the _expected future halving date_ fetched from [watchguru](https://watcher.guru/bitcoin-halving)

## Documentation

See this [notebook](https://github.com/giocaizzi/btc-cycles/bitcoin.ipynb).
