import functools
from typing import Dict, List, Tuple, Literal, Union, Callable
from langgraph.types import Command

class AgentDecorator:

    @staticmethod
    def inject_literal_annotations(cls):

        # 1) team_supervisor_node():
        orig_sup = cls.team_supervisor_node

        @functools.wraps(orig_sup)
        def team_supervisor_node(self, state):
            return orig_sup(self, state)

        team_supervisor_node.__annotations__ = orig_sup.__annotations__.copy()
        team_supervisor_node.__annotations__['return'] = Command[Literal[cls.ASSISTANT_NAME, "__end__"]]
        cls.team_supervisor_node = team_supervisor_node


        # 2) evaluator_node():
        orig_eval = cls.evaluator_node

        @functools.wraps(orig_eval)
        def evaluator_node(self, state):
            return orig_eval(self, state)

        evaluator_node.__annotations__ = orig_eval.__annotations__.copy()
        evaluator_node.__annotations__['return'] = Command[Literal[cls.ASSISTANT_NAME]]
        cls.evaluator_node = evaluator_node

        # 3) writer_node():
        orig_writer = cls.writer_node

        @functools.wraps(orig_writer)
        def writer_node(self, state):
            return orig_writer(self, state)

        writer_node.__annotations__ = orig_writer.__annotations__.copy()
        writer_node.__annotations__['return'] = Command[Literal[cls.EVALUATOR_NAME, cls.TEAM_SUPERVISOR_NAME]]
        cls.writer_node = writer_node
        return cls