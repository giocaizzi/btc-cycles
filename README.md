# btc-cycles

[![Update chart](https://github.com/giocaizzi/btc-cycles/actions/workflows/run.yml/badge.svg)](https://github.com/giocaizzi/btc-cycles/actions/workflows/run.yml)
![PyPI - Version](https://img.shields.io/pypi/v/btc-cycles?color=blue)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/btc-cycles)
[![Deploy](https://github.com/giocaizzi/btc-cycles/actions/workflows/deployment.yml/badge.svg)](https://github.com/giocaizzi/btc-cycles/actions/workflows/deployment.yml)

______________________________________________________________________

> ❗ This chart is updated everyday at 5 AM UTC.

![Bitcoin](https://github.com/giocaizzi/btc-cycles/blob/main/bitcoin.png)

______________________________________________________________________

## Install

```bash
pip install btc-cycles
```

## Usage

- **Bitcoin price** data is fetched from a set of available sources, such as:

  - [`coinmarketcap`](https://www.coinmarketcap.com), requires **paid** `api_key`.
  - [`coincompare`](https://www.cryptocompare.com/), requires **free-tier** `api_key`.

  In progress (TBA):
  - [`coinmarketcap-free`](https://www.coinmarketcap.com): **free** (no `api_key` required).

- **Cycles** are computed considering _past halving dates_ and the _expected future halving date_ fetched from [watchguru](https://watcher.guru/bitcoin-halving)

## Documentation

See this [notebook](https://github.com/giocaizzi/btc-cycles/blob/main/bitcoin.ipynb).
