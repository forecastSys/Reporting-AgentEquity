from src.config import OPENAI_API_KEY
from src.abstractions import LlmABC
from langchain_openai import ChatOpenAI

class OPENAI_CALLER(LlmABC):
    def _get_llm(self, model: str='gpt-4o'):
        return ChatOpenAI(model=model, openai_api_key=OPENAI_API_KEY)