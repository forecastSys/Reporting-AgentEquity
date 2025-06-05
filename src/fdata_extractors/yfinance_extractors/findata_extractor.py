from src.fdata_extractors.yfinance_extractors.findata_validator import YFinanceValidator
from src.fdata_extractors.decorator import apply_selection, apply_selection_growth
from typing import List
import yfinance as yf
import pandas as pd
import yahooquery


class YFinanceAnalyzer(YFinanceValidator):
    """
    A class to retrieve financial metrics for a given ticker using yfinance_extractors.
    Each metric is exposed through its own method for clarity and flexibility.
    """

    def __init__(self, ticker: str):
        """
        Initialize with a ticker symbol.

        Parameters:
        ticker (str): The stock ticker, e.g. "AAPL".
        """
        super().__init__()
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

        period: yfinance_extractors period string (e.g., '5d', '1mo', '1y').
        interval: data interval (e.g., '1d', '1h').
        """
        hist = self.ticker.history(period=period, interval=interval)
        return hist["Close"]

    # def get_eps(self, n_quarters: int = 4) -> float:
    #     """
    #     Calculate EPS over the last n_quarters (default TTM = 4 quarters).
    #     """
    #     ni = self.quarterly_income.loc["Net Income"][:n_quarters].sum()
    #     shares = self.info.get("sharesOutstanding", 1)
    #     return ni / shares
    #
    # def get_pe_ratio(self, price_period: str = "1d", price_interval: str = "1d", n_quarters: int = 4) -> float:
    #     """
    #     Calculate P/E ratio based on latest close price and EPS (TTM by default).
    #     """
    #     price_series = self.get_price(period=price_period, interval=price_interval)
    #     latest_price = price_series.iloc[-1]
    #     eps = self.get_eps(n_quarters)
    #     return latest_price / eps
    #
    # def get_income_statement(self, n_quarters: int = 4) -> pd.DataFrame:
    #     """
    #     Retrieve the income statement for the last n_quarters.
    #     """
    #     return self.quarterly_income.iloc[:, :n_quarters]
    #
    # def get_total_revenue(self, n_quarters: int = 4) -> pd.Series:
    #     """
    #     Get total revenue for the last n_quarters.
    #     """
    #     return self.quarterly_financials.loc["Total Revenue"][:n_quarters]
    #
    # def get_gross_profit(self, n_quarters: int = 4) -> pd.Series:
    #     """
    #     Get net profit (Net Income) for the last n_quarters.
    #     """
    #     return self.quarterly_financials.loc["Gross Profit"][:n_quarters]
    #
    # # def get_ebitda(self, n_quarters: int = 4) -> pd.Series:
    # #     """
    # #     Get EBITDA for last n_quarters.
    # #     """
    # #     return self.quarterly_financials.loc["EBITDA"][:n_quarters]
    #
    # def get_ma15(self, period: str = "6mo", interval: str = "1d") -> pd.Series:
    #     """
    #     15-day moving average of closing prices.
    #     """
    #     prices = self.get_price(period=period, interval=interval)
    #     return prices.rolling(window=15).mean()
    #
    # def get_ma30(self, period: str = "6mo", interval: str = "1d") -> pd.Series:
    #     """
    #     30-day moving average of closing prices.
    #     """
    #     prices = self.get_price(period=period, interval=interval)
    #     return prices.rolling(window=30).mean()
    #
    # def get_ma60(self, period: str = "6mo", interval: str = "1d") -> pd.Series:
    #     """
    #     60-day moving average of closing prices.
    #     """
    #     prices = self.get_price(period=period, interval=interval)
    #     return prices.rolling(window=60).mean()
    #
    # def get_ma90(self, period: str = "6mo", interval: str = "1d") -> pd.Series:
    #     """
    #     90-day moving average of closing prices.
    #     """
    #     prices = self.get_price(period=period, interval=interval)
    #     return prices.rolling(window=90).mean()
    #
    # def get_ma180(self, period: str = "1y", interval: str = "1d") -> pd.Series:
    #     """
    #     180-day moving average of closing prices.
    #     """
    #     prices = self.get_price(period=period, interval=interval)
    #     return prices.rolling(window=180).mean()
    #
    # def get_all_mas(self,
    #                 price_period: str = "1y",
    #                 price_interval: str = "1d",
    #                 ma_windows: list[int] = [15, 30, 60, 90, 120]
    #                 ) -> pd.DataFrame:
    #     """
    #     Returns a DataFrame with the close price and moving averages for each window.
    #
    #     Parameters:
    #     -----------
    #     price_period : str
    #         yfinance_extractors period for historical prices (e.g., "6mo", "1y").
    #     price_interval : str
    #         yfinance_extractors data interval (e.g., "1d", "1h").
    #     ma_windows : list of int
    #         List of rolling‐window lengths (in periods) to compute MAs for.
    #
    #     Returns:
    #     --------
    #     pd.DataFrame
    #         Indexed by date, columns = ["Close", "MA15", "MA30", …].
    #     """
    #     # fetch the base close‐price series once
    #     prices = self.get_price(period=price_period, interval=price_interval)
    #
    #     # start DataFrame
    #     df = pd.DataFrame({"Close": prices})
    #
    #     # compute each moving average
    #     for w in ma_windows:
    #         df[f"MA{w}"] = prices.rolling(window=w).mean()
    #
    #     return df
    #
    # def get_sp500(self, period: str = "1mo", interval: str = "1d") -> pd.Series:
    #     """
    #     Get historical closing prices for the S&P 500 index.
    #     """
    #     hist = self.market_ticker.history(period=period, interval=interval)
    #     return hist["Close"]
    #
    # def get_beta(self, period: str = "6mo", interval: str = "1d") -> float:
    #     """
    #     Calculate the beta of the stock relative to the S&P 500 over the specified period.
    #     """
    #     stock = self.get_price(period=period, interval=interval).pct_change().dropna()
    #     market = self.get_sp500(period=period, interval=interval).pct_change().dropna()
    #     df = pd.concat([stock, market], axis=1, join="inner")
    #     df.columns = ["stock", "market"]
    #     cov = df["stock"].cov(df["market"])
    #     var = df["market"].var()
    #     return cov / var
    #
    # def get_past_fiscal_year_end_shares(self, period: str = "5y") -> pd.DataFrame:
    #
    #     t = self.query_ticker
    #     df = t.income_statement(frequency='a', trailing=True)
    #     df = df[df.periodType == '12M']
    #     df = self.output_yfinance_format(df, date_name='asOfDate', output_colname='BasicAverageShares')
    #     return df
    #
    # def get_past_fiscal_year_end_stock_price(self,
    #                                          period_end_month: int,
    #                                          period_end_day: int,
    #                                          period: str = "5y") -> pd.DataFrame:
    #
    #     price_hist = self.get_price(period=period, interval="1d")
    #     price_hist = price_hist.reset_index()
    #     price_hist.Date = price_hist.Date.apply(lambda x: x.date())
    #     price_hist = price_hist.sort_values('Date')
    #     full_idx = pd.date_range(price_hist.Date.min(), price_hist.Date.max(), freq='D')
    #
    #     price_hist = price_hist.set_index("Date").reindex(full_idx).ffill()
    #     price_hist = price_hist.reset_index().rename(columns={"index": "Date"})
    #
    #     price_hist = price_hist[price_hist['Date'].dt.month.eq(period_end_month) & price_hist['Date'].dt.day.eq(period_end_day)]
    #
    #     df = self.output_yfinance_format(price_hist, date_name="Date", output_colname="Close")
    #     return df

    def get_past_yearly_financial(self) -> pd.DataFrame:
        """Get yearly financial data"""
        df = self.ticker.financials.T
        return df.sort_index()
    def get_past_quarterly_financial(self) -> pd.DataFrame:
        """Get quarterly financial data"""
        df = self.ticker.quarterly_financials.T
        return df.sort_index()
    def get_past_yearly_income_statement(self) -> pd.DataFrame:
        """Get yearly income statement data"""
        df = self.ticker.income_stmt.T
        return df.sort_index()

    def get_past_quarterly_income_statement(self) -> pd.DataFrame:
        """Get quarterly income statement data"""
        df = self.ticker.quarterly_income_stmt.T
        return df.sort_index()

    def get_past_yearly_cash_flow(self) -> pd.DataFrame:
        """Get yearly cash flow data"""
        df = self.ticker.cash_flow.T
        return df.sort_index()

    def get_past_quarterly_cash_flow(self) -> pd.DataFrame:
        """Get quarterly cash flow data"""
        df = self.ticker.quarterly_cash_flow.T
        return df.sort_index()

    def get_past_yearly_balance_sheet(self) -> pd.DataFrame:
        """Get yearly balance sheet data"""
        df = self.ticker.balance_sheet.T
        return df.sort_index()

    def get_past_quarterly_balance_sheet(self) -> pd.DataFrame:
        """Get quarterly balance sheet data"""
        df = self.ticker.quarterly_balance_sheet.T
        return df.sort_index()

    @apply_selection
    def get_selected_financial(self, quarterly: bool) -> pd.DataFrame:
        """Get selected financial data
        kwargs:
            n_years / n_quarters (max4): number of years data to return / number of quarters to return
            selected_columns: list of column to return
        """
        return self.get_past_quarterly_financial() if quarterly else self.get_past_yearly_financial()

    @apply_selection
    def get_selected_cash_flow(self, quarterly: bool) -> pd.DataFrame:
        """Get selected cash flow data
        kwargs:
            n_years / n_quarters (max4): number of years data to return / number of quarters to return
            selected_columns: list of column to return
        """
        return self.get_past_quarterly_cash_flow() if quarterly else self.get_past_yearly_cash_flow()

    @apply_selection
    def get_selected_balance_sheet(self, quarterly: bool) -> pd.DataFrame:
        """Get selected balance sheet data
        kwargs:
            n_years / n_quarters (max4): number of years data to return / number of quarters to return
            selected_columns: list of column to return
        """
        return self.get_past_quarterly_balance_sheet() if quarterly else self.get_past_yearly_balance_sheet()

    @apply_selection
    def get_selected_income_statement(self, quarterly: bool) -> pd.DataFrame:
        """Get selected income statement data
        kwargs:
            n_years / n_quarters (max4): number of years data to return / number of quarters to return
            selected_columns: list of column to return
        """
        return self.get_past_quarterly_income_statement() if quarterly else self.get_past_yearly_income_statement()

    ## -- Growth rate data
    @apply_selection_growth
    def get_selected_financial_growth(self, quarterly: bool) -> pd.DataFrame:
        """Get selected financial growth data
        kwargs:
            n_years / n_quarters (max4): number of years data to return / number of quarters to return
            selected_columns: list of column to return
        """
        return self.get_past_quarterly_financial() if quarterly else self.get_past_yearly_financial()

    @apply_selection_growth
    def get_selected_cash_flow_growth(self, quarterly: bool) -> pd.DataFrame:
        """Get selected cash flow growth data
        kwargs:
            n_years / n_quarters (max4): number of years data to return / number of quarters to return
            selected_columns: list of column to return
        """
        return self.get_past_quarterly_cash_flow() if quarterly else self.get_past_yearly_cash_flow()

    @apply_selection_growth
    def get_selected_balance_sheet_growth(self, quarterly: bool) -> pd.DataFrame:
        """Get selected balance sheet growth data
        kwargs:
            n_years / n_quarters (max4): number of years data to return / number of quarters to return
            selected_columns: list of column to return
        """
        return self.get_past_quarterly_balance_sheet() if quarterly else self.get_past_yearly_balance_sheet()

    @apply_selection_growth
    def get_selected_income_statement_growth(self, quarterly: bool) -> pd.DataFrame:
        """Get selected income statement growth data
        kwargs:
            n_years / n_quarters (max4): number of years data to return / number of quarters to return
            selected_columns: list of column to return
        """
        return self.get_past_quarterly_income_statement() if quarterly else self.get_past_yearly_income_statement()

    def get_selected_financial_v1(self, n_quarters: int = None, n_years: int = None, selected_columms: List = None) -> pd.DataFrame:
        """Get financial data over a number of quarters or years (mutually exclusive)."""
        df = self.get_past_quarterly_financial() if n_quarters is not None else self.get_past_yearly_financial()
        column_names = df.columns.tolist()
        self.validate(n_quarters=n_quarters, n_years=n_years, selected_columms=selected_columms, column_names=column_names,class_name=self.__class__.__name__)
        if n_quarters is not None:
            df = df[-n_quarters:] # select most recent 4 quarters
            return df[selected_columms].dropna()
        else:
            df = df[-n_years:]
            return df[selected_columms].dropna()

if __name__ == "__main__":
    # Example usage:
    analyzer = YFinanceAnalyzer("AAPL")
    # analyzer.get_past_quarterly_financial()
    # analyzer.get_past_fiscal_year_end_stock_price(period_end="09-30")
    # analyzer.get_past_fiscal_year_end_shares(period="5y")
    # analyzer.get_ebitda(n_quarters=4)
    # analyzer.get_ebitda(n_years=4)
    #
    # print(analyzer.get_selected_financial(n_years=4,selected_columms=['Total Revenue']))
    # print('--')
    # print(analyzer.get_selected_financial_v1(n_years=4,selected_columms=['Total Revenue']))


    print(analyzer.get_selected_financial_growth(n_years=4, selected_columns=['Total Revenue', 'EBITDA']))

