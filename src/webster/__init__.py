"""
'WEBSTER'
(C) 2023 hex benjamin (https://dev.hexbenjam.in)
GitHub: https://dev.hexbenjam.in/webster
"""

__version__ = "0.2.1"

from webster.console import C, C_LOG as log
from webster.embed import Embedder
from webster.scrape import Scraper


__all__ = ["__version__", "C", "log", "Embedder", "Scraper"]
