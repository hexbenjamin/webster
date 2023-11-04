"""
This module contains the chat functionality for Webster.
"""

import os

from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from langchain.chains import (
    LLMChain,
    ConversationalRetrievalChain,
    create_qa_with_sources_chain,
)

from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

from g4f import Provider, models
from langchain.llms.base import LLM
from langchain_g4f import G4FLLM

from dotenv import load_dotenv


load_dotenv()


class WebsterChat:
    """
    A class used to chat with Webster.

    Attributes:
        llm (ChatOpenAI): A ChatOpenAI object used to communicate with the OpenAI API.
        memory (ConversationBufferMemory): A ConversationBufferMemory object used to store conversation history.
        db (Chroma): A LangChain Chroma object used to store and retrieve embeddings.
        chain (ConversationalRetrievalChain): A ConversationalRetrievalChain object used to chat with Webster.
    """

    def __init__(
        self, webster_path: os.PathLike = os.path.join(os.getcwd(), ".webster")
    ):
        """
        Initializes a Chat instance with an OpenAI model, a conversation buffer memory, a Chroma database, and a conversational retrieval chain.
        """
        self.webster_path = webster_path
        self.llm: LLM = G4FLLM(
            model=models.gpt_4,
            provider=Provider.RetryProvider,
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        self.db = Chroma(
            persist_directory=os.path.join(self.webster_path, "chroma"),
            embedding_function=OpenAIEmbeddings(model="text-embedding-ada-002"),
        )
        self.chain = ConversationalRetrievalChain(
            question_generator=self._make_condense_chain(),
            retriever=self.db.as_retriever(),
            memory=self.memory,
            combine_docs_chain=self._make_qa_sources_chain(),
        )

    def ask(self, query: str) -> str:
        """
        Ask a question to Webster.

        Args:
            query (str): The question to ask.

        Returns:
            str: The response from Webster.
        """
        return self.chain.run(query)

    def _make_condense_chain(self) -> LLMChain:
        """
        Creates a language model chain that can be used to generate standalone questions from a given conversation and follow-up question.

        Returns:
            LLMChain: A language model chain that can be used to generate standalone questions.
        """

        template = PromptTemplate.from_template(
            template="\n".join(
                [
                    (
                        "Given the following conversation and follow up question, rephrase the follow up question to be a standalone question in its original language. "
                        + "Make sure to avoid using any unclear pronouns."
                    ),
                    "---",
                    "Chat History:",
                    "{chat_history}",
                    "---",
                    "Follow Up Input: '{question}'",
                    "---",
                    "Standalone question: ",
                ]
            )
        )
        return LLMChain(llm=self.llm, prompt=template)

    def _make_qa_sources_chain(self) -> StuffDocumentsChain:
        """
        Creates a chain of question-answer pairs with their corresponding sources.

        Returns:
            StuffDocumentsChain: A chain of question-answer pairs with their corresponding sources.
        """
        qa_chain = create_qa_with_sources_chain(self.llm)

        doc_prompt = PromptTemplate(
            template="Content: {page_content}\nSource: {source}",
            input_variables=["page_content", "source"],
        )

        return StuffDocumentsChain(
            llm_chain=qa_chain,
            document_variable_name="context",
            document_prompt=doc_prompt,
        )
