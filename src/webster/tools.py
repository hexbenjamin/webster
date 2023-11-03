"""
<docstring>
"""

import os


import os


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
