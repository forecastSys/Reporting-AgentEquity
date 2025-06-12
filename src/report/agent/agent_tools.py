"""
agent_tools.py
- step 1: log your tool under AgentToolHelper
    Note:
    - Your tool shuold be as general as possible, the assumption is each tool must contain ONLY one information.
    - For example, calling quick ratio, the tool should only return quick ratio
- step 2: register your tool under AgentTool
    - Here is you can register your tool as Langchain BaseTool.
- step 3: use your tools in src.report.agent.hub.agent_hub_config.py
"""

from sqlalchemy.dialects.postgresql.pg_catalog import quote_ident

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

class AgentToolsHelper:

    P = Path(__file__).resolve()
    PROJECT_DIR = P.parents[3]
    FDATA_DIR = PROJECT_DIR / 'data' / 'fdata'

    BS_VARIABLES = ['current_liabilities', 'current_assets', 'cash_and_cash_equivalents', 'accounts_receivable'] # balance sheet
    CF_VARIABLES = ['free_cash_flow'] # cash flow
    IS_VARIABLES = ['total_revenue', 'ebitda'] # income statement

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
        self.yfinance_stock_price = yfinance.get_price()

        self.yfinance_past_q_bs = yfinance.get_past_balance_sheet(n_quarters=self.N_QUARTERS, selected_columns=self.BS_VARIABLES)
        self.yfinance_past_q_is = yfinance.get_past_income_statement(n_quarters=self.N_QUARTERS, selected_columns=self.IS_VARIABLES)
        self.yfinance_past_q_cf = yfinance.get_past_cash_flow(n_quarters=self.N_QUARTERS, selected_columns=self.CF_VARIABLES)
        self.yfinance_past_q_bs_growth = yfinance.get_past_balance_sheet_growth(n_quarters=self.N_QUARTERS, selected_columns=self.BS_VARIABLES)
        self.yfinance_past_q_is_growth = yfinance.get_past_income_statement_growth(n_quarters=self.N_QUARTERS, selected_columns=self.IS_VARIABLES)
        self.yfinance_past_q_cf_growth = yfinance.get_past_cash_flow_growth(n_quarters=self.N_QUARTERS, selected_columns=self.CF_VARIABLES)

        ## Local SQL - Competitor data
        self.competitors = sql._get_competitors(competitors_limit=3)


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

    def _get_quarterly_current_ratio(self) -> pd.DataFrame:
        """Get past quarterly current ratio for the ticker."""
        current_assets = self.yfinance_past_q_bs['current_assets']
        current_liabilities = self.yfinance_past_q_bs['current_liabilities']
        current_ratio = current_assets / current_liabilities
        output = self._create_dict(current_ratio, 'current_ratio')
        return output

    def _get_quarterly_quick_ratio(self) -> pd.DataFrame:
        """Get past quarterly quick ratio for the ticker."""
        cash = self.yfinance_past_q_bs['cash_and_cash_equivalents']
        receivables = self.yfinance_past_q_bs['accounts_receivable']
        current_liabilities = self.yfinance_past_q_bs['current_liabilities']
        quick_ratio = (cash + receivables) / current_liabilities
        output = self._create_dict(quick_ratio, 'quick_ratio')
        return output

    def _get_quarterly_cash_ratio(self) -> pd.DataFrame:
        """Get past quarterly cash ratio for the ticker."""
        cash = self.yfinance_past_q_bs['cash_and_cash_equivalents']
        current_liabilities = self.yfinance_past_q_bs['current_liabilities']
        cash_ratio = cash / current_liabilities
        output = self._create_dict(cash_ratio, 'cash_ratio')
        return output

    def _get_quarterly_total_revenue(self) -> pd.DataFrame:
        """Get past quarterly total revenue for the ticker."""
        total_revenue = self.yfinance_past_q_is['total_revenue']
        output = self._create_dict(total_revenue, 'total_revenue')
        return output

    def _get_quarterly_total_revenue_growth(self) -> pd.DataFrame:
        """Get past quarterly total revenue growth for the ticker."""
        total_revenue_growth = self.yfinance_past_q_is_growth['total_revenue_growth']
        output = self._create_dict(total_revenue_growth, 'total_revenue_growth')
        return output

    def _get_quarterly_ebitda(self) -> pd.DataFrame:
        """Get past quarterly ebitda for the ticker."""
        ebitda = self.yfinance_past_q_is['ebitda']
        output = self._create_dict(ebitda, 'ebitda')
        return output

    def _get_quarterly_ebitda_growth(self) -> pd.DataFrame:
        """Get past quarterly ebitda growth for the ticker."""
        ebitda = self.yfinance_past_q_is['ebitda_growth']
        output = self._create_dict(ebitda, 'ebitda_growth')
        return output

    ## Local MySQL
    def _get_competitors_info(self):
        """Get competitors info for the ticker."""
        output = self._create_dict(self.competitors[['competitor_name', 'competitor_ticker', 'competed_product']],
                                   'competitors_info', orient='records')
        return output



