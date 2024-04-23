"""halving module"""

import json
import requests
import datetime
import pandas as pd

URL = "https://api.watcher.guru/bitcoinhalving/predictions"


def get_halving_data() -> tuple:
    """Get halving predicted date

    Returns:
        tuple: date (datetime), block (int)
    """
    response = requests.get(URL).json()
    date = datetime.datetime.fromtimestamp(response["target"]["predicted_timestamp"])
    # localize utc
    date = date.replace(tzinfo=datetime.timezone.utc)
    block = int(response["target"]["block_number"])
    return date, block


def update_predicted_halving_date(data: pd.DataFrame) -> pd.DataFrame:
    """Update predicted halving date

    Args:
        data (DataFrame): halving data

    Returns:
        DataFrame: updated halving data
    """
    # TODO: what happends if response is not
    # updated in time? (like in 2024)
    date, block = get_halving_data()
    # update predicted halving date
    data.loc[data["block"] == block, "Date"] = date
    return data


class Halvings:
    """Halvings

    Attributes:
        data (pd.DataFrame): halving data
    """

    def __init__(self):
        # load json data into DataFrame
        with open("btc_cycles/core/halvings.json", "r") as f:
            self.data = pd.DataFrame(json.load(f)).T
        # convert date to datetime
        self.data["date"] = pd.to_datetime(self.data["date"])
        self.data.index.name = "block"
        # Date with capital D
        self.data.rename(columns={"date": "Date"}, inplace=True)
        # reset index
        self.data.reset_index(inplace=True)
        self.data["block"] = self.data["block"].astype(int)
        # update predicted halving date
        self.data = update_predicted_halving_date(self.data)
        # cycle length, forced to int
        self.data["cycle_length"] = (self.data["Date"].diff().dt.days).shift(-1)
        # cycle id
        self.data["cycle_id"] = range(1, len(self.data) + 1)