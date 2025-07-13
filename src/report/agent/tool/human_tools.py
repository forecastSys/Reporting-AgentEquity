from src.report.agent.tool import ToolsHelper
from src.fdata_extractors import (
    YFinanceAnalyzer
)
from typing import Dict, List, Tuple, Literal, Union, Callable
import random
import asyncio

class HumanTools(ToolsHelper):

    def __init__(self,
                 ticker: str,
                 year: int,
                 quarter: int):

        super().__init__(ticker=ticker, year=year, quarter=quarter)

    ## Local MySQL
    async def _get_competitors_info(self):
        """Get competitors info for the ticker."""
        output = self._create_dict(self.competitors[['competitor_name', 'competitor_ticker', 'competed_product']],
                                   'competitors_info',
                                   orient='records')
        return output

    async def _fetch_ticker_data(self, ticker: str) -> Dict:
        """
        Helper to fetch data for one ticker in a thread.
        """
        # run the blocking analytics in a thread
        if ticker != self.ticker:
            yfinance = await asyncio.to_thread(YFinanceAnalyzer, ticker)
            yfinance_c_info = await asyncio.to_thread(lambda: yfinance.info)
            yfinance_stock = await asyncio.to_thread(lambda: yfinance.ticker.history(period='1y').Close)
        else:
            yfinance_c_info = self.yfinance_info
            yfinance_stock = self.yfinance_stock_price

        pe = self._apply_round(yfinance_c_info.get('trailingPE', None))
        current_price = self._apply_round(yfinance_c_info.get('currentPrice', None))
        est_price = self._apply_round(current_price * random.uniform(0.8, 1.5))
        price_to_est_price = self._apply_round(current_price / est_price)
        price_to_book = self._apply_round(current_price / yfinance_c_info.get('bookValue', None))
        dividends_yield = self._apply_round(yfinance_c_info.get('dividendYield', None))
        mkt_cap = yfinance_c_info.get('marketCap', None)

        one_year_low = self._apply_round(yfinance_stock.min())
        one_year_high = self._apply_round(yfinance_stock.max())
        one_year_price_range = f"{one_year_low}-{one_year_high}"

        return {
            'ticker': ticker,
            'pe': pe,
            'current_price': current_price,
            'est_price': est_price,
            'price_to_est_price': price_to_est_price,
            'price_to_book': price_to_book,
            'dividends_yield': dividends_yield,
            'mkt_cap': mkt_cap,
            'one_year_price_range': one_year_price_range
        }

    async def _get_comp_and_competitors_data(self) -> Dict[str, Dict]:
        """Get competitors data for the ticker, asynchronously."""
        competitors = await self._get_competitors_info()
        tickers = [self.ticker] + [
            info['competitor_ticker']
            for info in competitors['competitors_info']
        ]

        # fire off all fetches in parallel
        fetch_tasks = [self._fetch_ticker_data(t) for t in tickers]
        results = await asyncio.gather(*fetch_tasks)

        # combine into dict by ticker
        combined_data = {r['ticker']: {k: v for k, v in r.items() if k != 'ticker'} for r in results}
        return combined_data

    async def main(self):
        comp_and_data = await self._get_comp_and_competitors_data()
        return comp_and_data

if __name__ == '__main__':

    helper = HumanTools('NVDA', 2025, 1)
    asyncio.run(helper.main())