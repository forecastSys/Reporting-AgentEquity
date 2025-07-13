from typing import List, Literal, Annotated, Optional, Dict
from langgraph.graph import StateGraph, MessagesState, START, END
import operator
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from textwrap import dedent
import inspect

class State(MessagesState):
    next: Annotated[str, operator.add]

class AgentTeamUtils:

    @staticmethod
    def _get_last_message_for_team(messages: List, target_team: str) -> Optional[BaseMessage]:
        """
        Scan backwards through the messages list and return the last
        message whose .team_name matches target_team.
        """
        for msg in reversed(messages):
            if getattr(msg, "team_name", None) == target_team:
                return msg
        return None

    @staticmethod
    def _get_msg_content(state, name, team_name):
        label = name.split('_')[1]
        caller_name = inspect.stack()[1].function
        try:
            return next(
                m for m in state["messages"]
                if isinstance(m, HumanMessage) and m.name == name and m.team_name == team_name
            ).content
        except StopIteration:
            raise ValueError(f"[{caller_name}]: Missing message from {label} ('{name}' in team '{team_name}')")

class AgentWorkflowUtils:

    @staticmethod
    def _group_messages_by_team(entries):
        grouped = {}
        for entry in entries:
            for _, content in entry.items():
                team = content['messages'][0].team_name
                # team_member = content['messages'][0].name
                msgs = content['messages'][0]
                # msgs_dict = {team_member: msgs}
                grouped.setdefault(team, []).append(msgs)
        return grouped

    @staticmethod
    def _get_last_msg_for_team(team_msg_dict: Dict[str, List], team_name: str, team_member: str) -> Optional[BaseMessage]:
        msgs = []
        for msg in team_msg_dict[team_name]:
            if msg.name == team_member:
                msgs.append(msg)

        return msgs[-1]

