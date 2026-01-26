from core.scrapers.base import BaseScraper


class PiaoTianScraper(BaseScraper):

    def __init__(self, url: str, keywords: str = None):
        super().__init__(url, keywords)
        self.domain = "piaotia.com"
        self._search_url = url
        self._verify_url = "https://www.piaotia.com/modules/article/search.php"
        self._payload = {"searchtype": "articlename", "searchkey": keywords.encode(self._encoding), "Submit": "+%CB%D1+%CB%F7+"}


class ShuBaScraper(BaseScraper):

    def __init__(self, url: str, keywords: str = None):
        super().__init__(url, keywords)
        self.domain = "69shuba.com"
        self._search_url = url
        self._verify_url = "https://www.69shuba.com/modules/article/search.php"
        self._payload = {"searchkey": keywords.encode(self._encoding), "submit": "Search"}
        self._verify_selector = ".container>div:last-of-type>div"


class ShuXScraper(BaseScraper):

    def __init__(self, url: str, keywords: str = None):
        super().__init__(url, keywords)
        self._encoding = "UTF-8"
        self.domain = "69shux.co"
        self._search_url = url
        self._verify_url = "https://69shux.co/search"
        self._payload = {"searchkey": keywords, "submit": "Search"}


class TwKanScraper(BaseScraper):

    def __init__(self, url: str, keywords: str = None):
        super().__init__(url, keywords)
        self._encoding = "UTF-8"
        self.domain = "twkan.com"
        self._search_url = url
        self._verify_url = "https://twkan.com/search"
        self._payload = {"searchkey": keywords, "searchtype": "all"}
