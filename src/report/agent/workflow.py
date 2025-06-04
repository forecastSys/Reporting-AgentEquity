from dataclasses import field

from langchain_community.agent_toolkits import SteamToolkit
from langchain_community.utilities.clickup import Member

from src.config import (
    OPENAI_API_KEY,
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_PRIVATE_KEY,
    LANGFUSE_HOST
)
from src.report.agent import (
    State,
    SUP_HUB,
    BSOTeam,
    FVPDTeam,
    RUTeam,
    ReportTeamBase
)

from src.report.llm import OPENAI_CALLER
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

from typing import List, Optional, Literal, Annotated
from typing_extensions import TypedDict
from langchain_core.language_models.chat_models import BaseChatModel

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langchain_core.messages import HumanMessage, trim_messages
from langfuse.callback import CallbackHandler

from PIL import Image as PILImage
import io
from IPython.display import Image, display

class AgentWorkflow:

    def __init__(self,
                 ticker,
                 year,
                 quarter):
        self.ticker = ticker
        self.year = year
        self.quarter = quarter

        self.openai_llm = OPENAI_CALLER()._get_llm(model='gpt-4.1')
        self.langfuse_handler = CallbackHandler(secret_key=LANGFUSE_PRIVATE_KEY,
                                                public_key=LANGFUSE_PUBLIC_KEY,
                                                host=LANGFUSE_HOST
                                                )

        ## Define Agent Teams
        self.bso_team = BSOTeam(ticker=ticker, year=year, quarter=quarter)
        self.fvpd_team = FVPDTeam(ticker=ticker, year=year, quarter=quarter)
        self.ru_team = RUTeam(ticker=ticker, year=year, quarter=quarter)
        self.company = [self.bso_team, self.fvpd_team, self.ru_team]

    def create_team(self, builder: StateGraph, team: ReportTeamBase):

        builder.add_node(team.TEAM_SUPERVISOR_NAME, team.team_supervisor_node)
        builder.add_node(team.ASSISTANT_NAME, team.writer_node)
        builder.add_node(team.EVALUATOR_NAME, team.evaluator_node)
        builder.add_edge(START, team.TEAM_SUPERVISOR_NAME)
        return builder

    def run(self):

        company_builder = StateGraph(State)
        for team in self.company:
            company_builder = self.create_team(company_builder, team)
        company_graph = company_builder.compile(cache=None)

        ## Drawing Images
        buf = company_graph.get_graph().draw_mermaid_png()
        img = PILImage.open(io.BytesIO(buf))
        img.show()

        for s in company_graph.stream(
                {"messages": [("user", f"Please write me an Investment report for {self.ticker} for year {self.year}")]},
                config={"recursion_limit": 100, "callbacks": [self.langfuse_handler]}
        ):
            print(s)
            print("---")


if __name__ == '__main__':
    agent = AgentWorkflow('AAPL', 2025, 1)
    agent.run()
