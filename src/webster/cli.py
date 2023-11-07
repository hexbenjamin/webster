import asyncio
import click

from rich.traceback import install

from webster import __version__ as version, log
from webster.scrape import Scraper


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
    help="the maximum depth to scrape. Defaults to 3.",
)
@click.option(
    "--include",
    "-i",
    multiple=True,
    help="only scrape URLs that start with this path. can be used multiple times.",
)
@click.option(
    "--tag-name", "-t", help="only scrape the first tag with this name on the page."
)
@click.option(
    "--out-format",
    "-f",
    help="the output format for saving scraped content. accepts 'html' or 'md'.",
)
def scrape(
    url: str,
    depth: int,
    include: list = None,
    tag_name: str = None,
    out_format: str = "html",
) -> None:
    """
    scrape a website and save the content locally. depth is the maximum number of link-outs to follow from the URL.

    args:
        url (str): the URL to scrape.
        depth (int): the maximum depth to scrape.
        include (list): a list of paths to include. defaults to None.
    """

    if include is None:
        include = ["/"]
    else:
        include = [i if i.startswith("/") else f"/{i}" for i in include]

    if out_format.lower() not in {"html", "md"}:
        log(
            "warn",
            "invalid output format!",
            "defaulting to 'html'.",
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
    """

    install(show_locals=True)

    print("")
    log("success", "webster", f"v{version}")
    cli()
