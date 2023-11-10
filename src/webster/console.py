from typing import Literal

from addict import Dict

from rich.console import Console
from rich.style import Style
from rich.text import Text
from rich.theme import Theme


THEME = THM = Dict()

THEME.base = "#CBDEE1"
THEME.error = "#CF6E93"
THEME.warn = "#D7BC8E"
THEME.success = "#6DB59E"
THEME.neutral = "#8CB4DE"
THEME.note = "#9180BD"


C = Console(  # sourcery skip: avoid-single-character-names-variables
    theme=Theme(
        {
            "repr.number": "none",
            "repr.number_complex": "none",
            "log.message": Style.parse(THEME.base),
            "log.level": Style.parse(THEME.base),
            "log.path": Style.parse(f"dim {THEME.base}"),
            "log.time": Style.parse(f"dim {THEME.note}"),
        }
    )
)


_csyms = {
    "error": "!!!",
    "warn": " ! ",
    "success": "+++",
    "neutral": " > ",
    "note": " + ",
}


def c_log(
    level: Literal["neutral", "error", "warn", "note", "success"],
    msg: str,
    ctx: str = None,
    marker: bool = True,
    label: bool = False,
    locals: bool = False,
) -> None:
    """
    logs a stylized message with the specified level.

    args:
        level (Literal["neutral", "error", "warn", "note", "success"]): the log level.
        msg (str): the message to log.
        ctx (str, optional): the context of the log message. defaults to None.
        marker (bool, optional): whether to include a marker in the log message. defaults to True.
        label (bool, optional): whether to include a label in the log message. defaults to False.
        locals (bool, optional): whether to include local variables in the log message. defaults to False.
    """
    marker = (
        Text.assemble(
            "[ ",
            (_csyms[level], f"{THM[level]}"),
            " ]",
            "  ",
            style=f"bold {THM.base}",
        )
        or None
    )

    label = (
        Text(
            f" {level.upper()}: ",
            style=f"bold black on {THM[level]}",
        ).append(
            "  ",
            style="reset",
        )
    ) or None

    msg = Text(msg, style=f"bold {THM.base}")
    ctx = Text(f" {ctx}", Style.parse(f"italic {THM[level]}")) if ctx else None

    C.log(Text.assemble(marker or "", label or "", msg, ctx or ""), log_locals=locals)
