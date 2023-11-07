import os
import json

from langchain.document_loaders import (
    UnstructuredMarkdownLoader,
    DirectoryLoader,
)
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

# from webster import log


class Embedder:
    def __init__(
        self,
    ):
        self.loader = DirectoryLoader(
            "./scrape",
            glob="*.md",
            loader_cls=UnstructuredMarkdownLoader,
            show_progress=True,
            loader_kwargs={"mode": "elements", "strategy": "fast"},
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

        self.data = self.loader.load()
        self.documents = self.text_splitter.split_documents(self.data)
