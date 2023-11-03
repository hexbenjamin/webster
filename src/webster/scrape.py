"""
<docstring>
"""

import json
import os
import requests

from collections import defaultdict
from typing import Dict

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from webster import tools
from webster.console import warn, CPRINT


class Scraper:
    """
    A class used to scrape web pages and generate a sitemap.

    Attributes:
        output_path (os.PathLike): The output path to save the scraped files.
        sitemap (Dict[str, str]): A dictionary containing the scraped URLs.

    Methods:
        get_response_and_save(url: str) -> requests.Response:
            Get the response from the specified URL and save it.
        scrape_links(scheme: str, origin: str, path: str, depth: int = 3) -> Dict[str, str]:
            Recursively scrape links from a given URL up to a specified depth.
        save_sitemap() -> None:
            Save the sitemap to the output path at `Scraper.output_path`.
    """

    def __init__(self, output_path: os.PathLike = os.getcwd()):
        """
        Initialize the Scraper.

        Args:
            output_path (os.PathLike, optional): The output path to save the scraped files. Defaults to the current working directory.
        """
        self.output_path = output_path
        self.sitemap = {}

    def get_response_and_save(self, url: str) -> requests.Response:
        """
        Get the response from the specified URL and save it.

        Args:
            url (str): The URL to send the request to.

        Returns:
            requests.Response or None: The response object if the request is successful, None otherwise.

        Raises:
            requests.exceptions.HTTPError: If the request encounters an HTTP error.

        Examples:
            >>> response = get_response_and_save("https://example.com")
            >>> print(response.status_code)
            200
        """

        response = requests.get(url)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            warn(e)
            return None

        output_path = os.path.join(self.output_path, "scrape")
        tools.mkdir(output_path)

        clean_url = tools.clean_url(url)
        with open(os.path.join(output_path, f"{clean_url}.html"), "wb") as f:
            f.write(response.content)

        return response

    def scrape_links(
        self,
        scheme: str,
        origin: str,
        path: str,
        depth: int = 3,
    ) -> Dict[str, str]:
        """
        Recursively scrape links from a given URL up to a specified depth.

        Args:
            scheme (str): The URL scheme (e.g. "http", "https").
            origin (str): The URL origin (e.g. "example.com").
            path (str): The URL path (e.g. "/about").
            depth (int, optional): The maximum depth to scrape. Defaults to 3.

        Returns:
            Dict[str, str]: A dictionary containing the scraped URLs.
        """

        webster_path = os.path.join(self.output_path, ".webster")

        site_url = f"{scheme}://{origin}{path}"
        clean_url = tools.clean_url(site_url)

        if depth < 0 or self.sitemap[clean_url] != "":
            return

        self.sitemap[clean_url] = site_url
        response = self.get_response_and_save(site_url)
        if not response:
            return

        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all("a")

        # recursion
        for link in links:
            href = urlparse(link.get("href"))

            # don't scrape external links
            if href.netloc not in [origin, ""] or href.scheme not in ["https", ""]:
                continue

            self.scrape_links(
                href.scheme or "https",
                href.netloc or origin,
                href.path,
                depth=depth - 1,
            )

        return self.sitemap

    def save_sitemap(self) -> None:
        """
        Save the sitemap to the specified output path.

        Args:
            sitemap (Dict[str, str]): The sitemap to save.
            output_path (os.PathLike): The output path to save the sitemap to.
        """

        tools.mkdir(self.output_path)

        sitemap_path = os.path.join(self.output_path, "sitemap.json")
        with open(sitemap_path, "w") as f:
            f.write(json.dumps(self.sitemap))
