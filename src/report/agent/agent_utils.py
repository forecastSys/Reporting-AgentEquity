from typing import List, Literal, Annotated, Optional
from langgraph.graph import StateGraph, MessagesState, START, END
import operator
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

class State(MessagesState):
    next: Annotated[str, operator.add]
# class AgentLiteral(object):
#
#     @staticmethod
#     def _get_assistant_literal(assistants: List[str]) -> Literal[List[str]]:
#         MemberLiteral = Literal[*assistants]
#         return MemberLiteral

class AgentUtils:

    @staticmethod
    def get_last_message_for_team(messages: List, target_team: str) -> Optional[BaseMessage]:
        """
        Scan backwards through the messages list and return the last
        message whose .team_name matches target_team.
        """
        for msg in reversed(messages):
            if getattr(msg, "team_name", None) == target_team:
                return msg
        return None