class AgentTools(AgentToolsHelper):

    def __init__(self,
                 ticker: str,
                 year: int,
                 quarter: int):

        super().__init__(ticker=ticker, year=year, quarter=quarter)
        ## Wrapping Tools
        ## ---------------------------------------------------- FMP Tools---------------------------------------------------- ##
        ## ECC
        self.get_latest_ecc_tool = tool(
            name_or_callable='Latest_Earning_Transcripts',
            description='Get latest earning conference call transcripts for the ticker.'
        )(self._get_latest_ecc)

        ## Main Product
        self.get_main_products_tool = tool(
            name_or_callable='Main_Products',
            description='Get main selling products for the ticker.'
        )(self._get_main_products)

        ## Product Segment Growth
        self.get_yearly_product_segment_growth = tool(
            name_or_callable='Yearly_Product_Revenue_Growth',
            description='Get past year to year product revenue growth for the ticker.'
        )(self._get_yearly_product_segment_growth)

        ## ---------------------------------------------------- SEC Filing Tools ---------------------------------------------------- ##
        self.get_latest_filing_item1_tool = tool(
            name_or_callable='Latest_SEC_Filing_10K_item1',
            description='Get Latest SEC Filing 10K item1 for the ticker. item1 is about Business Description'
        )(self._get_latest_filing_item1)

        self.get_latest_filing_item1a_tool = tool(
            name_or_callable='Latest_SEC_Filing_10K_item1a',
            description='Get Latest SEC Filing 10K item1a for the ticker. item1a is about Risk Factors'
        )(self._get_latest_filing_item1a)

        self.get_latest_filing_item7_tool = tool(
            name_or_callable='Latest_SEC_Filing_10K_item7',
            description='Get Latest SEC Filing 10K item7 for the ticker. item7 is about Management’s Discussion and Analysis (MD&A)'
        )(self._get_latest_filing_item7)
        ## ---------------------------------------------------- Yfinance Tools ---------------------------------------------------- ##
        ## Stock Price
        self.get_stock_price_tool = tool(
            name_or_callable='Stock_Price_Movement',
            description='Get closing stock prices for the ticker.'
        )(self._get_yfinance_stock_price)

        ## Ratios
        self.get_quarterly_current_ratio_tool = tool(
            name_or_callable='Quarterly_Current_Ratio',
            description='Get past quarter to quarter current ratio for the ticker.'
        )(self._get_quarterly_current_ratio)
        self.get_quarterly_cash_ratio_tool = tool(
            name_or_callable='Quarterly_Cash_Ratio',
            description='Get past quarter to quarter cash ratio for the ticker.'
        )(self._get_quarterly_cash_ratio)
        self.get_quarterly_quick_ratio_tool = tool(
            name_or_callable='Quarterly_Quick_ratio',
            description='Get past quarter to quarter quick ratio for the ticker.'
        )(self._get_quarterly_quick_ratio)

        ## IS
        self.get_quarterly_total_revenue_tool = tool(
            name_or_callable='Quarterly_Total_revenue',
            description='Get past quarter to quarter total revenue for the ticker.'
        )(self._get_quarterly_total_revenue)
        self.get_quarterly_total_revenue_growth_tool = tool(
            name_or_callable='Quarterly_Total_Revenue_Growth',
            description='Get past quarter to quarter total revenue growth for the ticker.'
        )(self._get_quarterly_total_revenue_growth)

        self.get_quarterly_ebitda_tool = tool(
            name_or_callable='Quarterly_Ebitda',
            description='Get past quarter to quarter ebitda for the ticker.'
        )(self._get_quarterly_ebitda)
        self.get_quarterly_ebitda_growth_tool = tool(
            name_or_callable='Quarterly_Ebitda_Growth',
            description='Get past quarter to quarter ebitda growth for the ticker.'
        )(self._get_quarterly_ebitda_growth)
        ## ---------------------------------------------------- Local MYSQL Tools ---------------------------------------------------- ##
        self.get_competitors_info_tool = tool(
            name_or_callable='Competitors_Info',
            description="Get competitors infos, it contained the competitor's name and main product they competed with the ticker."
        )(self._get_competitors_info)

        ## register all tools
        self.all_tools = self._register_tools()

    def _register_tools(self) -> Dict[str, Literal[BaseTool, Callable[[Union[Callable, Runnable]], BaseTool]]]:
        """tools registration"""
        return {
            tool.name: tool
            for tool in vars(self).values()
            if isinstance(tool, BaseTool)
        }
    def _get_tools(self) -> Dict[str, Literal[BaseTool, Callable[[Union[Callable, Runnable]], BaseTool]]]:
        return self.all_tools

if __name__ == '__main__':

    agenttools = AgentTools('AAPL', 2025, 1)
    tools = agenttools._register_tools()
    count = 0
    for key, value in tools.items():
        print(f'{count}. {key}')
        count += 1

    agenttoolsHelp = AgentToolsHelper('AAPL', 2025, 1)
    print(agenttoolsHelp._get_competitors_info())
    print(agenttoolsHelp._get_estimate_price())
    print(agenttoolsHelp._get_yearly_product_segment_growth())
    print(agenttoolsHelp._get_quarterly_ebitda())
    print(agenttoolsHelp._get_quarterly_cash_ratio())
    print(agenttoolsHelp._get_quarterly_quick_ratio())
    print(agenttoolsHelp._get_quarterly_total_revenue())
    print(agenttoolsHelp._get_quarterly_total_revenue_growth())