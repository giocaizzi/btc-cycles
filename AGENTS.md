# btc-cycles

Python library analyzing Bitcoin's price against its halving cycles, plus a daily-updated chart shown in the [README](./README.md) and notebooks with additional analysis.

## Commands

- `make help` lists targets; `make check` (= `lint` + `test`) is what CI runs.
- Python tooling is `uv` only (`uv sync` to install).

## Rules

- Changes land on `main` only via squash-merged PRs with a Conventional Commit title; the required CI job is `check` ([ci.yml](./.github/workflows/ci.yml)). Releases via release-please.
- Keep [bitcoin.ipynb](./notebooks/bitcoin.ipynb) working: it is executed daily to produce the README chart. See [docs/daily-chart.md](./docs/daily-chart.md).
- Org-wide GitHub standard: <https://github.com/giocaizzi/.github/blob/main/docs/standard.md>.
