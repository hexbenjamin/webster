"""
Miscellaneous tools for `webster`.
"""

import os
import sys

import g4f
from g4f.api import Api
from loguru import logger


def run_api() -> None:
    """
    Run the G4F API interference server.
    """
    logger.disable("g4f")
    Api(engine=g4f, debug=False).run(
        bind_str="127.0.0.1:1337" if sys.platform == "win32" else "0.0.0.0:1337"
    )


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
