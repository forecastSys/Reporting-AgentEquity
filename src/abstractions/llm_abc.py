from abc import ABC, abstractmethod

class LlmABC(ABC):

    @abstractmethod
    def _get_llm(self, model: str):
        pass