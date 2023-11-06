import asyncio
import click

from webster import __version__ as version, log
from webster.scrape import Scraper


@click.group()
def cli():
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
def scrape(url: str, depth: int, include: list = None) -> None:
    """
    Scrape a website and save the HTML files locally. Depth is the maximum number of link-outs to follow from the URL.
    """

    if include is None:
        include = ["/"]
    else:
        include = [i if i.startswith("/") else f"/{i}" for i in include]

    scraper = Scraper(site=url, depth=depth, include_paths=include)

    asyncio.run(scraper.run())


def run():
    print("")
    log("note", f"webster v{version}", "is online!")
    cli()
