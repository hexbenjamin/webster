"""
this module contains a web scraper for scraping web pages and processing links.

the Scraper class can be used to scrape a web page and save the scraped content in either HTML or Markdown format.
the scraper can also recursively process links found in the web page up to a specified depth.

the module also contains several utility functions for cleaning URLs, extracting tags from BeautifulSoup objects,
parsing Markdown content, and decomposing media tags.

classes:
    Scraper

functions:
    clean_url
    extract_tag
    parse_markdown
    decompose_media

constants:
    USER_AGENTS
    HTML_IO
"""

import os
import json
import random
import aiohttp
import asyncio
import re

from time import sleep

from urllib.parse import urlparse
from collections import defaultdict

from typing import Union

import bs4
from bs4 import BeautifulSoup
import html2text

from webster import wlog

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
]

HTML_IO = html2text.HTML2Text()


def clean_url(url: str) -> str:
    """
    Clean the URL by replacing slashes, dots, and colons with dashes.

    args:
        url (str): the URL to be cleaned.

    returns:
        str: the cleaned URL.

    """

    return re.sub(r"[/.:]", "-", url).removesuffix("-")


def extract_tag(soup: BeautifulSoup, **kwargs) -> bs4.element.Tag | bs4.element.NavigableString | None:
    """
    extract and return the first tag that matches the given keyword arguments from the BeautifulSoup object.

    args:
        soup (BeautifulSoup): the BeautifulSoup object to search in.
        **kwargs: keyword arguments specifying the attributes and values to match. these will be passed to the 'soup.find()' method.

    returns:
        Tag or None: the first matching tag, or None if no match is found.

    """
    return soup.find(**kwargs)


def parse_markdown(tag: BeautifulSoup) -> str:
    """
    parse the given BeautifulSoup tag as Markdown and return the resulting HTML as a string.

    args:
        tag (BeautifulSoup): The BeautifulSoup tag to parse.

    returns:
        str: the parsed Markdown content as HTML.

    """
    return HTML_IO.handle(str(tag))


def decompose_media(tag: BeautifulSoup) -> BeautifulSoup:
    """
    decompose the given BeautifulSoup tag and return the resulting tag.

    args:
        tag (BeautifulSoup): The BeautifulSoup tag to parse.

    returns:
        BeautifulSoup: the decomposed tag.

    """
    for media in (
            tag.find_all("img") + tag.find_all("video") + tag.find_all(class_="breadcrumbs")
    ):
        media.decompose()
    return tag


async def fetch(url: str, session: aiohttp.ClientSession) -> None:
    """
    Fetch the content of the given URL using the provided aiohttp ClientSession.

    args:
        url (str): The URL to fetch.
        session (aiohttp.ClientSession): The aiohttp ClientSession to use for the request.

    returns:
        str: The content of the response as a string, or None if an error occurs.

    Raises:
        aiohttp.ClientError: If an error occurs during the request.
    """

    headers = {"User-Agent": random.choice(USER_AGENTS)}
    try:
        async with session.get(url, headers=headers) as response:
            return await response.text()
    except aiohttp.ClientError as e:
        wlog(
            "error",
            f"failed to fetch '{url}'!",
            f"error: '{str(e)}'.",
            marker=False,
            label=True,
        )
        return None


async def save_output(content: str, path: str) -> None:
    """
    Save the given content to the given path.

    args:
        content (str): The content to save.
        path (str): The path to save the content to.

    returns:
        None
    """

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


