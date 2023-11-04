"""
Miscellaneous tools for `webster`.
"""

import os

from torch.cuda import is_available

from langchain.embeddings import HuggingFaceEmbeddings

from dotenv import load_dotenv


load_dotenv()


def mkdir(path: os.PathLike) -> None:
    """
    Create a new directory at the given path if it doesn't already exist.

    Args:
        path (os.PathLike): The path to the directory to create.
    """
    if not os.path.exists(path):
        os.makedirs(path)


def clean_url(url: str) -> str:  # sourcery skip: docstrings-for-functions
    return (
        url.replace("https://", "")
        .replace("/", "-")
        .replace(".", "_")
        .replace(":", "--")
    )


# EMBEDDINGS = HuggingFaceInferenceAPIEmbeddings(
#     api_key=os.getenv("HF_TOKEN"),
#     model_name="sentence-transformers/all-MiniLM-l6-v2",
# )

EMBEDDINGS = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-l6-v2",
    model_kwargs={"device": "cuda" if is_available() else "cpu"},
    encode_kwargs={"normalize_embeddings": False, "show_progress_bar": True},
)
