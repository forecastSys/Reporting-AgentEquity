from src.config import OPENAI_API_KEY, MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_PORT
from src.database import MySQLHandler
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import SystemMessage, HumanMessage
from langchain_core.output_parsers.json import JsonOutputParser
from sqlalchemy import create_engine, text
import pandas as pd
import os
from tqdm import tqdm

def read_comp_list():
    sql = MySQLHandler()
    engine = sql._get_engine()
    df = pd.read_sql('ent_company_info', engine)
    df = df[df.apply(lambda x: 'JP' not in x.Ticker.split(' ')[1], axis=1)]
    df.Ticker = df.Ticker.apply(lambda x: x.split(' ')[0])
    df = df[['Ticker', 'Company_name', 'BICS_LEVEL_1']]
    return df


def get_direct_competitor_info(
    company_name: str,
    ticker: str,
    company_pool: Dict[str, str] = None,
    max_retries: int = 3
) -> Optional[List[dict]]:
    # for attempt in range(1, max_retries + 1):
    # run the chain, passing in variables
    result = chain.invoke({'company_name':company_name,
                           'ticker':ticker})
    # parser.parse will validate & convert the JSON string to Python objects
    return result
    # print(f"Failed after {max_retries} attempts.")
    # return None

def main():
    df_comp = read_comp_list()
    output_df_list = []
    for ind_code, groups in df_comp.groupby('BICS_LEVEL_1'):
        groups_list = groups[['Ticker', 'Company_name']].to_dict(orient='records')
        df_competitor_list = []
        for j, comp in groups.iterrows():
            company_name = comp.Company_name
            ticker = comp.Ticker
            competitors = get_direct_competitor_info(company_name=company_name, ticker=ticker)
            for k in tqdm(range(len(competitors['competitor_name'])), desc=f'Generating competitor info for industry code: {ind_code}'):
                df_temp = pd.DataFrame(
                    {
                        'company_name': company_name,
                        'company_ticker': ticker,
                        'industry_code': ind_code,
                        'competitor_name': competitors['competitor_name'][k],
                        'competitor_ticker': competitors['ticker'][k],
                        'competed_product': ', '.join(competitors['products_compete_head_to_head'][k]),
                        'competitor_rank': competitors['rank'][k]},
                        index=[k])
                df_competitor_list.append(df_temp)
        df_combine_industry = pd.concat(df_competitor_list, ignore_index=True)
        output_df_list.append(df_combine_industry)
    df_combine = pd.concat(output_df_list, ignore_index=True)
    return df_combine

if __name__ == "__main__":
    class Competitor(BaseModel):
        competitor_name: List[str]
        ticker: List[str]
        products_compete_head_to_head: List[List[str]]
        rank: List[int]

    parser = JsonOutputParser(pydantic_object=Competitor)
    prompt_template = PromptTemplate(
        template=(
            "You are an expert in competitive analysis.\n\n"
            "Give me the direct competitors of {company_name} (Ticker: {ticker}) "
            "in terms of the same types of products/services, focusing on companies "
            "that compete head-to-head."
            "You should also give a rank of competitors if the companys have multiple, 1 is the biggest competitor etc.,"
            "For each competitor, output STRICT JSON matching the schema.\n\n"
            "{format_instructions}"
        ),
        input_variables=["company_name", "ticker"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    # "You must select competitors from this list: {company_pool}"
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
    chain = prompt_template | llm | parser
    # competitors = get_direct_competitor_info(company_name="APPLE INC", ticker="AAPL", industry_list=industry_list)

    # print(competitors)
    main()