class Scraper:
    """
    A web scraper for scraping web pages and processing links.

    args:
        site (str): the URL of the web page to scrape.
        depth (int): the maximum depth for recursive link processing.
        include_paths (list, optional): list of paths to include for link processing.
        tag_filter (dict, optional): dictionary of tag attributes to filter during scraping.
        output_format (str, optional): the output format for saving scraped content. must be "html" or "md". defaults to "html".
    """

    def __init__(
            self,
            site: str,
            depth: int,
            include_paths: list = None,
            tag_filter: dict = None,
            output_format: str = None,
            webster_path: str = ".webster",
    ) -> None:
        """
        Initialize the Scraper object.

        args:
            site (str): The URL of the web page to scrape.
            depth (int): The maximum depth for recursive link processing.
            include_paths (list, optional): List of paths to include for link processing.
            tag_filter (dict, optional): Dictionary of tag attributes to filter during scraping.
            output_format (str, optional): The output format for saving scraped content.

        returns:
            None
        """

        self.site = site
        self.depth = depth
        self.includes = include_paths
        self.tag_filter = tag_filter or {"name": "body"}

        self.output_format = (
            output_format.lower() if output_format.lower() in {"html", "md", "urls"} else "urls"
        )
        if self.output_format == "urls":
            self.urls_list = []

        self.scrape_path = os.path.join(webster_path, "scrape")
        self.sitemap = defaultdict(lambda: "")

    async def process_links(
            self,
            links: list,
            session: aiohttp.ClientSession,
            scheme: str,
            origin: str,
            depth: int,
    ) -> None:
        """
        Process the links found in the web page.

        args:
            links (list): a list of BeautifulSoup tags representing the links.
            session (aiohttp.ClientSession): the aiohttp ClientSession to use for making requests.
            scheme (str): the URL scheme [e.g., "http", "https"].
            origin (str): the URL origin.
            depth (int): the maximum depth for recursive link processing.

        returns:
            None
        """

        tasks = []
        for link in links:
            href = urlparse(link.get("href", ""))
            if (href.netloc and href.netloc != origin) or (
                    href.scheme and href.scheme != "https"
            ):
                continue
            tasks.append(
                self.scrape(
                    session,
                    href.scheme or scheme,
                    href.netloc or origin,
                    href.path,
                    depth - 1,
                )
            )
        await asyncio.gather(*tasks)

    async def scrape(
            self,
            session: aiohttp.ClientSession,
            scheme: str,
            origin: str,
            path: str,
            depth: int,
    ) -> None:
        """
        scrape the web page at the given URL and process the links recursively.

        args:
            session: the aiohttp ClientSession to use for making requests.
            scheme (str): the URL scheme [e.g., "http", "https"].
            origin (str): the URL origin.
            path (str): the URL path.
            depth (int): the maximum depth for recursive link processing.

        returns:
            None
        """

        if depth < 0 or (
                len(self.includes) > 0
                and all(not path.startswith(inc) for inc in self.includes)
        ):
            return

        site_url = f"{scheme}://{origin}{path}"

        response_content = await fetch(site_url, session)
        if response_content is None:
            return

        if not os.path.exists(self.scrape_path):
            os.makedirs(self.scrape_path)

        if self.output_format == "urls":
            if site_url not in self.urls_list:
                wlog("neutral", "saving URL:", site_url, marker=True, label=False)
                self.urls_list.append(site_url)
                soup = BeautifulSoup(response_content, "html.parser")
        else:
            cleaned_url = clean_url(origin + path)

            if self.sitemap[cleaned_url] != "" or site_url == "":
                return

            self.sitemap[cleaned_url] = site_url

            soup = BeautifulSoup(response_content, "html.parser")

            if output := extract_tag(soup, **self.tag_filter):
                output = decompose_media(output).decode()
                if self.output_format == "md":
                    output = parse_markdown(output)

                wlog("neutral", "saving URL:", site_url, marker=True, label=False)

                filename = f"{cleaned_url}.{self.output_format}"

                await save_output(
                    output,
                    os.path.join(self.scrape_path, filename),
                )

        await self.process_links(soup.find_all("a"), session, scheme, origin, depth)

    async def run(self) -> None:
        """
        run the web scraping process.

        args:
            None

        returns:
            None

        """

        url = urlparse(self.site)
        wlog("note", "scraping initiated!", f"for: {self.site} @ depth: {self.depth}\n")

        async with aiohttp.ClientSession() as session:
            await self.scrape(session, url.scheme, url.netloc, url.path, self.depth)

        if self.output_format == "urls":
            with open(os.path.join(self.scrape_path, f"{url.netloc.replace('.', '-')}.urls"), "w") as f:
                f.write("\n".join(self.urls_list))
        else:
            with open(os.path.join(self.scrape_path, "sitemap.json"), "w") as f:
                json.dump(self.sitemap, f)
