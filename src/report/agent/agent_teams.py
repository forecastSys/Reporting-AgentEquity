from src.abstractions import AgentTeamABC
from src.report.agent.hub import (
    SUP_HUB,
    EVALUATION_HUB
)
from src.report.agent import (
    State,
    AgentTeamUtils,
    AgentTools
)
from src.report.llm import OPENAI_CALLER
from src.report.decorator import AgentDecorator
from typing import Dict, List, Tuple, Literal, Union, Callable, Annotated, Optional
from typing_extensions import TypedDict
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, trim_messages, AIMessage
from langgraph.types import Command
from langgraph.graph import StateGraph, MessagesState, START, END

class ReportTeamBase(AgentTeamABC,
                     AgentTools,
                     AgentTeamUtils):
    TEAM                   : str
    EXECUTIVE_DIRECTOR_NAME: str
    SECTION:                 str
    TEAM_NAME:               str
    TEAM_DESC:               str
    TEAM_SUPERVISOR_NAME:    str
    ASSISTANT_NAME:          str
    EVALUATOR_NAME:          str
    DATA_TOOLS:              List[str]
    ASSISTANT_INSTRU:        str
    PROMPT_DESCRIPTION:      str
    PROMPT_TOOLS_STR:        str
    PROMPT_DELIVERABLE:      str
    EVALUATOR_INSTRU:        str
    EVAL2ASSIST_INSTRU:      str

    def __init__(self, ticker:str, year:str, quarter:str):
        super().__init__(ticker=ticker, year=year, quarter=quarter)

        self.openai_llm = OPENAI_CALLER()._get_llm()
        tools_list = self._get_tools()
        self.tools_used = [tools_list[i] for i in self.DATA_TOOLS]

    def team_supervisor_node(self, state: State):
        assistants = [self.ASSISTANT_NAME]
        options = ["FINISH"] + assistants

        class Router(TypedDict):
            """Worker to route to next. If no workers needed, route to FINISH."""
            next: Literal[*options]
            plan: str

        system_prompt = self.TEAM_DESC.format(year=self.year,
                                              quarter=self.quarter,
                                              team_assistants=assistants,
                                              sections=self.SECTION,
                                              prompt_description=self.PROMPT_DESCRIPTION,
                                              prompt_tools_str=self.PROMPT_TOOLS_STR,
                                              prompt_deliverable=self.PROMPT_DELIVERABLE
                                             )
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
                           "messages": [HumanMessage(content=plan, name=self.TEAM_SUPERVISOR_NAME, team_name=self.TEAM_NAME)]
                       })


    def evaluator_node(self, state: State):
        ROUTE_TO = [self.ASSISTANT_NAME]

        class Router(TypedDict):
            """
            1. Worker to route to next.
            2. Provide feedback to your colleagues
            """
            next: Literal[*ROUTE_TO]
            feedback: str

        writer_msg = self._get_msg_content(state, self.ASSISTANT_NAME, self.TEAM_NAME)
        supervisor_msg = self._get_msg_content(state, self.TEAM_SUPERVISOR_NAME, self.TEAM_NAME)

        system_prompt = self.EVALUATOR_INSTRU.format(section=self.SECTION,
                                                   assistant_name=self.ASSISTANT_NAME,
                                                   data_tools=self.tools_used,
                                                   writer_msg=writer_msg,
                                                   supervisor_msg=supervisor_msg)
        messages = {
            'messages':[{"role": "system", "content": system_prompt}]
        }

        evaluator_agent = create_react_agent(self.openai_llm,
                                                 response_format=Router,
                                                 tools=self.tools_used)

        result = evaluator_agent.invoke(messages)
        goto = result["structured_response"]["next"]
        feedback = result["structured_response"]["feedback"]
        feedback = (f"The {self.EVALUATOR_NAME}'s feedback is: \n\n<START>\n{feedback}\n<END>"
                    + f"\n\n For your previous written section: \n\n<START>\n{writer_msg}\n<END>"
                    + self.EVAL2ASSIST_INSTRU)

        return Command(
            goto=goto,
            update={
                "next": goto,
                "messages": [
                    AIMessage(content=feedback, name=self.EVALUATOR_NAME, team_name=self.TEAM_NAME)
                ]
            }
        )

    def writer_node(self, state: State):

        ROUTE_TO = [self.EVALUATOR_NAME, self.TEAM_SUPERVISOR_NAME]
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
        last_msg_from_team = self._get_last_message_for_team(messages=state["messages"], target_team=self.TEAM_NAME)
        msg_content = last_msg_from_team.content + "\n\n" + self.ASSISTANT_INSTRU
        prompt = {
            "messages": [
                {"role": "system", "content": msg_content}
            ]
        }

        result = writer_agent.invoke(prompt)
        written_section = result["structured_response"]["written_section"]

        # check if evaluator has already run
        ran_eval = any(
            isinstance(m, AIMessage) and m.name == self.EVALUATOR_NAME
            for m in state["messages"]
        )
        goto = self.TEAM_SUPERVISOR_NAME if ran_eval else self.EVALUATOR_NAME

        return Command(
            update={
                "next": goto,
                "messages": [
                    HumanMessage(content=written_section, name=self.ASSISTANT_NAME, team_name=self.TEAM_NAME)
                ]
            },
            goto=goto,
        )

