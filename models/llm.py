from langchain_openai import ChatOpenAI
from core.config import *
import os



llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    base_url= OPENROUTER_URL,
    max_tokens=1000,
    api_key= os.getenv("OPENROUTER_API_KEY")
)