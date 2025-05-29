from http.client import responses

from src.abstractions import AgentTeamABC
from src.report.agent import (
    State,
    SUP_HUB,
    WOKER_HUB,
    EVALUATION_HUB
)
from src.report.agent import AgentTools
from src.report.llm import OPENAI_CALLER
from src.report.decorator import AgentDecorator

from typing import Dict, List, Tuple, Literal, Union, Callable
from typing_extensions import TypedDict

from langgraph.prebuilt import create_react_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, trim_messages, AIMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langchain_core.runnables import Runnable
from langchain_core.tools.base import ArgsSchema, BaseTool
from langfuse.callback import CallbackHandler
import functools


class ReportTeamBase(AgentTeamABC,
                     AgentTools):
    EXECUTIVE_DIRECTOR_NAME: str
    SECTION:                 str
    TEAM_NAME:               str
    SUPERVISOR_NAME:         str
    ASSISTANT_NAME:          str
    EVALUATOR_NAME:          str
    DATA_INPUT:              List[str]

    def __init__(self, ticker:str, year:str, quarter:str):
        super().__init__(ticker=ticker, year=year, quarter=quarter)

        self.openai_llm = OPENAI_CALLER()._get_llm()
        tools_list = self._get_tools()
        self.tools_used = [tools_list[i] for i in self.DATA_INPUT]

    def team_supervisor_node(self, state: State):
        ROUTE_TO = [self.ASSISTANT_NAME, self.EXECUTIVE_DIRECTOR_NAME]

        class Router(TypedDict):
            """Worker to route to next. If no workers needed, route to FINISH."""
            next: Literal[*ROUTE_TO]

        system_prompt = SUP_HUB['bso_team']['desc'].format(ed_name=self.EXECUTIVE_DIRECTOR_NAME,
                                                           assistant_name=self.ASSISTANT_NAME)
        messages = {
            'messages':[{"role": "system", "content": system_prompt}]
        }
        supervisor_agent = create_react_agent(
            self.openai_llm,
            response_format=Router,
            tools=[],
        )
        result = supervisor_agent.invoke(messages)
        next_node = result["structured_response"]["next"]

        return Command(
            goto=next_node,
            update={
                "messages": state["messages"],
                "next": next_node,
            }
        )

    def evaluator_node(self, state: State):
        ROUTE_TO = [self.ASSISTANT_NAME]

        class Router(TypedDict):
            """
            1. Worker to route to next.
            2. Provide feedback to your colleagues
            """
            next: Literal[*ROUTE_TO]
            feedback: str

        writer_msg = next(
            m for m in state["messages"]
            if isinstance(m, HumanMessage) and m.name == self.ASSISTANT_NAME
        ).content

        system_prompt = EVALUATION_HUB['report_review']['desc'].format(section=self.SECTION,
                                                                       assistant_name=self.ASSISTANT_NAME,
                                                                       data_tools=self.DATA_INPUT,
                                                                       writer_msg=writer_msg)

        messages = {
            'messages':[{"role": "system", "content": system_prompt}]
        }

        evaluator_agent = create_react_agent(self.openai_llm,
                                                 response_format=Router,
                                                 tools=self.tools_used)

        result = evaluator_agent.invoke(messages)
        goto = result["structured_response"]["next"]
        feedback = result["structured_response"]["feedback"]
        feedback = f"The {self.EVALUATOR_NAME}'s feedback is: \n\n {feedback}"

        return Command(
            goto=goto,
            update={
                "next": goto,
                "messages": [
                    AIMessage(content=feedback, name=self.EVALUATOR_NAME),
                    HumanMessage(content=writer_msg, name=self.ASSISTANT_NAME),
                ]
            }
        )

    def writer_node(self, state: State):

        ROUTE_TO = [self.EVALUATOR_NAME, self.SUPERVISOR_NAME]
        class Router(TypedDict):
            """
            1. Worker to route to next.
            2. Written Section written by the assistant.
            """
            next: Literal[*ROUTE_TO]
            written_section: str

        writer_agent = create_react_agent(self.openai_llm,
                                       response_format=Router,
                                       tools=self.tools_used)

        result = writer_agent.invoke(state)
        written_section = result["structured_response"]["written_section"]

        # check if evaluator has already run
        ran_eval = any(
            isinstance(m, AIMessage) and m.name == self.EVALUATOR_NAME
            for m in state["messages"]
        )
        goto = self.SUPERVISOR_NAME if ran_eval else self.EVALUATOR_NAME

        return Command(
            update={
                "messages": [
                    HumanMessage(content=written_section, name=self.ASSISTANT_NAME)
                ]
            },
            goto=goto,
        )

