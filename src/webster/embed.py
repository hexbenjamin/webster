"""
This module defines an Embedder class that can be used to embed documents from a given directory.
The Embedder class uses a DirectoryLoader to load documents from a directory, a RecursiveCharacterTextSplitter to split the documents into chunks, and a Chroma vectorstore to store the embeddings.
The Embedder class has methods to embed the documents, map the sources of the documents to their corresponding entries in a sitemap, and create a Chroma database from the documents.
"""

import os
import json
from typing import List

from langchain.document_loaders import (
    BSHTMLLoader,
    DirectoryLoader,
)
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

from dotenv import load_dotenv

from webster.console import cmsg
from webster.tools import api_thread


load_dotenv()

LOADER = DirectoryLoader(
    "",
    glob="*.html",
    loader_cls=BSHTMLLoader,
    show_progress=True,
    loader_kwargs={
        "get_text_separator": " ",
        "open_encoding": "ISO-8859-1",
    },
)


SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)


class Embedder:
    """
    A class used to embed documents using OpenAI's text-embedding-ada-002 model.

    Attributes:
        document_loader (DocumentLoader): A DocumentLoader object used to load documents.
        text_splitter (TextSplitter): A TextSplitter object used to split documents into chunks.
        chunk_size (int): The size of each chunk in tokens.
        chunk_overlap (int): The overlap between chunks in tokens.
        webster_path (os.PathLike): The path to the `.webster` directory.
        embedding_model (OpenAIEmbeddings): An OpenAIEmbeddings object used to embed text.
        db (Chroma): A LangChain Chroma object used to store and retrieve embeddings.
        db_path (os.PathLike): The path to the Chroma database.
    """

    def __init__(
        self,
        webster_path: os.PathLike,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:
        """
        Initializes the Embedder object.

        Args:
            webster_path: The path to the `.webster` directory.
            chunk_size: The size of each chunk in tokens (default: 1000).
            chunk_overlap: The overlap between chunks in tokens (default: 200).
        """

        api_thread()

        self.document_loader = LOADER

        self.text_splitter = SPLITTER
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.webster_path = webster_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")

        self.db: Chroma = None
        self.db_path = os.path.join(self.webster_path, "chroma")

    def embed(self) -> None:
        """
        Embeds the documents in the input path.
        """
        data = self.document_loader.load()
        data = self.text_splitter.split_documents(data)
        self.map_sources(data)
        self.create_db(data)

    def map_sources(self, data: List[Document]) -> None:
        """
        Maps the source of each document in the given list to its corresponding entry in the sitemap.

        Args:
            data (List[Document]): The list of documents to map sources for.

        Returns:
            None
        """
        sitemap_path = os.path.join(self.webster_path, "scrape", "sitemap.json")

        if not os.path.exists(sitemap_path):
            cmsg(
                "error",
                msg=(
                    "No sitemap found. Please run 'webster scrape' before embedding, "
                    + "and ensure you have provided the correct path to the '.webster' directory."
                ),
            )

        with open(sitemap_path, "r") as f:
            sitemap = json.loads(f.read())
        for doc in data:
            doc.metadata["source"] = sitemap[
                os.path.split(doc.metadata["source"])[-1].replace(".html", "")
            ]

    def create_db(self, data: List[Document]) -> None:
        """
        Creates a Chroma database from the given list of documents and saves it to disk.

        Args:
            data (List[Document]): A list of Document objects to create the database from.

        Returns:
            None
        """
        self.db = Chroma.from_documents(
            data,
            self.embedding_model,
            persist_directory=self.db_path,
        )
        self.db.persist()

    @property
    def webster_path(self) -> os.PathLike:
        """
        Returns the input path for the embedder.
        """
        return self._webster_path

    @webster_path.setter
    def webster_path(self, value: os.PathLike) -> None:
        """
        Sets the input path for the document loader.

        Args:
            value (os.PathLike): The path to the input directory.
        """
        self._webster_path = value
        self.document_loader.path = os.path.join(self._webster_path, "scrape")

    @property
    def chunk_size(self) -> int:
        """
        Returns the chunk size used by the embedder.
        """
        return self._chunk_size

    @chunk_size.setter
    def chunk_size(self, value: int) -> None:
        """
        Set the chunk size for text splitting.

        Args:
            value (int): The size of each chunk.

        Returns:
            None
        """
        self._chunk_size = value
        self.text_splitter.chunk_size = self._chunk_size

    @property
    def chunk_overlap(self) -> int:
        """
        Returns the number of overlapping words between adjacent chunks.
        """
        return self._chunk_overlap

    @chunk_overlap.setter
    def chunk_overlap(self, value: int) -> None:
        """
        Set the overlap between text chunks.

        Args:
            value (int): The overlap value to set.

        Returns:
            None
        """
        self._chunk_overlap = value
        self.text_splitter.chunk_overlap = self._chunk_overlap
