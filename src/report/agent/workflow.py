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
    FVPDTeam
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
        # super().__init__(ticker=ticker, year=year, quarter=quarter)
        self.ticker = ticker
        self.year = year
        self.quarter = quarter

        self.openai_llm = OPENAI_CALLER()._get_llm()
        self.langfuse_handler = CallbackHandler(secret_key=LANGFUSE_PRIVATE_KEY,
                                                public_key=LANGFUSE_PUBLIC_KEY,
                                                host=LANGFUSE_HOST
                                                )

        self.bso_team = BSOTeam(ticker=ticker, year=year, quarter=quarter)
        self.fvpd_team = FVPDTeam(ticker=ticker, year=year, quarter=quarter)

    def make_supervisor_node(self,
                             assistants: List[str],
                             team_desc: str,
                             TEAM_SUPERVISOR_NAME: str,
                             TEAM_NAME: str) -> str:

        ROUTE_TO = assistants + ["__end__"]
        options = ["FINISH"] + assistants
        class Router(TypedDict):
            """Worker to route to next. If no workers needed, route to FINISH."""
            next: Literal[*options]
            plan: str

        def supervisor_node(state: State) -> Command[Literal[*ROUTE_TO]]:

            system_prompt = team_desc.format(team_assistants=assistants)
            """An LLM-based router."""
            messages = [
                           {"role": "system", "content": system_prompt},
                       ] + state["messages"]
            response = self.openai_llm.with_structured_output(Router).invoke(messages)
            goto = response["next"]
            plan = response["plan"]
            if goto == "FINISH":
                goto = END

            return Command(goto=goto,
                           update={
                               "next": goto,
                               "messages": [HumanMessage(content=plan, name=TEAM_SUPERVISOR_NAME, team_name=TEAM_NAME)]
                           })

        return supervisor_node

    def create_bso_team(self, company_builder) -> StateGraph:

        team = self.bso_team
        team_desc = SUP_HUB['bso_team']['desc']
        assistants = [team.ASSISTANT_NAME]
        ed_node = self.make_supervisor_node(assistants=assistants,
                                            team_desc=team_desc,
                                            TEAM_SUPERVISOR_NAME=team.TEAM_SUPERVISOR_NAME,
                                            TEAM_NAME=team.TEAM_NAME)

        # bso_team_builder = StateGraph(State)
        company_builder.add_node(team.TEAM_SUPERVISOR_NAME, ed_node)
        # company_builder.add_node(team.SUPERVISOR_NAME, team.team_supervisor_node)
        company_builder.add_node(team.ASSISTANT_NAME, team.writer_node)
        company_builder.add_node(team.EVALUATOR_NAME, team.evaluator_node)

        company_builder.add_edge(START, team.TEAM_SUPERVISOR_NAME)
        # company_builder.add_edge(team.EXECUTIVE_DIRECTOR_NAME, team.ASSISTANT_NAME)
        # company_builder.add_edge(team.ASSISTANT_NAME, team.EVALUATOR_NAME)
        # company_builder.add_edge(team.EVALUATOR_NAME, team.ASSISTANT_NAME)
        # company_builder.add_edge(team.ASSISTANT_NAME, team.EXECUTIVE_DIRECTOR_NAME)
        # company_builder.add_edge(team.EXECUTIVE_DIRECTOR_NAME, END)
        # company_builder.add_edge(team.SUPERVISOR_NAME, self.EXECUTIVE_DIRECTOR_NAME)
        # bso_team_graph = bso_team_builder.compile().with_config({"callbacks": [self.langfuse_handler]})

        return company_builder

    def create_fvpd_team(self, company_builder) -> StateGraph:

        team = self.fvpd_team
        team_desc = SUP_HUB['fvpd_team']['desc']
        assistants = [team.ASSISTANT_NAME]
        ed_node = self.make_supervisor_node(assistants=assistants,
                                            team_desc=team_desc,
                                            TEAM_SUPERVISOR_NAME=team.TEAM_SUPERVISOR_NAME,
                                            TEAM_NAME=team.TEAM_NAME)
        # company_builder.add_node(team.ASSISTANT_NAME, team.writer_node)
        # company_builder.add_node(team.EVALUATOR_NAME, team.evaluator_node)
        company_builder.add_node(team.TEAM_SUPERVISOR_NAME, ed_node)
        company_builder.add_node(team.ASSISTANT_NAME, team.writer_node)
        company_builder.add_node(team.EVALUATOR_NAME, team.evaluator_node)

        company_builder.add_edge(START, team.TEAM_SUPERVISOR_NAME)
        # company_builder.add_edge(team.EXECUTIVE_DIRECTOR_NAME, team.ASSISTANT_NAME)
        # company_builder.add_edge(team.ASSISTANT_NAME, team.EVALUATOR_NAME)
        # company_builder.add_edge(team.EVALUATOR_NAME, team.ASSISTANT_NAME)
        # company_builder.add_edge(team.ASSISTANT_NAME, team.EXECUTIVE_DIRECTOR_NAME)
        # company_builder.add_edge(team.EXECUTIVE_DIRECTOR_NAME, END)
        # company_builder.add_edge(team.SUPERVISOR_NAME, self.EXECUTIVE_DIRECTOR_NAME)
        # bso_team_graph = bso_team_builder.compile().with_config({"callbacks": [self.langfuse_handler]})

        return company_builder

    # def call_bso_team(self, state: State) -> Command[Literal[EXECUTIVE_DIRECTOR_NAME]]:
    #     team_graph = self.create_bso_team()
    #     response = team_graph.invoke({"messages": state["messages"][-1]})
    #
    #     return Command(
    #         update={
    #             "messages": [
    #                 HumanMessage(
    #                     content=response["messages"][-1].content, name=team.TEAM_NAME
    #                 )
    #             ]
    #         },
    #         goto=self.EXECUTIVE_DIRECTOR_NAME,
    #     )
    # def call_fvpd_team(self, state: State) -> Command[Literal[EXECUTIVE_DIRECTOR_NAME]]:
    #     team_graph = self.create_fvpd_team()
    #     response = team_graph.invoke({"messages": state["messages"][-1]})
    #
    #     return Command(
    #         update={
    #             "messages": [
    #                 HumanMessage(
    #                     content=response["messages"][-1].content, name=team.TEAM_NAME
    #                 )
    #             ]
    #         },
    #         goto=self.EXECUTIVE_DIRECTOR_NAME,
    #     )

    def run(self):

        # assistant_teams = [team.ASSISTANT_NAME, team.ASSISTANT_NAME]
        # company_supervisor_node = self.make_supervisor_node(assistants=assistant_teams)

        company_builder = StateGraph(State)
        # company_builder.add_node(self.EXECUTIVE_DIRECTOR_NAME, company_supervisor_node)
        # company_builder.add_edge(START, self.EXECUTIVE_DIRECTOR_NAME)
        company_builder = self.create_bso_team(company_builder)
        company_builder = self.create_fvpd_team(company_builder)
        company_graph = company_builder.compile(cache=None)



        # super_builder.add_node(team.TEAM_NAME, self.call_bso_team)
        # super_builder.add_node(team.TEAM_NAME, self.call_fvpd_team)

        # super_builder.add_edge(START, self.EXECUTIVE_DIRECTOR_NAME)
        # super_graph = super_builder.compile()


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
