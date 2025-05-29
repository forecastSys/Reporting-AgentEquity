from abc import ABC, abstractmethod
import pandas as pd

class FDataAbc(ABC):

    @abstractmethod
    def get_price(self, period: str = "1mo", interval: str = "1d") -> pd.Series:
        pass

    @abstractmethod
    def get_eps(self, n_quarters: int = 4) -> float:
        pass
    def get_pe_ratio(self, price_period: str = "1d", price_interval: str = "1d", n_quarters: int = 4) -> float:
        pass
    @abstractmethod
    def get_income_statement(self, n_quarters: int = 4) -> pd.DataFrame:
        pass
    @abstractmethod
    def get_total_revenue(self, n_quarters: int = 4) -> pd.Series:
        pass
    @abstractmethod
    def get_gross_profit(self, n_quarters: int = 4) -> pd.Series:
        pass
    @abstractmethod
    def get_ebitda(self, n_quarters: int = 4) -> pd.Series:
        pass
    @abstractmethod
    def get_ma15(self, period: str = "6mo", interval: str = "1d") -> pd.Series:
        pass
    @abstractmethod
    def get_ma30(self, period: str = "6mo", interval: str = "1d") -> pd.Series:
        pass
    @abstractmethod
    def get_ma60(self, period: str = "6mo", interval: str = "1d") -> pd.Series:
        pass
    @abstractmethod
    def get_ma90(self, period: str = "6mo", interval: str = "1d") -> pd.Series:
        pass
    @abstractmethod
    def get_ma180(self, period: str = "1y", interval: str = "1d") -> pd.Series:
        pass
    @abstractmethod
    def get_all_mas(self,
                    price_period: str = "1y",
                    price_interval: str = "1d",
                    ma_windows: list[int] = [15, 30, 60, 90, 120]
                    ) -> pd.DataFrame:
        pass
    @abstractmethod
    def get_sp500(self, period: str = "1mo", interval: str = "1d") -> pd.Series:
        pass
    @abstractmethod
    def get_beta(self, period: str = "6mo", interval: str = "1d") -> float:
        pass
    @abstractmethod
    def get_past_fiscal_year_end_shares(self, period: str = "5y") -> pd.DataFrame:
        pass
    @abstractmethod
    def get_past_fiscal_year_end_stock_price(self,
                                             period_end_month: int,
                                             period_end_day: int,
                                             period: str = "5y") -> pd.DataFrame:
        pass
    @abstractmethod
    def get_past_financial(self) -> pd.DataFrame:
        pass
    @abstractmethod
    def get_past_balance_sheet(self) -> pd.DataFrame:
        pass