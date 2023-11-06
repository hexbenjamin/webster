from typing import Literal

from addict import Dict

from rich.console import Console
from rich.style import Style
from rich.text import Text
from rich.theme import Theme


THEME = Dict()
THEME.base = "#CBDEE1"
THEME.error = "#CF6E93"
THEME.warn = "#D7BC8E"
THEME.success = "#6DB59E"
THEME.neutral = "#8CB4DE"
THEME.note = "#9180BD"


C = Console(
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


def C_LOG(
    level: Literal["neutral", "error", "warn", "note", "success"],
    msg: str,
    ctx: str = None,
    locals: bool = False,
    divider: bool = False,
):
    marker = Text.assemble(
        "[ ", (_csyms[level], f"{THEME[level]}"), " ]", style=f"bold {THEME.base}"
    )

    divider = Text(" || ", style=f"bold {THEME.base}") if divider else None

    msg = Text(msg, style=f"bold {THEME.base}")

    ctx = Text(f" {ctx}", Style.parse(f"italic {THEME[level]}")) if ctx else None

    C.log(Text.assemble(marker, divider or " ", msg, ctx or ""), log_locals=locals)


# C_LOG("error", "This is an error message.", "This is context.")
# C_LOG("warn", "This is a warning message.", "This is context.")
# C_LOG("success", "This is a success message.", "This is context, and locals.")
# C_LOG("neutral", "This is a neutral message.", "This is context.")
# C_LOG("note", "This is a note message.", "This is context.")
C_LOG("error", "This is a normal message.", "Almost definitely.")