@AgentDecorator.inject_literal_annotations
class BSOTeam(ReportTeamBase):
    # EXECUTIVE_DIRECTOR_NAME = SUP_HUB['company']['name']
    TEAM = 'bso_team'
    SECTION                 = SUP_HUB[TEAM].section
    TEAM_SUPERVISOR_NAME    = SUP_HUB[TEAM].supervisor_name
    TEAM_NAME               = SUP_HUB[TEAM].team_name
    TEAM_DESC               = SUP_HUB[TEAM].desc
    ASSISTANT_NAME          = SUP_HUB[TEAM].assistant_name
    EVALUATOR_NAME          = SUP_HUB[TEAM].evaluator_name
    DATA_TOOLS              = SUP_HUB[TEAM].data_tools
    ASSISTANT_INSTRU        = SUP_HUB[TEAM].assistant_instruction
    PROMPT_DESCRIPTION      = SUP_HUB[TEAM].prompt_section_specific
    PROMPT_TOOLS_STR        = SUP_HUB[TEAM].prompt_section_tools
    PROMPT_DELIVERABLE      = SUP_HUB[TEAM].prompt_section_deliverable
    EVALUATOR_INSTRU        = EVALUATION_HUB.evaluator_instruction
    EVAL2ASSIST_INSTRU      = EVALUATION_HUB.evaluator2assistant_instruction

@AgentDecorator.inject_literal_annotations
class FVPDTeam(ReportTeamBase):
    # EXECUTIVE_DIRECTOR_NAME = SUP_HUB['company']['name']
    TEAM = 'fvpd_team'
    SECTION                 = SUP_HUB[TEAM].section
    TEAM_SUPERVISOR_NAME    = SUP_HUB[TEAM].supervisor_name
    TEAM_NAME               = SUP_HUB[TEAM].team_name
    TEAM_DESC               = SUP_HUB[TEAM].desc
    ASSISTANT_NAME          = SUP_HUB[TEAM].assistant_name
    EVALUATOR_NAME          = SUP_HUB[TEAM].evaluator_name
    DATA_TOOLS              = SUP_HUB[TEAM].data_tools
    ASSISTANT_INSTRU        = SUP_HUB[TEAM].assistant_instruction
    PROMPT_DESCRIPTION      = SUP_HUB[TEAM].prompt_section_specific
    PROMPT_TOOLS_STR        = SUP_HUB[TEAM].prompt_section_tools
    PROMPT_DELIVERABLE      = SUP_HUB[TEAM].prompt_section_deliverable
    EVALUATOR_INSTRU        = EVALUATION_HUB.evaluator_instruction
    EVAL2ASSIST_INSTRU      = EVALUATION_HUB.evaluator2assistant_instruction

