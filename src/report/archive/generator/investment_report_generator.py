from src.report.prompts import (
    SUMMARY_SECTION_PROMPT,
    BUSINESS_SECTION_PROMPT,
    RISK_ASSESSMENT_SECTION_PROMPT,
)
from src.config import OPENAI_API_KEY
from src.fdata_extractors.fmp_extractors.fmp_ecc_extractor import FMPTranscriptFetcher
from src.fdata_extractors.sec_filing_extractor import fetch_sec_filings_text
from src.fdata_extractors.yfinance_extractors.yf_findata_extractor import YFinanceAnalyzer
from src.report.parser import ReportGenerated, SummaryGenerated
import datetime
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import pandas as pd

class InvestmentReportGenerator:
    def __init__(self):
        # Initialize the LLM (uses OPENAI_API_KEY env var by default)
        self.llm = ChatOpenAI(model_name='gpt-4o',temperature=0, openai_api_key=OPENAI_API_KEY)
        self.parser = JsonOutputParser(pydantic_object=ReportGenerated)
        self.summary_parser = JsonOutputParser(pydantic_object=SummaryGenerated)

        # Prompt templates
        self.summary_template = PromptTemplate(
            template=SUMMARY_SECTION_PROMPT,
            input_variables=[
                "company_name", "year", "quarter", "next_year", "ecc_transcripts",
                "fiscal_year", "item7", "today_date", "stock_price",
                "stock_price_ma_15", "stock_price_ma_30", "stock_price_ma_60", "stock_price_ma_90", "stock_price_ma_120",
                "eps", "total_revenues", "ebitda"
            ],
            partial_variables={"format_instructions": self.summary_parser.get_format_instructions()}
        )
        self.business_template = PromptTemplate(
            template=BUSINESS_SECTION_PROMPT,
            input_variables=["item1", "ecc_transcripts"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        self.risk_template = PromptTemplate(
            template=RISK_ASSESSMENT_SECTION_PROMPT,
            input_variables=["item1a"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

    def generate(self, ticker: str, year: int, quarter: int) -> dict:
        # Compute next year
        next_year = year + 1

        # 1. Fetch earnings call transcript
        ecc_fetcher = FMPTranscriptFetcher()
        ecc_data = ecc_fetcher.fetch(ticker, year, quarter)[0]
        ecc_text = ecc_data.get("content", ecc_data if isinstance(ecc_data, dict) else str(ecc_data))

        # 2. Fetch SEC 10-K sections
        sec_items = fetch_sec_filings_text(ticker, form_type="10-K")
        item1_text = sec_items.get("item1", "")
        item1a_text = sec_items.get("item1a", "")
        item7_text = sec_items.get("item7", "")

        # 3. Retrieve financial and market data
        yf = YFinanceAnalyzer(ticker)
        today = datetime.date.today().isoformat()
        # Latest close price
        stock_price = yf.get_price(period="1mo", interval="1d")
        stock_price = stock_price.reset_index()
        stock_price.Date = stock_price.Date.apply(lambda x: str(x.date()))
        stock_price_in_dict = stock_price.set_index('Date').to_dict()['Close']

        ## 3.2 Stock price MA
        stock_price_ma = yf.get_all_mas()  # assume index is a DatetimeIndex
        stock_price_ma = stock_price_ma.reset_index()  # bring the dates into a column
        stock_price_ma.rename(columns={'index': 'Date'}, inplace=True)

        # 2. Convert Date column to actual date objects
        stock_price_ma['Date'] = pd.to_datetime(stock_price_ma['Date']).dt.date

        # 3. Compute the cutoff (3 months ago from the latest date in your data)
        latest_date = stock_price_ma['Date'].max()
        three_months_ago = latest_date - pd.DateOffset(months=1)

        # 4. Filter to only the last 3 months
        ma_last_3m = stock_price_ma[stock_price_ma['Date'] >= three_months_ago.date()]

        # 5. Convert back to strings and to a dict
        ma_last_3m['Date'] = ma_last_3m['Date'].astype(str)
        stock_price_ma_in_dict = ma_last_3m.set_index('Date').to_dict()

        stock_price_ma_15 = stock_price_ma_in_dict['MA15']
        stock_price_ma_30 = stock_price_ma_in_dict['MA30']
        stock_price_ma_60 = stock_price_ma_in_dict['MA60']
        stock_price_ma_90 = stock_price_ma_in_dict['MA90']
        stock_price_ma_120 = stock_price_ma_in_dict['MA120']

        # 3.3 Income metrics
        eps = yf.get_eps(n_quarters=4)
        total_revenues = yf.get_total_revenue(n_quarters=4)
        total_revenues = total_revenues.reset_index()  # bring the dates into a column
        total_revenues.rename(columns={'index': 'Date'}, inplace=True)
        total_revenues.Date = total_revenues.Date.apply(lambda x: str(x.date()))
        total_revenues_dict = total_revenues.set_index('Date').to_dict()

        ebitda = yf.get_ebitda(n_quarters=4)
        ebitda = ebitda.reset_index()
        ebitda.rename(columns={'index': 'Date'}, inplace=True)
        ebitda.Date = ebitda.Date.apply(lambda x: str(x.date()))
        ebitda_dict = ebitda.set_index('Date').to_dict()

        # 4. Generate investment summary
        # summary_chain = LLMChain(llm=self.llm, prompt=self.summary_template)

        summary_chain = self.summary_template | self.llm | self.summary_parser

        summary = summary_chain.invoke({
            'company_name':ticker,
            'year':year,
            'quarter':quarter,
            'next_year':next_year,
            'ecc_transcripts':ecc_text,
            'fiscal_year':year,
            'item7':item7_text,
            'today_date':today,
            'stock_price':stock_price_in_dict,
            'stock_price_ma_15':stock_price_ma_15,
            'stock_price_ma_30':stock_price_ma_30,
            'stock_price_ma_60':stock_price_ma_60,
            'stock_price_ma_90':stock_price_ma_90,
            'stock_price_ma_120':stock_price_ma_120,
            'eps':eps,
            'total_revenues':total_revenues_dict,
            'ebitda':ebitda_dict
        }
        )

        # 5. Generate business overview
        business_chain = self.business_template | self.llm | self.parser
        business = business_chain.invoke({
            'item1': item1_text,
            'ecc_transcripts': ecc_text
        }
        )

        # 6. Generate risk assessment
        risk_chain = self.risk_template | self.llm | self.parser
        risk = risk_chain.invoke({
            'item1a': item1a_text,
        }
        )

        return {
            "investment_summary": summary,
            "business_overview": business,
            "risk_assessment": risk,
        }


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    ticker = "AAPL"
    year = 2025
    quarter = 1

    generator = InvestmentReportGenerator()
    report = generator.generate(ticker, year, quarter)

    print("\n=== Investment Summary ===\n", report["investment_summary"])
    print("\n=== Business Overview ===\n", report["business_overview"])
    print("\n=== Risk Assessment ===\n", report["risk_assessment"])