@AgentDecorator.inject_literal_annotations
class BSOTeam(ReportTeamBase):
    EXECUTIVE_DIRECTOR_NAME = SUP_HUB['company']['name']
    SECTION                 = SUP_HUB['bso_team']['section']
    SUPERVISOR_NAME         = SUP_HUB['bso_team']['supervisor_name']
    TEAM_NAME               = SUP_HUB['bso_team']['team_name']
    ASSISTANT_NAME          = SUP_HUB['bso_team']['assistant_name']
    EVALUATOR_NAME          = SUP_HUB['bso_team']['evaluator_name']
    DATA_INPUT              = SUP_HUB['bso_team']['data_tools']

@AgentDecorator.inject_literal_annotations
class FVPDTeam(ReportTeamBase):
    EXECUTIVE_DIRECTOR_NAME = SUP_HUB['company']['name']
    SECTION                 = SUP_HUB['fvpd_team']['section']
    SUPERVISOR_NAME         = SUP_HUB['fvpd_team']['supervisor_name']
    TEAM_NAME               = SUP_HUB['fvpd_team']['team_name']
    ASSISTANT_NAME          = SUP_HUB['fvpd_team']['assistant_name']
    EVALUATOR_NAME          = SUP_HUB['fvpd_team']['evaluator_name']
    DATA_INPUT              = SUP_HUB['fvpd_team']['data_tools']

