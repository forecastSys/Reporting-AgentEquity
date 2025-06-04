from abc import ABC, abstractmethod

class AgentTeamABC(ABC):

    @abstractmethod
    def team_supervisor_node(self, **kwargs):
        pass

    @abstractmethod
    def evaluator_node(self, **kwargs):
        pass

    @abstractmethod
    def writer_node(self, **kwargs):
        pass
