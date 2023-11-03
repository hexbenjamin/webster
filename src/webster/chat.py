"""
This module contains the chat functionality for Webster.
"""

from dotenv import load_dotenv

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain


load_dotenv()

LLM = ChatOpenAI(openai_api_base="localhost:1337/v1", temperature=0, model="gpt-4")
