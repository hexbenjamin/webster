from webster import __version__ as version
from webster.console import C


def run():
    C.log("WEBSTER", f"[bold]v{version}[/]")
