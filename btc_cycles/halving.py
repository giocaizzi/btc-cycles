"""halving module"""

import requests
import datetime

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
