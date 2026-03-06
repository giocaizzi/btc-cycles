# Project

`btc_cycles` is a repository for analyzing Bitcoin's price trends against its halving cycles. The idea is to a have a repository with a useful readme showing a everyday updated chart of Bitcoin's price against its halving cycles, and notebooks with additional analysis.

Read more in [README.md](./README.md).

# `bitcoin.ipynb`

This repo has a [bitcoin.ipynb](./notebooks/bitcoin.ipynb) notebook that contains the code producing [bitcoin.png](./notebooks/bitcoin.png), the chart shown in the README.
Keep the notebook updated.

The notebook is run everyday at everyday at 5:00 UTC by the [run.yml](./.github/workflows/run.yml) GitHub Action workflow, which commits the updated notebook and chart to the repository.