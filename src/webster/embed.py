import os
import json
import chardet

from langchain.document_loaders import (
    UnstructuredMarkdownLoader,
    DirectoryLoader,
)
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

from webster import log


class Embedder:
    def __init__(self):
        pass

    def load_file_content(self) -> str:
        with open(self.filepath, "rb") as f:
            content = f.read()
            encoding = chardet.detect(content)["encoding"]
            content = content.decode(encoding or "utf-8", errors="replace")
        return content
