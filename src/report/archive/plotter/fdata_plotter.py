import matplotlib.pyplot as plt
from src.fdata_extractors import YFinanceAnalyzer
import pandas as pd

class FinancialPlotter:
    """
    Generates financial chart Figure objects for a given ticker:
      1) Close price + multiple moving averages in one Figure
      2) EPS (TTM) vs. P/E ratio in one Figure
    """
    def __init__(self, ticker: str):
        self.symbol   = ticker
        self.analyzer = YFinanceAnalyzer(ticker)

    def plot_moving_averages_to_fig(self,
                                    df=None,
                                    period: str = "1y",
                                    interval: str = "1d",
                                    ma_windows: list[int] = [15, 30, 60, 90]) -> plt.Figure:
        """
        Returns a Matplotlib Figure plotting:
          - Close price
          - MA15, MA30, MA60, MA90
        If `df` is None, fetches data via analyzer.
        """
        if df is None:
            df = self.analyzer.get_all_mas(
                price_period=period,
                price_interval=interval,
                ma_windows=ma_windows
            )

        fig, ax = plt.subplots()
        ax.plot(df.index, df['Close'], label='Close')
        for w in ma_windows:
            col = f'MA{w}'
            if col in df.columns:
                ax.plot(df.index, df[col], label=col)
        ax.set_title(f"{self.symbol}: Close & MA({','.join(map(str, ma_windows))})")
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.legend(fontsize=7)
        fig.tight_layout()
        return fig

    def plot_eps_pe_to_fig(self,
                           eps: float = None,
                           pe: float = None,
                           n_quarters: int = 4,
                           period: str = "1d",
                           interval: str = "1d") -> plt.Figure:
        """
        Returns a Matplotlib Figure with a bar chart comparing:
          - EPS (TTM)
          - P/E Ratio
        If `eps` or `pe` is None, computes using analyzer.
        """
        # compute if not provided
        if eps is None:
            eps = self.analyzer.get_eps(n_quarters=n_quarters)
        if pe is None:
            pe = self.analyzer.get_pe_ratio(
                price_period=period,
                price_interval=interval,
                n_quarters=n_quarters
            )

        fig, ax = plt.subplots()
        ax.bar(['EPS (TTM)', 'P/E Ratio'], [eps, pe])
        ax.set_title(f"{self.symbol}: EPS (TTM) vs. P/E Ratio")
        ax.set_ylabel('Value')
        fig.tight_layout()
        return fig

    def plot_oil_price(self,
                       df: pd.DataFrame,
                       period: str = "1y",
                       interval: str = "1d",):

        fig, ax = plt.subplots()
        ax.plot(df.index, df["Close"], label="WTI Crude Oil")
        ax.set_title(f"WTI Crude Oil Price ({period})")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price (USD)")
        ax.legend()
        fig.tight_layout()
        return fig
