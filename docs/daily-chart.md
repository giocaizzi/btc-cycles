# Daily chart update

[bitcoin.ipynb](../notebooks/bitcoin.ipynb) produces [bitcoin.png](../notebooks/bitcoin.png), the chart shown in the README.

The [run.yml](../.github/workflows/run.yml) workflow runs every day at 5:00 UTC (or manually via `workflow_dispatch`):

1. Executes the notebook in place (`uv run jupyter nbconvert --execute --inplace`).
2. Generates the interactive plotly chart with a standalone Python script (not from the notebook) into `_site/index.html`.
3. If `bitcoin.png` changed, commits `notebooks/` to the `bot/daily-chart` branch (force-updated each run) and opens an auto-merging squash PR `chore(data): update daily chart` (only if none is open). It authenticates with a token minted from the release-please GitHub App (secrets `RP_APP_ID`, `RP_APP_KEY`), so the push triggers CI and the PR passes the `main` ruleset.
4. Deploys `_site` to GitHub Pages (`actions/upload-pages-artifact` + `actions/deploy-pages`), served at <https://giocaizzi.github.io/btc-cycles/>.

GitHub Pages must deploy from GitHub Actions (Settings → Pages → Source → GitHub Actions). The release-please App must be installed on the repo and `RP_APP_ID` / `RP_APP_KEY` set as Actions secrets.

If CI fails on the bot PR, it stays open; the next run force-updates the branch and the PR picks up the new commit.

## Run manually

```bash
gh workflow run run.yml
```
