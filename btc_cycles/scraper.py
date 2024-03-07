"""scraper module"""

from cryptocmd import CmcScraper


class Scraper:
    """Scraper class

    Attributes:
        coin: str, coin to scrape
    """

    def __init__(self, coin):
        self.coin = coin

    def get_data(self):
        """Get data from coin"""
        scraper = CmcScraper(self.coin)
        scraper.get_data()
        return scraper.get_dataframe()
