from src.config import (
    OPENAI_API_KEY,
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_PRIVATE_KEY,
    LANGFUSE_HOST
)
from src.report.agent import (
    State,
    BSOTeam,
    FVPDTeam,
    RUTeam,
    CATeam,
    BDTeam,
    ReportTeamBase,
    AgentWorkflowUtils,
    HumanTools
)
from src.report.llm import OPENAI_CALLER
from langgraph.graph import StateGraph, MessagesState, START, END
from langfuse.callback import CallbackHandler
from PIL import Image as PILImage
import io
import json
import asyncio
import time

class AgentWorkflow(AgentWorkflowUtils):

    def __init__(self,
                 ticker,
                 year,
                 quarter):
        self.ticker = ticker
        self.year = year
        self.quarter = quarter

        self.openai_llm = OPENAI_CALLER()._get_llm(model='gpt-4o')
        self.langfuse_handler = CallbackHandler(secret_key=LANGFUSE_PRIVATE_KEY,
                                                public_key=LANGFUSE_PUBLIC_KEY,
                                                host=LANGFUSE_HOST
                                                )

        self.humantools = HumanTools(ticker, year, quarter)

        ## Define Agent Teams
        self.bso_team = BSOTeam(ticker=ticker, year=year, quarter=quarter)
        self.fvpd_team = FVPDTeam(ticker=ticker, year=year, quarter=quarter)
        self.ru_team = RUTeam(ticker=ticker, year=year, quarter=quarter)
        self.bd_team = BDTeam(ticker=ticker, year=year, quarter=quarter)
        self.ca_team = CATeam(ticker=ticker, year=year, quarter=quarter)
        self.company = [self.bso_team, self.fvpd_team, self.ru_team, self.bd_team, self.ca_team]


    def create_team(self, builder: StateGraph, team: ReportTeamBase):

        builder.add_node(team.TEAM_SUPERVISOR_NAME, team.team_supervisor_node)
        builder.add_node(team.ASSISTANT_NAME, team.writer_node)
        builder.add_node(team.EVALUATOR_NAME, team.evaluator_node)
        builder.add_edge(START, team.TEAM_SUPERVISOR_NAME)
        return builder

    def run(self):

        start = time.perf_counter()
        company_builder = StateGraph(State)
        for team in self.company:
            company_builder = self.create_team(company_builder, team)
        company_graph = company_builder.compile(cache=None)

        end = time.perf_counter()
        print(f"Elapsed: {end - start:.6f} s")

        ## Drawing Images
        buf = company_graph.get_graph().draw_mermaid_png()
        img = PILImage.open(io.BytesIO(buf))
        img.show()
        team_msg = []
        for s in company_graph.stream(
                {"messages": [("user", f"Please write me an Investment report for {self.ticker} for year {self.year}")]},
                config={"recursion_limit": 100, "callbacks": [self.langfuse_handler]}
        ):
            team_msg.append(s)
            print(s)
            print("---")

        grouped_messages = self._group_messages_by_team(team_msg)
        output_dict = {}
        for team in self.company:
            temp_dict = {}
            temp_dict["section"] = self._get_last_msg_for_team(team_msg_dict=grouped_messages, team_name=team.TEAM_NAME, team_member=team.ASSISTANT_NAME).content
            output_dict[team.TEAM_NAME] = temp_dict

        output_dict["comp_and_competitors_infos"] = asyncio.run(self.humantools.main())
        # with open("output.json", "w") as outfile:
        #     json.dump(output_dict, outfile)
        return output_dict



if __name__ == '__main__':
    start = time.perf_counter()
    agent = AgentWorkflow('NVDA', 2025, 1)
    agent.run()

    end = time.perf_counter()
    print(f"Elapsed: {end - start:.6f} s")