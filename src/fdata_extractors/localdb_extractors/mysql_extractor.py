from yfinance import tickers

from src.database import MySQLHandler
import pandas as pd

class MySQLExtractor:

    def __init__(self, ticker):
        sql = MySQLHandler()
        self.ticker = ticker
        self.engine = sql._get_engine()

    def _get_competitors(self, competitors_limit):

        df_competitors = pd.read_sql("SELECT * FROM caesars_reporting_system.competitors_selectedfrom1100", self.engine)
        return df_competitors[df_competitors["company_ticker"] == self.ticker].reset_index(drop=True).iloc[:competitors_limit]


if __name__ == "__main__":
    extractor = MySQLExtractor(ticker='AAPL')
    print(extractor._get_competitors())

