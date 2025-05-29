from sqlalchemy.dialects.postgresql.pg_catalog import quote_ident

from src.fdata_extractors import (
    FMPTranscriptFetcher,
    SecFilingExtractor,
    YFinanceAnalyzer
)

from typing import Dict, List, Tuple, Literal, Union, Callable
import pandas as pd
from langchain_core.tools import tool
from langchain_core.runnables import Runnable
from langchain_core.tools.base import ArgsSchema, BaseTool
from pathlib import Path
import json

class AgentToolsHelper:

    P = Path(__file__).resolve()
    PROJECT_DIR = P.parents[3]
    FDATA_DIR = PROJECT_DIR / 'data' / 'fdata'

    def __init__(self,
                 ticker: str,
                 year: int,
                 quarter: int):

        self.ticker = ticker
        self.year = year
        self.quarter = quarter

        self.yfinance = YFinanceAnalyzer(self.ticker)
        self.fmp = FMPTranscriptFetcher()
        # latest_filing = SecFilingExtractor().fetch(ticker=ticker)

        file_path = self.FDATA_DIR / '10K_Items_AAPL.json'
        with open(file_path, 'r', encoding='cp1252') as f:
            latest_filing = json.load(f)

        self.latest_filing_item1 = latest_filing['item1']
        self.latest_filing_item1a = latest_filing['item1a']
        self.latest_filing_item7 = latest_filing['item7']

    def _get_yfinance_stock_price(self) -> Dict[str, float]:
        """Get closing stock prices for the ticker."""
        df = self.yfinance.get_price()
        df.index = pd.DatetimeIndex(df.index.date).astype(str)
        return df.to_dict()

    def _get_latest_ecc(self) -> str:
        """Get latest earning conference call transcripts for the ticker."""
        return self.fmp.fetch(ticker=self.ticker, year=self.year, quarter=self.quarter)['content']

    def _get_latest_filing_item1(self) -> str:
        """Get latest sec filing 10K item1 for the ticker. item1 is about Business Description"""
        return self.latest_filing_item1

    def _get_latest_filing_item1a(self) -> str:
        """Get latest sec filing 10K item1a for the ticker. item1a is about Risk Factors"""
        return self.latest_filing_item1a

    def _get_latest_filing_item7(self) -> str:
        """Get latest sec filing 10K item7 for the ticker. item7 is about Management’s Discussion and Analysis (MD&A)"""
        return self.latest_filing_item7


class AgentTools(AgentToolsHelper):

    def __init__(self,
                 ticker: str,
                 year: int,
                 quarter: int):

        super().__init__(ticker=ticker, year=year, quarter=quarter)
        ## Wrapping Tools
        self.get_stock_price_tool = tool(
            name_or_callable='get_stock_price',
            description='Get closing stock prices for the ticker.'
        )(self._get_yfinance_stock_price)

        self.get_latest_ecc_tool = tool(
            name_or_callable='get_latest_ecc',
            description='Get latest earning conference call transcripts for the ticker.'
        )(self._get_latest_ecc)

        self.get_latest_filing_item1_tool = tool(
            name_or_callable='get_latest_filing_item1',
            description='Get Latest SEC Filing 10K item1 for the ticker. item1 is about Business Description'
        )(self._get_latest_filing_item1)

        self.get_latest_filing_item1a_tool = tool(
            name_or_callable='get_latest_filing_item1a',
            description='Get Latest SEC Filing 10K item1a for the ticker. item1a is about Risk Factors'
        )(self._get_latest_filing_item1a)

        self.get_latest_filing_item7_tool = tool(
            name_or_callable='get_latest_filing_item7',
            description='Get Latest SEC Filing 10K item7 for the ticker. item7 is about Management’s Discussion and Analysis (MD&A)'
        )(self._get_latest_filing_item7)

    def _get_tools(self) -> Dict[str,
                                 Literal[BaseTool, Callable[[Union[Callable, Runnable]], BaseTool]]]:

        dict_tools = {
            'Stock_Price_Movement': self.get_stock_price_tool,
            'Latest_Earning_Transcripts': self.get_latest_ecc_tool,
            'Latest_SEC_Filing_10K_item1': self.get_latest_filing_item1_tool,
            'Latest_SEC_Filing_10K_item1a': self.get_latest_filing_item1a_tool,
            'Latest_SEC_Filing_10K_item7': self.get_latest_filing_item7_tool
        }
        return dict_tools

if __name__ == '__main__':

    agenttools = AgentTools('AAPL', 2025, 1)
    agenttools._get_yfinance_stock_price()

