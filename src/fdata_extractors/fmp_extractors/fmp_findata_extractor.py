from src.config.config import FMP_API_KEY, ECC_COLLECTION
from src.fdata_extractors.decorator import apply_selection, apply_selection_growth
from src.fdata_extractors.findata_validator import FinDataValidator
import pandas as pd
import requests

class FMPAnalyzer(FinDataValidator):
    BASE_URL = "https://financialmodelingprep.com/stable/revenue-product-segmentation"

    def __init__(self, ticker: str):
        self.api_key = FMP_API_KEY
        self.ticker = ticker

    def get_product_data(self, n_years: int=None, n_quarters: int=None):
        def _convert_df_format(records):
            # Flatten data into a DataFrame
            rows = []
            for entry in records:
                fiscal_year = entry['fiscalYear']
                for product, revenue in entry['data'].items():
                    rows.append({
                        "fiscalYear": fiscal_year,
                        "product": product,
                        "revenue": revenue
                    })

            df = pd.DataFrame(rows)

            # Pivot to get fiscalYear as index, products as columns
            pivot_df = df.pivot(index='fiscalYear', columns='product', values='revenue').sort_index()

            return pivot_df
        if n_years is not None:
            url = f"{self.BASE_URL}?symbol={self.ticker}&period=annual"
        elif n_quarters is not None:
            url = f"{self.BASE_URL}?symbol={self.ticker}&period=quarter"
        else:
            return pd.DataFrame()

        params = {
            "apikey": self.api_key
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        response = response.json()[:n_years+1]
        df = _convert_df_format(response)
        return df.sort_index()

    @apply_selection
    def get_product_segment_revenue(self, n_years: int=None, n_quarters: int=None):
        return self.get_product_data(n_years=n_years, n_quarters=n_quarters)

    @apply_selection_growth
    def get_product_segment_revenue_growth(self, n_years: int=None, n_quarters: int=None):
        return self.get_product_data(n_years=n_years, n_quarters=n_quarters)

if __name__ == "__main__":
    fmp = FMPAnalyzer("AAPL")
    print(fmp.get_product_segment_revenue(n_years=3))
    print(fmp.get_product_segment_revenue_growth(n_years=3))
    print(fmp.get_product_segment_revenue_growth_test(n_years=3))

