from typing import List, Literal
from langgraph.graph import StateGraph, MessagesState, START, END

class State(MessagesState):
    next: str

# class AgentLiteral(object):
#
#     @staticmethod
#     def _get_assistant_literal(assistants: List[str]) -> Literal[List[str]]:
#         MemberLiteral = Literal[*assistants]
#         return MemberLiteral