"""halving module"""

import requests
import datetime

URL = "https://api.watcher.guru/bitcoinhalving/predictions"


def get_halving_predicted_date():
    """Get halving predicted date

    Returns:
        datetime: predicted halving date
    """
    current_status = requests.get(URL).json()
    return datetime.datetime.fromtimestamp(
        current_status["target"]["predicted_timestamp"]
    )
