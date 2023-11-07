"""
this module contains the command-line interface for webster.
it provides a CLI for scraping a website and saving the content locally.
"""

import os
import asyncio

import click

from webster import (
    __version__ as version,
    log,
    Embedder,
    Scraper,
)


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
    help="the maximum depth to scrape. defaults to 3.",
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
    help="the output format for saving scraped content. accepts 'html' or 'md', defaults to 'md'.",
    default="md",
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

    out_format = out_format or ""
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
        output_format=out_format or "md",
    )

    asyncio.run(scraper.run())

    log(
        "success",
        "scraping completed!",
        "sitemap saved to './scrape/sitemap.json'.",
    )


@cli.command()
@click.option(
    "--docs-path",
    "-d",
    help="the path to the directory containing the scraped documents.",
)
@click.option(
    "--docs-format",
    "-f",
    default="md",
    help="the format of the text documents. defaults to 'md'.",
)
@click.option(
    "--embed-model",
    "-e",
    default="all-MiniLM-L6-v2",
    help="the name of the Hugging Face embedding model to use. defaults to 'all-MiniLM-L6-v2'.",
)
@click.option(
    "--chunk-size",
    "-cs",
    default=1000,
    help="the size of the chunks to split the text into. defaults to 1000.",
)
@click.option(
    "--chunk-overlap",
    "-co",
    default=200,
    help="the amount of overlap between chunks. defaults to 200.",
)
def embed(
    docs_path: str,
    docs_format: str,
    embed_model: str,
    chunk_size: int,
    chunk_overlap: int,
) -> None:
    if not os.path.exists(docs_path):
        log(
            "error",
            "'scrape/' directory not found!",
            (
                "make sure to run 'webster scrape' first, "
                + "and to pass in the path to the 'scrape/' directory with '-d'."
            ),
            label=True,
        )
        return

    docs_format = docs_format or ""
    if docs_format.lower() not in {"html", "md"}:
        log(
            "warn",
            "invalid document format!",
            "defaulting to 'md'.",
            marker=False,
            label=True,
        )
        docs_format = "md"

    log("note", "creating embedder...")
    embedder = Embedder(docs_path, docs_format, embed_model, chunk_size, chunk_overlap)

    embedder.embed(db_path="./chroma")

    log(
        "success",
        "embedding completed!",
        "database saved.",
    )


def run() -> None:
    """
    entrypoint for the 'webster' command-line script.

    args:
        None

    returns:
        Nones
    """

    from rich.traceback import install

    install(show_locals=True)

    print(" . . . ")
    log("success", "webster", f"v{version}")
    cli()
