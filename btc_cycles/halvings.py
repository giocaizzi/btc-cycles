"""halving module"""

import json
import requests
import datetime
import pandas as pd

URL = "https://api.watcher.guru/bitcoinhalving/predictions"


def get_halving_data():
    """Get halving predicted date

    Returns:
        tuple: date (datetime), block (int)
    """
    response = requests.get(URL).json()
    date = datetime.datetime.fromtimestamp(response["target"]["predicted_timestamp"])
    block = response["target"]["block_number"]
    return date, block


class Halvings:
    """Halvings

    Attributes:
        data (pd.DataFrame): halving data
    """

    def __init__(self):
        # load json data into DataFrame
        with open("btc_cycles/halvings.json", "r") as f:
            self.data = pd.DataFrame(json.load(f)).T
        # convert date to datetime
        self.data["date"] = pd.to_datetime(self.data["date"])
        self.data.index.name = "block"
        # cycle length
        self.data["cycle_length"] = (self.data["date"].diff().dt.days).shift(-1)
        # cycle id
        self.data["cycle_id"] = range(1, len(self.data) + 1)
        # Date with capital D
        self.data.rename(columns={"date": "Date"}, inplace=True)
        # reset index
        self.data.reset_index(inplace=True)
