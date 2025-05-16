import matplotlib.pyplot as plt
from src.fdata_extractors import YFinanceAnalyzer

class FinancialPlotter:
    """
    Generates financial charts for a given ticker:
      1) Close price + multiple moving averages in one plot
      2) EPS (TTM) vs. P/E ratio as a bar chart
    """
    def __init__(self, ticker: str):
        self.symbol   = ticker
        self.analyzer = YFinanceAnalyzer(ticker)

    def plot_moving_averages(self,
                             period: str = "1y",
                             interval: str = "1d",
                             ma_windows: list[int] = [15, 30, 60, 90]):
        """
        Fetches price history and plots:
          - Close price
          - MA15, MA30, MA60, MA90
        """
        # get DataFrame with Close and all MAs
        df = self.analyzer.get_all_mas(
            price_period=period,
            price_interval=interval,
            ma_windows=ma_windows
        )

        plt.figure()
        plt.plot(df.index, df["Close"], label="Close")
        for w in ma_windows:
            plt.plot(df.index, df[f"MA{w}"], label=f"MA{w}")
        plt.title(f"{self.symbol} Close & Moving Averages")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_eps_pe(self,
                    price_period: str = "1d",
                    price_interval: str = "1d",
                    n_quarters: int = 4):
        """
        Calculates:
          - EPS (TTM over n_quarters)
          - P/E ratio based on latest close
        Then plots them side by side.
        """
        eps = self.analyzer.get_eps(n_quarters=n_quarters)
        pe  = self.analyzer.get_pe_ratio(
            price_period=price_period,
            price_interval=price_interval,
            n_quarters=n_quarters
        )

        plt.figure()
        plt.bar(["EPS (TTM)", "P/E Ratio"], [eps, pe])
        plt.title(f"{self.symbol} EPS vs. P/E Ratio")
        plt.ylabel("Value")
        plt.tight_layout()
        plt.show()

# Example usage:
if __name__ == "__main__":
    fp = FinancialPlotter("AAPL")
    # 1) MA chart
    fp.plot_moving_averages()
    # 2) EPS vs P/E
    fp.plot_eps_pe()