# class BSOTeam(AgentTeamABC,
#               AgentTools):
#
#     SECTION: str = 'Business Strategy & Outlook'
#     DATA_INPUT: List[str] = ['Stock_Price_Movement', 'Latest_Earning_Transcripts', 'Latest_SEC_Filing_10K_item1']
#
#     SUPERVISOR_NAME: str = 'Supervisor'
#     ASSISTANT_NAME: str = 'BSO_Assistant'
#     EVALUATOR_NAME: str = 'BSO_Evaluator'
#
#     ROUTE_TO: List[str] = [ASSISTANT_NAME]
#
#     def __init__(self, ticker: str, year: str, quarter: str):
#         super().__init__(ticker=ticker, year=year, quarter=quarter)
#
#         self.openai_llm = OPENAI_CALLER()._get_llm()
#
#         tools_list = self._get_tools()
#         self.tools_used = [tools_list[i] for i in self.DATA_INPUT]
#
#     def evaluator_node(self, state: State) -> Command[Literal[ASSISTANT_NAME]]:
#         ROUTE_TO = self.ROUTE_TO
#
#         class Router(TypedDict):
#             """
#             1. Worker to route to next.
#             2. Provide feedback to your colleagues
#             """
#             next: Literal[*ROUTE_TO]
#             feedback: str
#
#         section: str = self.SECTION
#         assistant_name: str = self.ASSISTANT_NAME
#         data_inputs: List[str] = self.DATA_INPUT
#
#         writer_msg = next(
#             m for m in state["messages"]
#             if isinstance(m, HumanMessage) and m.name == self.ASSISTANT_NAME
#         ).content
#
#         system_prompt = EVALUATION_HUB['report_review']['desc'].format(section=section,
#                                                                        assistant_name=assistant_name,
#                                                                        data_inputs=data_inputs,
#                                                                        writer_msg=writer_msg)
#
#
#         messages = {
#             'messages':[{"role": "system", "content": system_prompt}]
#         }
#
#         bso_evaluator_agent = create_react_agent(self.openai_llm,
#                                                  response_format=Router,
#                                                  tools=self.tools_used)
#
#         result = bso_evaluator_agent.invoke(messages)
#
#         goto = result["structured_response"]["next"]
#         feedback = result["structured_response"]["feedback"]
#
#         feedback = f"The {self.EVALUATOR_NAME}'s feedback is: \n\n {feedback}"
#         return Command(
#             goto=goto,
#             update={"next": goto,
#                     "messages": [
#                         AIMessage(content=feedback, name=self.EVALUATOR_NAME),
#                         HumanMessage(content=writer_msg, name=self.ASSISTANT_NAME),
#                     ]
#                     }
#         )
#
#     def writer_node(self, state: State) -> Command[Literal[SUPERVISOR_NAME, EVALUATOR_NAME]]:
#
#         options = [self.EVALUATOR_NAME, self.SUPERVISOR_NAME]
#         class Router(TypedDict):
#             """
#             1. Worker to route to next.
#             2. Written Section written by the assistant.
#             """
#             next: Literal[*options]
#             written_section: str
#
#         bso_writer_agent = create_react_agent(self.openai_llm,
#                                        response_format=Router,
#                                        tools=self.tools_used)
#
#         result = bso_writer_agent.invoke(state)
#         written_section = result["structured_response"]["written_section"]
#
#         # check if evaluator has already run
#         ran_eval = any(
#             isinstance(m, AIMessage) and m.name == self.EVALUATOR_NAME
#             for m in state["messages"]
#         )
#         goto = self.SUPERVISOR_NAME if ran_eval else self.EVALUATOR_NAME
#
#         return Command(
#             update={
#                 "messages": [
#                     HumanMessage(content=written_section, name=self.ASSISTANT_NAME)
#                 ]
#             },
#             # We want our workers to ALWAYS "report back" to the supervisor when done
#             goto=goto,
#         )
#
# class FVPDTeam(AgentTeamABC,
#                 AgentTools):
#
#     SECTION: str = 'Fair Value & Profit Drivers'
#     DATA_INPUT: List[str] = ['Stock_Price_Movement', 'Latest_Earning_Transcripts', 'Latest_SEC_Filing_10K_item7']
#
#     SUPERVISOR_NAME: str = 'Supervisor'
#     ASSISTANT_NAME: str = 'FVPD_Assistant'
#     EVALUATOR_NAME: str = 'FVPD_Evaluator'
#
#     ROUTE_TO: List[str] = [SUPERVISOR_NAME, ASSISTANT_NAME]
#
#     def __init__(self, ticker: str, year: str, quarter: str):
#
#         super().__init__(ticker=ticker, year=year, quarter=quarter)
#
#         self.openai_llm = OPENAI_CALLER()._get_llm()
#
#         tools_list = self._get_tools()
#         self.tools_used = [tools_list[i] for i in self.DATA_INPUT]
#
#     def evaluator_node(self, state: State) -> Command[Literal[ASSISTANT_NAME]]:
#         ROUTE_TO = self.ROUTE_TO
#
#         class Router(TypedDict):
#             """
#             1. Worker to route to next.
#             2. Provide feedback to your colleagues
#             """
#             next: Literal[*ROUTE_TO]
#             feedback: str
#
#         section: str = self.SECTION
#         assistant_name: str = self.ASSISTANT_NAME
#         data_inputs: List[str] = self.DATA_INPUT
#
#         writer_msg = next(
#             m for m in state["messages"]
#             if isinstance(m, HumanMessage) and m.name == self.ASSISTANT_NAME
#         ).content
#
#         system_prompt = EVALUATION_HUB['report_review']['desc'].format(section=section,
#                                                                        assistant_name=assistant_name,
#                                                                        data_inputs=data_inputs,
#                                                                        writer_msg=writer_msg)
#
#         messages = {
#             'messages': [{"role": "system", "content": system_prompt}]
#         }
#
#         bso_evaluator_agent = create_react_agent(self.openai_llm,
#                                                  response_format=Router,
#                                                  tools=self.tools_used)
#
#         result = bso_evaluator_agent.invoke(messages)
#
#         goto = result["structured_response"]["next"]
#         feedback = result["structured_response"]["feedback"]
#
#         feedback = f"The {self.EVALUATOR_NAME}'s feedback is: \n\n {feedback}"
#         return Command(
#             goto=goto,
#             update={"next": goto,
#                     "messages": [
#                         AIMessage(content=feedback, name=self.EVALUATOR_NAME),
#                         HumanMessage(content=writer_msg, name=self.ASSISTANT_NAME),
#                     ]
#                     }
#         )
#
#     def writer_node(self, state: State) -> Command[Literal[SUPERVISOR_NAME, EVALUATOR_NAME]]:
#         options = [self.EVALUATOR_NAME, self.SUPERVISOR_NAME]
#
#         class Router(TypedDict):
#             """
#             1. Worker to route to next.
#             2. Written Section written by the assistant.
#             """
#             next: Literal[*options]
#             written_section: str
#
#         bso_writer_agent = create_react_agent(self.openai_llm,
#                                               response_format=Router,
#                                               tools=self.tools_used)
#
#         result = bso_writer_agent.invoke(state)
#         written_section = result["structured_response"]["written_section"]
#
#         # check if evaluator has already run
#         ran_eval = any(
#             isinstance(m, AIMessage) and m.name == self.EVALUATOR_NAME
#             for m in state["messages"]
#         )
#         goto = self.SUPERVISOR_NAME if ran_eval else self.EVALUATOR_NAME
#
#         return Command(
#             update={
#                 "messages": [
#                     HumanMessage(content=written_section, name=self.ASSISTANT_NAME)
#                 ]
#             },
#             # We want our workers to ALWAYS "report back" to the supervisor when done
#             goto=goto,
#         )