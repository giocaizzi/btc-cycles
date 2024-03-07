"""bitcoin module"""

from .halving import get_halving_data

import pandas as pd
import datetime

HALVINGS = [
    (datetime.datetime(2012, 11, 28), 210000),
    (datetime.datetime(2016, 7, 9), 420000),
    (datetime.datetime(2020, 5, 11), 630000),
]


class Bitcoin:
    """Bitcoin"""

    def __init__(self):
        self.name = "Bitcoin"
        self.founded = datetime.datetime(2009, 1, 3)
        self._set_history()

    def _set_history(self):
        self.history = pd.DataFrame(
            [(self.founded, 0)] + HALVINGS + [(get_halving_data())],
            columns=["Date", "block"],
        )
        ## cycle length
        self.history["cycle_length"] = (self.history["Date"].diff().dt.days).shift(-1)
        # cycle id
        self.history["cycle"] = self.history.index+1
        # halving
        self.history["Halving"] = self.history["Date"]
