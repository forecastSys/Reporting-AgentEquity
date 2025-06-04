import yfinance as yf
import pandas as pd
import yahooquery
from src.abstractions import FDataAbc


class YFinanceAnalyzer(FDataAbc):
    """
    A class to retrieve financial metrics for a given ticker using yfinance.
    Each metric is exposed through its own method for clarity and flexibility.
    """

    def __init__(self, ticker: str):
        """
        Initialize with a ticker symbol.

        Parameters:
        ticker (str): The stock ticker, e.g. "AAPL".
        """
        self.query_ticker = yahooquery.Ticker(ticker)
        self.ticker = yf.Ticker(ticker)
        self.info = self.ticker.info
        # Quarterly income statement and financials
        self.quarterly_income = self.ticker.quarterly_income_stmt
        self.quarterly_financials = self.ticker.quarterly_financials

        # S&P 500 index ticker for market metrics
        self.market_ticker = yf.Ticker("^GSPC")
    @staticmethod
    def output_yfinance_format(df: pd.DataFrame, date_name: str, output_colname: str) -> pd.Series:

        df = df.set_index(date_name)[output_colname].sort_index(ascending=False).rename_axis(None)
        return df

    def get_price(self, period: str = "1mo", interval: str = "1d") -> pd.Series:
        """
        Get historical closing prices for the ticker.

        period: yfinance period string (e.g., '5d', '1mo', '1y').
        interval: data interval (e.g., '1d', '1h').
        """
        hist = self.ticker.history(period=period, interval=interval)
        return hist["Close"]

    def get_eps(self, n_quarters: int = 4) -> float:
        """
        Calculate EPS over the last n_quarters (default TTM = 4 quarters).
        """
        ni = self.quarterly_income.loc["Net Income"][:n_quarters].sum()
        shares = self.info.get("sharesOutstanding", 1)
        return ni / shares

    def get_pe_ratio(self, price_period: str = "1d", price_interval: str = "1d", n_quarters: int = 4) -> float:
        """
        Calculate P/E ratio based on latest close price and EPS (TTM by default).
        """
        price_series = self.get_price(period=price_period, interval=price_interval)
        latest_price = price_series.iloc[-1]
        eps = self.get_eps(n_quarters)
        return latest_price / eps

    def get_income_statement(self, n_quarters: int = 4) -> pd.DataFrame:
        """
        Retrieve the income statement for the last n_quarters.
        """
        return self.quarterly_income.iloc[:, :n_quarters]

    def get_total_revenue(self, n_quarters: int = 4) -> pd.Series:
        """
        Get total revenue for the last n_quarters.
        """
        return self.quarterly_financials.loc["Total Revenue"][:n_quarters]

    def get_gross_profit(self, n_quarters: int = 4) -> pd.Series:
        """
        Get net profit (Net Income) for the last n_quarters.
        """
        return self.quarterly_financials.loc["Gross Profit"][:n_quarters]

    def get_ebitda(self, n_quarters: int = 4) -> pd.Series:
        """
        Get EBITDA for last n_quarters.
        """
        return self.quarterly_financials.loc["EBITDA"][:n_quarters]

    def get_ma15(self, period: str = "6mo", interval: str = "1d") -> pd.Series:
        """
        15-day moving average of closing prices.
        """
        prices = self.get_price(period=period, interval=interval)
        return prices.rolling(window=15).mean()

    def get_ma30(self, period: str = "6mo", interval: str = "1d") -> pd.Series:
        """
        30-day moving average of closing prices.
        """
        prices = self.get_price(period=period, interval=interval)
        return prices.rolling(window=30).mean()

    def get_ma60(self, period: str = "6mo", interval: str = "1d") -> pd.Series:
        """
        60-day moving average of closing prices.
        """
        prices = self.get_price(period=period, interval=interval)
        return prices.rolling(window=60).mean()

    def get_ma90(self, period: str = "6mo", interval: str = "1d") -> pd.Series:
        """
        90-day moving average of closing prices.
        """
        prices = self.get_price(period=period, interval=interval)
        return prices.rolling(window=90).mean()

    def get_ma180(self, period: str = "1y", interval: str = "1d") -> pd.Series:
        """
        180-day moving average of closing prices.
        """
        prices = self.get_price(period=period, interval=interval)
        return prices.rolling(window=180).mean()

    def get_all_mas(self,
                    price_period: str = "1y",
                    price_interval: str = "1d",
                    ma_windows: list[int] = [15, 30, 60, 90, 120]
                    ) -> pd.DataFrame:
        """
        Returns a DataFrame with the close price and moving averages for each window.

        Parameters:
        -----------
        price_period : str
            yfinance period for historical prices (e.g., "6mo", "1y").
        price_interval : str
            yfinance data interval (e.g., "1d", "1h").
        ma_windows : list of int
            List of rolling‐window lengths (in periods) to compute MAs for.

        Returns:
        --------
        pd.DataFrame
            Indexed by date, columns = ["Close", "MA15", "MA30", …].
        """
        # fetch the base close‐price series once
        prices = self.get_price(period=price_period, interval=price_interval)

        # start DataFrame
        df = pd.DataFrame({"Close": prices})

        # compute each moving average
        for w in ma_windows:
            df[f"MA{w}"] = prices.rolling(window=w).mean()

        return df

    def get_sp500(self, period: str = "1mo", interval: str = "1d") -> pd.Series:
        """
        Get historical closing prices for the S&P 500 index.
        """
        hist = self.market_ticker.history(period=period, interval=interval)
        return hist["Close"]

    def get_beta(self, period: str = "6mo", interval: str = "1d") -> float:
        """
        Calculate the beta of the stock relative to the S&P 500 over the specified period.
        """
        stock = self.get_price(period=period, interval=interval).pct_change().dropna()
        market = self.get_sp500(period=period, interval=interval).pct_change().dropna()
        df = pd.concat([stock, market], axis=1, join="inner")
        df.columns = ["stock", "market"]
        cov = df["stock"].cov(df["market"])
        var = df["market"].var()
        return cov / var

    def get_past_fiscal_year_end_shares(self, period: str = "5y") -> pd.DataFrame:

        t = self.query_ticker
        df = t.income_statement(frequency='a', trailing=True)
        df = df[df.periodType == '12M']
        df = self.output_yfinance_format(df, date_name='asOfDate', output_colname='BasicAverageShares')
        return df

    def get_past_fiscal_year_end_stock_price(self,
                                             period_end_month: int,
                                             period_end_day: int,
                                             period: str = "5y") -> pd.DataFrame:

        price_hist = self.get_price(period=period, interval="1d")
        price_hist = price_hist.reset_index()
        price_hist.Date = price_hist.Date.apply(lambda x: x.date())
        price_hist = price_hist.sort_values('Date')
        full_idx = pd.date_range(price_hist.Date.min(), price_hist.Date.max(), freq='D')

        price_hist = price_hist.set_index("Date").reindex(full_idx).ffill()
        price_hist = price_hist.reset_index().rename(columns={"index": "Date"})

        price_hist = price_hist[price_hist['Date'].dt.month.eq(period_end_month) & price_hist['Date'].dt.day.eq(period_end_day)]

        df = self.output_yfinance_format(price_hist, date_name="Date", output_colname="Close")
        return df

    def get_past_financial(self) -> pd.DataFrame:

        df = self.ticker.financials
        return df

    def get_past_balance_sheet(self) -> pd.DataFrame:
        df = self.ticker.balance_sheet
        return df


if __name__ == "__main__":
    # Example usage:
    analyzer = YFinanceAnalyzer("AAPL")
    # analyzer.get_past_fiscal_year_end_stock_price(period_end="09-30")
    # analyzer.get_past_fiscal_year_end_shares(period="5y")
    analyzer.get_past_financial()
    print(analyzer.get_price("5d"))
    print(analyzer.get_eps(n_quarters=4))
    print(analyzer.get_pe_ratio("5d", "1d", 4))

