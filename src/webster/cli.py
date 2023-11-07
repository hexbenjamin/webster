"""
this module contains the command-line interface for webster.
it provides a CLI for scraping a website and saving the content locally.
"""

import asyncio
import click

from webster import __version__ as version, log
from webster.scrape import Scraper

from rich.traceback import install


@click.group()
def cli() -> None:
    """
    entrypoint for the webster CLI.

    args:
        None

    returns:
        None
    """
    pass


@cli.command()
@click.argument("url")
@click.option(
    "--depth",
    "-d",
    default=3,
    help="The maximum depth to scrape. Defaults to 3.",
)
@click.option(
    "--include",
    "-i",
    multiple=True,
    help="Only scrape URLs that start with this path. Can be used multiple times.",
)
@click.option(
    "--tag-name", "-t", help="Only scrape the first tag with this name on the page."
)
@click.option(
    "--out-format",
    "-f",
    help="The output format for saving scraped content. Accepts 'html' or 'md'.",
)
def scrape(
    url: str,
    depth: int,
    include: list = None,
    tag_name: str = None,
    out_format: str = "html",
) -> None:
    """
    scrape a website and save the content locally.
    depth is the maximum number of link-outs to follow from the URL.

    args:
        url (str): The URL to scrape.
        depth (int): The maximum depth to scrape.
        include (list): A list of paths to include. Defaults to None.

    returns:
        None
    """

    if include is None:
        include = ["/"]
    else:
        include = [i if i.startswith("/") else f"/{i}" for i in include]

    if out_format.lower() not in {"html", "md"}:
        log(
            "warn",
            "Invalid output format!",
            "Defaulting to 'html'.",
            marker=False,
            label=True,
        )
        out_format = "html"

    scraper = Scraper(
        site=url,
        depth=depth,
        include_paths=include,
        tag_filter={"name": tag_name} if tag_name else None,
        output_format=out_format,
    )

    asyncio.run(scraper.run())


def run() -> None:
    """
    entrypoint for the 'webster' command-line script.

    args:
        None

    returns:
        Nones
    """

    install(show_locals=True)

    print("")
    log("success", "webster", f"v{version}")
    cli()
