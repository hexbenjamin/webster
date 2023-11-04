"""
<docstring>
"""

import json
import os
import requests

from collections import defaultdict, deque
from typing import Dict

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from webster import utils
from webster.console import cmsg


class Url:
    """
    A class representing a URL object.

    Attributes:
        url (str): The URL to parse.
        scheme (str): The scheme of the URL.
        origin (str): The origin (netloc) of the URL.
        path (str): The path of the URL.
    """

    def __init__(self, url: str):
        """
        Initialize the URL object.

        Args:
            url (str): The URL to parse.
        """
        self.url = url
        url_parts = urlparse(url)
        self.scheme = url_parts.scheme
        self.origin = url_parts.netloc
        self.path = url_parts.path


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

    def __init__(self, url: str, output_path: os.PathLike = os.getcwd()):
        """
        Initialize the Scraper.

        Args:
            url (str): The URL to scrape.
            output_path (os.PathLike, optional): The output path to save the scraped files. Defaults to the current working directory.
        """
        self.url = Url(url)
        self.output_path = os.path.join(output_path, ".webster")
        self.scrape_path = os.path.join(self.output_path, "scrape")
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
        except requests.exceptions.HTTPError as err:
            cmsg("warning", msg=err)
            return None

        if not response:
            return

        clean_url = utils.clean_url(url)
        with open(os.path.join(self.scrape_path, f"{clean_url}.html"), "wb") as f:
            f.write(response.content)

        return response

    def scrape_links(
        self,
        depth: int = 3,
    ) -> Dict[str, str]:
        """
        Recursively scrape links from a given URL up to a specified depth.

        Args:
            scheme (str): The URL scheme.
            origin (str): The URL origin.
            path (str): The URL path.
            depth (int, optional): The maximum number of link-outs to follow from the URL. Defaults to 3.

        Returns:
            Dict[str, str]: A dictionary containing the scraped URLs.
        """

        output_path = os.path.join(self.output_path, "scrape")
        utils.mkdir(output_path)

        scheme = self.url.scheme
        origin = self.url.origin
        path = self.url.path

        site_url = f"{scheme}://{origin}{path}"
        clean_url = utils.clean_url(site_url)

        self.sitemap[clean_url] = site_url

        queue = deque([(site_url, depth)])
        visited = {clean_url}

        while queue:
            url, current_depth = queue.popleft()
            if current_depth < 0:
                continue

            response = self.get_response_and_save(url)
            if not response:
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            links = soup.find_all("a")

            for link in links:
                href = urlparse(link.get("href"))

                # don't scrape external links
                if href.netloc not in [origin, ""] or href.scheme not in ["https", ""]:
                    continue

                new_url = (
                    f"{href.scheme or 'https'}://{href.netloc or origin}{href.path}"
                )
                clean_new_url = utils.clean_url(new_url)

                if clean_new_url not in visited:
                    visited.add(clean_new_url)
                    self.sitemap[clean_new_url] = new_url
                    queue.append((new_url, current_depth - 1))

        return self.sitemap

    def save_sitemap(self) -> None:
        """
        Save the sitemap to the path `.webster/scrape/sitemap.json`.
        """

        sitemap_path = os.path.join(self.output_path, "scrape", "sitemap.json")

        with open(sitemap_path, "w") as f:
            f.write(json.dumps(self.sitemap))
