from src.fdata_extractors import (
    FMPTranscriptFetcher,
    FMPAnalyzer,
    SecFilingExtractor,
    YFinanceAnalyzer,
    MySQLExtractor
)

from typing import Dict, List, Tuple, Literal, Union, Callable
import pandas as pd
from langchain_core.tools import tool
from langchain_core.runnables import Runnable
from langchain_core.tools.base import ArgsSchema, BaseTool
from pathlib import Path
import json
import random
import asyncio

class ToolsHelper:

    P = Path(__file__).resolve()
    PROJECT_DIR = P.parents[3]
    FDATA_DIR = PROJECT_DIR / 'data' / 'fdata'

    BS_VARIABLES = ['current_liabilities', 'current_assets', 'cash_and_cash_equivalents', 'accounts_receivable'] # balance sheet
    CF_VARIABLES = ['free_cash_flow'] # cash flow
    IS_VARIABLES = ['total_revenue', 'ebitda'] # income statement
    IS_VARIABLES = None # None means all the variables

    N_QUARTERS = 4 ## How many past quarter data to extract?
    N_YEARS = 3 ## How many past year data to extract?

    def __init__(self,
                 ticker: str,
                 year: int,
                 quarter: int):

        self.ticker = ticker
        self.year = year
        self.quarter = quarter

        yfinance = YFinanceAnalyzer(self.ticker)
        fmp_findata = FMPAnalyzer(self.ticker)
        sql = MySQLExtractor(self.ticker)

        self.fmp_extractors = FMPTranscriptFetcher()
        # # latest_filing = SecFilingExtractor().fetch(ticker=ticker)

        ## FMP / DB - ECC Data
        # ecc_content = self.fmp_extractors.fetch(ticker=self.ticker, year=self.year, quarter=self.quarter)['content']
        self.ecc_content = self.fmp_extractors.fetch_from_db(ticker=self.ticker, year=self.year, quarter=self.quarter)['content']

        ## FMP - Financial Data
        try:
            self.fmp_past_y_product_segment_rev = fmp_findata.get_product_segment_revenue(n_years=self.N_YEARS)
            self.fmp_past_y_product_segment_rev_growth = fmp_findata.get_product_segment_revenue_growth(n_years=self.N_YEARS)
        except:
            self.fmp_past_y_product_segment_rev = pd.DataFrame()
            self.fmp_past_y_product_segment_rev_growth = pd.DataFrame()

        ## SEC FILING - Items
        try:
            file_path = self.FDATA_DIR / f'10K_Items_{self.ticker}.json'
            with open(file_path, 'r', encoding='cp1252') as f:
                latest_filing = json.load(f)
        except FileNotFoundError:
            latest_filing = SecFilingExtractor().fetch(ticker=ticker)

        self.latest_filing_item1 = latest_filing['item1']
        self.latest_filing_item1a = latest_filing['item1a']
        self.latest_filing_item7 = latest_filing['item7']

        ## Yfinance - Financial Data
        self.yfinance_stock_price = yfinance.get_price(period='1y')
        self.yfinance_info = yfinance.info

        self.yfinance_past_q_bs = yfinance.get_past_balance_sheet(n_quarters=self.N_QUARTERS, selected_columns=self.BS_VARIABLES)
        self.yfinance_past_q_is = yfinance.get_past_income_statement(n_quarters=self.N_QUARTERS, selected_columns=self.IS_VARIABLES)
        self.yfinance_past_q_cf = yfinance.get_past_cash_flow(n_quarters=self.N_QUARTERS, selected_columns=self.CF_VARIABLES)
        self.yfinance_past_q_bs_growth = yfinance.get_past_balance_sheet_growth(n_quarters=self.N_QUARTERS, selected_columns=self.BS_VARIABLES)
        self.yfinance_past_q_is_growth = yfinance.get_past_income_statement_growth(n_quarters=self.N_QUARTERS, selected_columns=self.IS_VARIABLES)
        self.yfinance_past_q_cf_growth = yfinance.get_past_cash_flow_growth(n_quarters=self.N_QUARTERS, selected_columns=self.CF_VARIABLES)

        ## Local SQL - Competitor data
        self.competitors = sql._get_competitors(competitors_limit=3)

    @staticmethod
    def _apply_round(value: Literal[float, None]) -> Literal[float, None]:
        if value is None:
            return None
        return round(value, 2)

    @staticmethod
    def _create_dict(df: pd.DataFrame, key: str, orient: str = 'dict'):
        output = {}
        if isinstance(df, pd.DataFrame):
            output[key] = df.to_dict(orient=orient)
        elif isinstance(df, pd.Series):
            output[key] = df.to_dict()
        return output

    ## ESTIMATED PRICE
    def _get_estimate_price(self) -> Dict[str, float]:
        """Get estimated stock prices for the ticker for the next financial quarter."""
        last_cloing_price = self.yfinance_stock_price.iloc[-1]
        estimate_price = last_cloing_price * random.uniform(0.8, 1.5)
        # df.index = pd.DatetimeIndex(df.index.date).astype(str)
        return estimate_price

    ## FMP ECC
    def _get_latest_ecc(self) -> str:
        """Get latest earning conference call transcripts for the ticker."""
        # ecc_content = self.fmp_extractors.fetch(ticker=self.ticker, year=self.year, quarter=self.quarter)['content']
        # ecc_content = self.fmp.fetch_from_db(ticker=self.ticker, year=self.year, quarter=self.quarter)['content']
        return self.ecc_content

    ## SEC FILING
    def _get_latest_filing_item1(self) -> str:
        """Get latest sec filing 10K item1 for the ticker. item1 is about Business Description"""
        return self.latest_filing_item1

    def _get_latest_filing_item1a(self) -> str:
        """Get latest sec filing 10K item1a for the ticker. item1a is about Risk Factors"""
        return self.latest_filing_item1a

    def _get_latest_filing_item7(self) -> str:
        """Get latest sec filing 10K item7 for the ticker. item7 is about Management’s Discussion and Analysis (MD&A)"""
        return self.latest_filing_item7


    ## FMP Findata
    def _get_yearly_product_segment_growth(self) -> Dict[str, float]:
        '''Get past yearly product segment growth for the ticker.'''
        try:
            output = self._create_dict(self.fmp_past_y_product_segment_rev_growth, 'product_segment_revenue_growth')
        except:
            return {}
        return output

    def _get_main_products(self) -> Dict[str, float]:
        """Get the selling main product for the ticker."""
        modified_output = {}
        try:
            output = self._create_dict(self.fmp_past_y_product_segment_rev, 'product_segment_revenue')
            modified_output['main_products'] = list(output['product_segment_revenue'].keys())
        except:
            return {}
        return modified_output

    ## Yfinance Findata
    def _get_yfinance_stock_price(self) -> Dict[str, float]:
        """Get closing stock prices for the ticker."""
        output = self._create_dict(self.yfinance_stock_price, 'Stock Price')
        return output

    def _get_quarterly_current_ratio(self) -> Dict[str, float]:
        """Get past quarterly current ratio for the ticker."""
        current_assets = self.yfinance_past_q_bs['current_assets']
        current_liabilities = self.yfinance_past_q_bs['current_liabilities']
        current_ratio = current_assets / current_liabilities
        output = self._create_dict(current_ratio, 'current_ratio')
        return output

    def _get_quarterly_quick_ratio(self) -> Dict[str, float]:
        """Get past quarterly quick ratio for the ticker."""
        cash = self.yfinance_past_q_bs['cash_and_cash_equivalents']
        receivables = self.yfinance_past_q_bs['accounts_receivable']
        current_liabilities = self.yfinance_past_q_bs['current_liabilities']
        quick_ratio = (cash + receivables) / current_liabilities
        output = self._create_dict(quick_ratio, 'quick_ratio')
        return output

    def _get_quarterly_cash_ratio(self) -> Dict[str, float]:
        """Get past quarterly cash ratio for the ticker."""
        cash = self.yfinance_past_q_bs['cash_and_cash_equivalents']
        current_liabilities = self.yfinance_past_q_bs['current_liabilities']
        cash_ratio = cash / current_liabilities
        output = self._create_dict(cash_ratio, 'cash_ratio')
        return output

    def _get_quarterly_total_revenue(self) -> Dict[str, float]:
        """Get past quarterly total revenue for the ticker."""
        total_revenue = self.yfinance_past_q_is['total_revenue']
        output = self._create_dict(total_revenue, 'total_revenue')
        return output

    def _get_quarterly_total_revenue_growth(self) -> Dict[str, float]:
        """Get past quarterly total revenue growth for the ticker."""
        total_revenue_growth = self.yfinance_past_q_is_growth['total_revenue_growth']
        output = self._create_dict(total_revenue_growth, 'total_revenue_growth')
        return output

    def _get_quarterly_ebitda(self) -> Dict[str, float]:
        """Get past quarterly ebitda for the ticker."""
        ebitda = self.yfinance_past_q_is['ebitda']
        output = self._create_dict(ebitda, 'ebitda')
        return output

    def _get_quarterly_ebitda_growth(self) -> Dict[str, float]:
        """Get past quarterly ebitda growth for the ticker."""
        ebitda = self.yfinance_past_q_is['ebitda_growth']
        output = self._create_dict(ebitda, 'ebitda_growth')
        return output

    def _get_estimate_pe(self) -> float:
        """Get Estimated PE = estimate price / EPS for the ticker."""
        pe = self._get_estimate_price() / self.yfinance_info['trailingEps']
        return pe

    ## Local MySQL
    def _get_competitors_info(self):
        """Get competitors info for the ticker."""
        output = self._create_dict(self.competitors[['competitor_name', 'competitor_ticker', 'competed_product']],
                                   'competitors_info', orient='records')
        return output

if __name__ == '__main__':

    helper = ToolsHelper('AAPL', 2025, 1)


    async def main():
        # sync methods can still be called directly
        print(helper._get_estimate_price())
        print(helper._get_yearly_product_segment_growth())
        print(helper._get_quarterly_ebitda())
        print(helper._get_quarterly_cash_ratio())
        print(helper._get_quarterly_quick_ratio())
        print(helper._get_quarterly_total_revenue())
        print(helper._get_quarterly_total_revenue_growth())

        # async methods *must* be awaited
        competitors_info = await helper._get_competitors_info()
        print(competitors_info)
        import time
        start = time.perf_counter()
        comp_and_data = await helper._get_comp_and_competitors_data()
        end = time.perf_counter()
        print(f"Elapsed: {end - start:.6f} s")
        print(comp_and_data)
    asyncio.run(main())