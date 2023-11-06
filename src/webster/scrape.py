import os
import json
import random
import aiohttp
import asyncio
from urllib.parse import urlparse
from collections import defaultdict
from bs4 import BeautifulSoup

from webster import log


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


class Scraper:
    def __init__(self, site, depth, include_paths=None):
        self.site = site
        self.depth = depth
        self.includes = include_paths
        self.sitemap = defaultdict(lambda: "")

    def clean_url(self, url: str) -> str:
        clean_url = url.replace("https://", "").replace("/", "-").replace(".", "_")
        return clean_url.removesuffix("-")

    async def fetch(self, url: str, session: aiohttp.ClientSession) -> str:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        try:
            async with session.get(url, headers=headers) as response:
                log(
                    "neutral",
                    "fetching URL:",
                    url,
                )
                return await response.text()
        except Exception as e:
            log(
                "error",
                f"failed to fetch '{url}'!",
                f"error: '{str(e)}'.",
                marker=False,
                label=True,
            )
            return None

    def extract_article(self, soup: BeautifulSoup):
        article = soup.find("article")
        return article or None

    async def save_response_content(self, content: str, path: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    async def scrape_links(
        self,
        session: aiohttp.ClientSession,
        scheme: str,
        origin: str,
        path: str,
        depth=3,
    ) -> dict:
        site_url = f"{scheme}://{origin}{path}"
        cleaned_url = self.clean_url(site_url)

        if (
            depth < 0
            or self.sitemap[cleaned_url] != ""
            or not any(path.startswith(p) for p in self.includes)
        ):
            return self.sitemap

        self.sitemap[cleaned_url] = site_url
        response_content = await self.fetch(site_url, session)
        if response_content is None:
            return self.sitemap

        if not os.path.exists("./scrape"):
            os.mkdir("./scrape")
        await self.save_response_content(
            response_content, f"./scrape/{cleaned_url}.html"
        )

        soup = BeautifulSoup(response_content, "html.parser")
        if self.extract_article(soup):
            log("note", "article found!")
        else:
            log("warn", "no article found!")

        links = soup.find_all("a")

        tasks = []
        for link in links:
            href = urlparse(link.get("href", ""))
            if (href.netloc and href.netloc != origin) or (
                href.scheme and href.scheme != "https"
            ):
                continue
            tasks.append(
                self.scrape_links(
                    session,
                    href.scheme or scheme,
                    href.netloc or origin,
                    href.path,
                    depth=depth - 1,
                )
            )

        await asyncio.gather(*tasks)
        return self.sitemap

    async def run(self):
        url = urlparse(self.site)
        log("note", "scraping initiated!" f"for: {self.site} @ depth: {self.depth}\n")

        async with aiohttp.ClientSession() as session:
            self.sitemap = await self.scrape_links(
                session, url.scheme, url.netloc, url.path, depth=self.depth
            )

        with open("./scrape/sitemap.json", "w") as f:
            json.dump(self.sitemap, f)

        log(
            "success",
            "scraping completed!",
            "sitemap saved to './scrape/sitemap.json'.",
        )