@AgentDecorator.inject_literal_annotations
class RUTeam(ReportTeamBase):
    # EXECUTIVE_DIRECTOR_NAME = SUP_HUB['company']['name']
    TEAM = 'ru_team'
    SECTION                 = SUP_HUB[TEAM].section
    TEAM_SUPERVISOR_NAME    = SUP_HUB[TEAM].supervisor_name
    TEAM_NAME               = SUP_HUB[TEAM].team_name
    TEAM_DESC               = SUP_HUB[TEAM].desc
    ASSISTANT_NAME          = SUP_HUB[TEAM].assistant_name
    EVALUATOR_NAME          = SUP_HUB[TEAM].evaluator_name
    DATA_TOOLS              = SUP_HUB[TEAM].data_tools
    ASSISTANT_INSTRU        = SUP_HUB[TEAM].assistant_instruction
    PROMPT_DESCRIPTION      = SUP_HUB[TEAM].prompt_section_specific
    PROMPT_TOOLS_STR        = SUP_HUB[TEAM].prompt_section_tools
    PROMPT_DELIVERABLE      = SUP_HUB[TEAM].prompt_section_deliverable
    EVALUATOR_INSTRU        = EVALUATION_HUB.evaluator_instruction
    EVAL2ASSIST_INSTRU      = EVALUATION_HUB.evaluator2assistant_instruction

@AgentDecorator.inject_literal_annotations
class BDTeam(ReportTeamBase):
    TEAM = 'bd_team'
    SECTION                 = SUP_HUB[TEAM].section
    TEAM_SUPERVISOR_NAME    = SUP_HUB[TEAM].supervisor_name
    TEAM_NAME               = SUP_HUB[TEAM].team_name
    TEAM_DESC               = SUP_HUB[TEAM].desc
    ASSISTANT_NAME          = SUP_HUB[TEAM].assistant_name
    EVALUATOR_NAME          = SUP_HUB[TEAM].evaluator_name
    DATA_TOOLS              = SUP_HUB[TEAM].data_tools
    ASSISTANT_INSTRU        = SUP_HUB[TEAM].assistant_instruction
    PROMPT_DESCRIPTION      = SUP_HUB[TEAM].prompt_section_specific
    PROMPT_TOOLS_STR        = SUP_HUB[TEAM].prompt_section_tools
    PROMPT_DELIVERABLE      = SUP_HUB[TEAM].prompt_section_deliverable
    EVALUATOR_INSTRU        = EVALUATION_HUB.evaluator_instruction
    EVAL2ASSIST_INSTRU      = EVALUATION_HUB.evaluator2assistant_instruction


@AgentDecorator.inject_literal_annotations
class CATeam(ReportTeamBase):
    TEAM = 'ca_team'
    SECTION                 = SUP_HUB[TEAM].section
    TEAM_SUPERVISOR_NAME    = SUP_HUB[TEAM].supervisor_name
    TEAM_NAME               = SUP_HUB[TEAM].team_name
    TEAM_DESC               = SUP_HUB[TEAM].desc
    ASSISTANT_NAME          = SUP_HUB[TEAM].assistant_name
    EVALUATOR_NAME          = SUP_HUB[TEAM].evaluator_name
    DATA_TOOLS              = SUP_HUB[TEAM].data_tools
    ASSISTANT_INSTRU        = SUP_HUB[TEAM].assistant_instruction
    PROMPT_DESCRIPTION      = SUP_HUB[TEAM].prompt_section_specific
    PROMPT_TOOLS_STR        = SUP_HUB[TEAM].prompt_section_tools
    PROMPT_DELIVERABLE      = SUP_HUB[TEAM].prompt_section_deliverable
    EVALUATOR_INSTRU        = EVALUATION_HUB.evaluator_instruction
    EVAL2ASSIST_INSTRU      = EVALUATION_HUB.evaluator2assistant_instruction
