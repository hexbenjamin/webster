"""
This module provides functions to print styled error and warning messages to the console via `rich`.
"""

from rich.console import Console
from rich.theme import Theme

_console = Console(
    theme=Theme({"error": "bold red", "warning": "bold gold1"}, inherit=False)
)
CPRINT = _console.print


def error(message: str) -> None:
    """
    Print a styled error message and exit.

    Args:
        message (str): The error message to print.

    Returns:
        None
    """

    CPRINT(f"[ [error]!!![/] ]  |  [bold italic]{message}[/]")
    exit(1)


def warn(message: str) -> None:
    """
    Print a styled warning message.

    Args:
        message (str): The warning message to print.

    Returns:
        None
    """

    CPRINT(f"[  [warning]![/]  ]  |  [italic]{message}[/]")


__all__ = ["CPRINT", "error", "warn"]
