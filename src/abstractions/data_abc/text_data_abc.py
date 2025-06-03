from abc import ABC, abstractmethod
from typing import List, Dict
class TextDataABC(ABC):

    @abstractmethod
    def fetch(self, **kwargs) -> Dict[str, str]:
        pass

    @abstractmethod
    def fetch_from_db(self, **kwargs) -> Dict[str, str]:
        pass