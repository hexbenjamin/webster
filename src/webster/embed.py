"""
this module defines an Embedder class that can be used to embed documents from a given directory.

the Embedder class uses a DirectoryLoader & UnstructuredMarkdownLoader to load documents from 
a directory, a RecursiveCharacterTextSplitter to split the documents into chunks, and a Chroma 
vectorstore to store the embeddings.

the Embedder class has methods to embed the documents, map the sources of the documents to 
their corresponding entries in a sitemap JSON file, and create a Chroma database from the documents.
"""

import os
import json
import re

from typing import List, Literal
from langchain.schema.document import Document

from langchain.document_loaders import (
    DirectoryLoader,
    UnstructuredMarkdownLoader,
    BSHTMLLoader,
)
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

import chardet
from bs4 import BeautifulSoup

from rich import inspect

from webster import log


# Custom BSHTMLLoader to handle different encodings
class CustomBSHTMLLoader(BSHTMLLoader):
    """
    a custom HTML loader that extends the functionality of the BSHTMLLoader class.

    attributes:
        path (str): The path to the HTML file to be loaded.
    """

    def __init__(self, path, **kwargs):
        super().__init__(path, **kwargs)
        self.path = path

    def _load_file_content(self, file_path: os.PathLike) -> str:
        """
        load the content of a file and return it as a string.

        args:
            file_path (os.PathLike): the path to the file to load.

        returns:
            str: the content of the file.
        """

        with open(file_path, "rb") as f:  # Reading as bytes
            byte_content = f.read()
            # Detect encoding
            encoding = chardet.detect(byte_content)["encoding"]
            # Decode using detected encoding
            content = byte_content.decode(encoding or "utf-8", errors="replace")
        return content

    def load(self) -> str:
        """
        loads the content of the file at the specified path, parses it using BeautifulSoup,
        and returns the text content.

        args:
            None

        returns:
            str: the parsed text content of the HTML file.
        """

        content = self._load_file_content(self.path)
        soup = BeautifulSoup(content, **self.bs_kwargs)
        return soup.get_text(separator=" ", strip=True)


LOADERS = {
    "md": UnstructuredMarkdownLoader,
    "html": CustomBSHTMLLoader,
}

ARGS = {
    "md": {"mode": "elements", "strategy": "fast"},
    "html": {"get_text_separator": " "},
}


class Embedder:
    """
    a class for embedding text data using a specified embedding model and saving the resulting embeddings to a Chroma database.

    args:
        docs_path (os.PathLike): the path to the directory containing the text documents to be embedded.
        docs_format (Literal["html", "md"], optional): the format of the text documents. Defaults to "md".
        embedding_model (str, optional): the name of the Hugging Face embedding model to use. Defaults to "all-MiniLM-L6-v2".
        chunk_size (int, optional): the size of the chunks to split the text into. Defaults to 1000.
        chunk_overlap (int, optional): the amount of overlap between chunks. Defaults to 200.
    """


class Embedder:
    def __init__(
        self,
        docs_path: os.PathLike,
        docs_format: Literal["html", "md"] = "md",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.docs_path = docs_path

        self.loader = DirectoryLoader(
            self.docs_path,
            glob=f"*.{docs_format}",
            loader_cls=LOADERS[docs_format],
            show_progress=True,
            loader_kwargs=ARGS[docs_format],
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        self.embedding_model = HuggingFaceEmbeddings(
            model_name=embedding_model,
        )

    def map_sources(self, documents: List[Document]) -> None:
        """
        maps the sources of the given documents to their corresponding entries in the sitemap.

        args:
            documents (List[Document]): The list of documents to map sources for.

        returns:
            None
        """
        if not os.path.exists(os.path.join(self.docs_path, "sitemap.json")):
            log(
                "error",
                "sitemap.json not found!",
                "make sure to run 'webster scrape' first, and to pass in the path to the 'scrape/' directory.",
                label=True,
            )
            raise FileNotFoundError

        with open(os.path.join(self.docs_path, "sitemap.json"), "r") as f:
            sitemap = json.loads(f.read())
        for document in documents:
            document.metadata["source"] = sitemap[
                re.sub(
                    f"{self.docs_path}\/|\.html|\.md", "", document.metadata["source"]
                )
            ]

    def embed(self, db_path: os.PathLike) -> None:
        """
        embeds the loaded data using the specified embedding model and saves the resulting
        embeddings to a Chroma database at the specified path.

        args:
            db_path (os.PathLike): The path to the directory where the Chroma database should be saved.
        """

        log("note", "loading documents...")

        self.documents = self.loader.load()
        self.documents = self.text_splitter.split_documents(self.documents)
        self.map_sources(self.documents)

        log("note", "creaating Chroma database", f"at {db_path}...")
        self.db = Chroma.from_documents(
            self.documents,
            self.embedding_model,
            persist_directory=db_path,
        )

        self.db.persist()
