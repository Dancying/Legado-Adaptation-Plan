from core.scrapers.sites import PiaoTianScraper
from core.scrapers.sites import ShuBaScraper
from core.scrapers.sites import ShuXScraper
from core.scrapers.sites import TwKanScraper


class Factory:
    _SCRAPER_MAP = {
        "piaotia": PiaoTianScraper,
        "69shuba": ShuBaScraper,
        "cdnshu": ShuBaScraper,
        "69shux": ShuXScraper,
        "twkan": TwKanScraper,
    }

    @classmethod
    def create(cls, url: str, keywords: str = ""):
        site = url.split("/")[2].split(".")[-2]
        scraper_cls = cls._SCRAPER_MAP.get(site)
        if url.startswith("http") and scraper_cls:
            return scraper_cls(url, keywords)
        return None
