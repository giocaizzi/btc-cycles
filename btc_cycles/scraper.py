"""scraper module"""

from cryptocmd import CmcScraper


class Scraper:
    """Scraper"""

    def __init__(self):
        self.coin = "BTC"

    def get_data(self):
        """Get historical OHLC data
        
        Returns:
            DataFrame: OHLC data
        """
        scraper = CmcScraper(self.coin)
        scraper.get_data()
        return scraper.get_dataframe()
