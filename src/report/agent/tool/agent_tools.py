"""
agent_tools.py
- step 1: log your tool under ToolHelper @ tool_utils.py
    Note:
    - Your tool shuold be as general as possible, the assumption is each tool must contain ONLY one information.
    - For example, calling quick ratio, the tool should only return quick ratio
- step 2: register your tool under AgentTool
    - Here is you can register your tool as Langchain BaseTool.
- step 3: use your tools @ src.report.agent.hub.agent_hub_config.py
"""
from src.report.agent.tool import ToolsHelper

from typing import Dict, List, Tuple, Literal, Union, Callable
import pandas as pd
from langchain_core.tools import tool
from langchain_core.runnables import Runnable
from langchain_core.tools.base import ArgsSchema, BaseTool

class AgentTools(ToolsHelper):

    def __init__(self,
                 ticker: str,
                 year: int,
                 quarter: int):

        super().__init__(ticker=ticker, year=year, quarter=quarter)
        ## Wrapping Tools
        ## ---------------------------------------------------- EST. DATA ------------------------------------------------- ##
        self.get_estimate_price = tool(
            name_or_callable='Estimate_Price',
            description='Estimate Price (predicted by in house model) for future quarter from the ticker',
        )(self._get_estimate_price)
        self.get_estimate_pe = tool(
            name_or_callable='Estimate_PE',
            description='[Estimated PE = Estimate_Price / EPS] for the ticker',
        )(self._get_estimate_pe)

        ## ---------------------------------------------------- FMP Tools ---------------------------------------------------- ##
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