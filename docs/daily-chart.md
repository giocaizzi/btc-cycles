# Daily chart update

[bitcoin.ipynb](../notebooks/bitcoin.ipynb) produces [bitcoin.png](../notebooks/bitcoin.png), the chart shown in the README.

The [run.yml](../.github/workflows/run.yml) workflow runs every day at 5:00 UTC (or manually via `workflow_dispatch`):

1. Executes the notebook in place (`uv run jupyter nbconvert --execute --inplace`).
2. Generates the interactive plotly chart with a standalone Python script (not from the notebook) into `_site/index.html`.
3. If `bitcoin.png` changed, commits `notebooks/` as `GitHub Action` and pushes to `main`.
4. Deploys `_site` to GitHub Pages (`actions/upload-pages-artifact` + `actions/deploy-pages`), served at <https://giocaizzi.github.io/btc-cycles/>.

GitHub Pages must deploy from GitHub Actions (Settings → Pages → Source → GitHub Actions).

## Run manually

```bash
gh workflow run run.yml
```
