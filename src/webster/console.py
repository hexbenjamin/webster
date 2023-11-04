"""
This module provides functions to print styled error and warning messages to the console via `rich`.
"""

from typing import Literal

from rich.console import Console
from rich.theme import Theme


_console = Console(
    theme=Theme(
        {
            "repr.str": "not bold not italic gray82",
            "accent": "bold steel_blue3",
            "error": "bold deep_pink2",
            "success": "bold spring_green3",
            "warning": "bold gold1",
        },
        inherit=False,
    ),
)
CPRINT = _console.print


_csyms = {
    "accent": " + ",
    "error": "!!!",
    "success": "+++",
    "warning": " ! ",
}


def cmsg(type: Literal["accent", "error", "success", "warning"], msg: str) -> None:
    """
    Print a styled message to the console.

    Args:
        type (str): The type of message to print.
        msg (str): The message to print.
    """
    CPRINT(f"[ [{type}]{_csyms[type]}[/{type}] ] |  {msg}")


__all__ = ["CPRINT", "error", "success", "warn"]
