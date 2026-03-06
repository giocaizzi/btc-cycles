"""halving module"""

import datetime
import json
from pathlib import Path

import pandas as pd
import requests

URL = "https://api.watcher.guru/bitcoinhalving/predictions"
REQUEST_TIMEOUT = 10


class HalvingAPIError(Exception):
    """Raised when the halving prediction API is unreachable or returns invalid data."""


def get_halving_data() -> tuple[datetime.datetime, int]:
    """Get next halving data from the watcher.guru API.

    Returns:
        Predicted halving date and block number.

    Raises:
        HalvingAPIError: If the API request fails or returns unexpected data.
    """
    try:
        response = requests.get(URL, timeout=REQUEST_TIMEOUT).json()
    except (requests.RequestException, ValueError) as e:
        raise HalvingAPIError(f"Failed to fetch halving data: {e}") from e

    try:
        date = datetime.datetime.fromtimestamp(
            response["target"]["predicted_timestamp"]
        )
        date = date.replace(tzinfo=datetime.timezone.utc)
        block = int(response["target"]["block_number"])
    except (KeyError, TypeError, ValueError) as e:
        raise HalvingAPIError(f"Unexpected API response format: {e}") from e

    return date, block


def _update_predicted_halving_date(
    data: pd.DataFrame,
    prediction: tuple[datetime.datetime, int],
) -> pd.DataFrame:
    """Update the predicted halving date in the halving dataframe.

    Args:
        data: Halving data.
        prediction: Predicted halving date and block number.

    Returns:
        Updated halving data.
    """
    date, block = prediction
    data.loc[data["block"] == block, "Date"] = date
    return data


class Halvings:
    """Halving cycles data loaded from JSON with predicted next halving date.

    Args:
        prediction: Pre-fetched halving prediction to avoid redundant API calls.
            If None, fetches from the API.

    Attributes:
        data: Halving data.
    """

    def __init__(
        self,
        prediction: tuple[datetime.datetime, int] | None = None,
    ):
        halvings_path = Path(__file__).resolve().parent / "halvings.json"
        with open(halvings_path) as f:
            self.data = pd.DataFrame(json.load(f)).T

        self.data["date"] = pd.to_datetime(self.data["date"])
        self.data.index.name = "block"
        self.data.rename(columns={"date": "Date"}, inplace=True)
        self.data.reset_index(inplace=True)
        self.data["block"] = self.data["block"].astype(int)

        _prediction = prediction if prediction is not None else get_halving_data()
        self.data = _update_predicted_halving_date(self.data, _prediction)

        self.data["cycle_length"] = (self.data["Date"].diff().dt.days).shift(-1)
        self.data["cycle_id"] = range(1, len(self.data) + 1)
