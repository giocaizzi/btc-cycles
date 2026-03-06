<div align="center">

# btc-cycles

**Bitcoin price analysis across halving cycles.**

[![PyPI](https://img.shields.io/pypi/v/btc-cycles?color=blue)](https://pypi.org/project/btc-cycles/)
[![Python](https://img.shields.io/pypi/pyversions/btc-cycles)](https://pypi.org/project/btc-cycles/)
[![Tests](https://github.com/giocaizzi/btc-cycles/actions/workflows/deployment.yml/badge.svg?branch=main)](https://github.com/giocaizzi/btc-cycles/actions/workflows/deployment.yml)
[![Update chart](https://github.com/giocaizzi/btc-cycles/actions/workflows/run.yml/badge.svg)](https://github.com/giocaizzi/btc-cycles/actions/workflows/run.yml)
[![Codecov](https://codecov.io/gh/giocaizzi/btc-cycles/branch/main/graph/badge.svg)](https://codecov.io/gh/giocaizzi/btc-cycles)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

> This chart is updated daily at 5:00 UTC.

[**Interactive chart**](https://giocaizzi.github.io/btc-cycles/) | [Static chart](https://github.com/giocaizzi/btc-cycles/blob/main/notebooks/bitcoin.png)

![Bitcoin](https://github.com/giocaizzi/btc-cycles/blob/main/notebooks/bitcoin.png)

---

Fetch Bitcoin price data, enrich it with halving cycle metrics (ATH, cycle progress, cycle lows), and render a polar chart. Cycles are computed using past halving dates and the predicted next halving from [watcher.guru](https://watcher.guru/bitcoin-halving).

```python
from btc_cycles import Bitcoin

btc = Bitcoin(
    source="cryptocompare",
    api_key="YOUR_API_KEY",
)

# static chart (matplotlib)
fig = btc.plot(from_date="2012-11-28")
fig.savefig("bitcoin.png")

# interactive chart (plotly)
fig = btc.plot(kind="interactive", from_date="2012-11-28")
fig.write_html("bitcoin.html")
```

## Installation

```bash
pip install btc-cycles
```

## Data Sources

| Source | API Key | Status |
|--------|---------|--------|
| [`cryptocompare`](https://www.cryptocompare.com/) | Free tier | **Default** |
| [`coinmarketcap`](https://www.coinmarketcap.com) | Paid | Not implemented |
| `coinmarketcap-free` | None | Broken ([ref](https://github.com/guptarohit/cryptoCMD/issues/86)) |

## Documentation

See the [notebook](https://github.com/giocaizzi/btc-cycles/blob/main/notebooks/bitcoin.ipynb) for a full working example.

## License

[MIT](LICENSE)
