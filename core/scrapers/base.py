import os.path
import os.path
import threading

import requests
from filelock import FileLock
from filelock import Timeout as FileLockTimeoutError

import config
from core.engine.browser_launcher import close_browser_service
from core.engine.browser_launcher import get_cdp_version
from core.engine.browser_launcher import launch_browser_with_cdp
from core.engine.browser_operator import get_domain_cookies
from core.engine.browser_operator import prepare_verification_page
from core.engine.browser_operator import solve_cloudflare_turnstile
from utils.file_io import load_cookies
from utils.file_io import read_json
from utils.file_io import save_cookies
from utils.file_io import write_json
from utils.logger import get_logger
from utils.network import fetch_data_by_proxyscotch
from utils.network import fetch_data_by_requests


class BaseScraper:

    def __init__(self, url: str, keywords: str = None):
        self._logger = get_logger()
        self._encoding = "GB18030"
        self.domain = url.split("/")[2]
        self._proxy_url = url
        self._verify_url = self._proxy_url
        self._payload = {"searchkey": keywords.encode(self._encoding)}
        self._headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
        }
        self._failure_text = "Just a moment..."
        self._verify_selector = "div.main-content>div:first-of-type"
        self._image_extensions = (".jpg", ".jpeg", "png", ".gif", ".webp", ".bmp", ".svg", ".tiff")
        self._browser_task_count_file_path = os.path.join(config.TEMP_DIR, "browser_task_count")
        self._browser_cdp_version_file_path = os.path.join(config.TEMP_DIR, "browser_cdp_version")

    def search(self) -> str:
        try:
            with FileLock(os.path.join(config.TEMP_DIR, f"{self.domain}_search.lock"), timeout=15):
                response = requests.post(url=self._proxy_url, data=self._payload,
                                         headers=self._set_browser_headers(),
                                         cookies=load_cookies(self.domain),
                                         timeout=10)
                response_text = response.content.decode(self._encoding, errors="ignore")
                if self._failure_text not in response_text:
                    self._logger.info(f"Search Success: {self._payload}")
                    return response_text
        except FileLockTimeoutError:
            self._logger.error(f"Search Timeout: {self._proxy_url}, Payload: {self._payload}")
            return "Search Server Busy"
        except Exception as e:
            self._logger.error(f"Unexpected Error: {e}")
            return "Search Server Error"
        return self._handle_expiration()



    def proxy(self) -> str | bytes:
        try:
            with FileLock(os.path.join(config.TEMP_DIR, f"{self.domain}_proxy.lock"), timeout=15):
                is_image = self._proxy_url.lower().endswith(self._image_extensions)
                for mode in ("requests", "proxyscotch"):
                    response = self.__get_page_data(self._proxy_url, load_cookies(self.domain), mode)
                    if not response:
                        continue
                    if is_image:
                        return response
                    response_text = response.decode(self._encoding, errors="ignore")
                    if self._failure_text not in response_text:
                        return response_text
        except FileLockTimeoutError:
            self._logger.error(f"Proxy Timeout: {self._proxy_url}")
            return "Proxy Server Busy"
        except Exception as e:
            self._logger.error(f"Unexpected Error: {e}")
            return "Proxy Server Error"
        return self._handle_expiration()



    def __get_browser_task_count(self) -> int:
        if os.path.isfile(self._browser_task_count_file_path):
            with open(file=self._browser_task_count_file_path, mode="r", encoding="UTF-8") as f:
                content = f.read().strip()
            task_count = int(content) if content.isdigit() else 0
            return task_count
        self._logger.warning(f"Browser Task Count File Missing: {self._browser_task_count_file_path}")
        return 0

    def _increment_browser_task_count(self) -> int:
        with FileLock(f"{self._browser_task_count_file_path}.lock", timeout=10):
            self._logger.debug("Increasing browser tasks...")
            new_count = self.__get_browser_task_count() + 1
            with open(file=self._browser_task_count_file_path, mode="w", encoding="UTF-8") as f:
                f.write(str(new_count))
            self._logger.info(f"Browser Task Count: {new_count}")
        return new_count

    def _decrement_browser_task_count(self) -> int:
        with FileLock(f"{self._browser_task_count_file_path}.lock", timeout=10):
            self._logger.debug("Decreasing browser tasks...")
            new_count = max(0, self.__get_browser_task_count() - 1)
            with open(file=self._browser_task_count_file_path, mode="w", encoding="UTF-8") as f:
                f.write(str(new_count))
            self._logger.info(f"Browser Task Count: {new_count}")
        return new_count

    def _set_browser_headers(self) -> dict:
        if os.path.isfile(self._browser_cdp_version_file_path):
            with FileLock(f"{self._browser_cdp_version_file_path}.lock", timeout=5):
                version_info = read_json(self._browser_cdp_version_file_path)
                if version_info:
                    self._headers["User-Agent"] = version_info["User-Agent"]
        self._logger.debug(f"Current Browser Headers: {self._headers}")
        return self._headers

    def _save_browser_cdp_version(self) -> dict:
        with FileLock(f"{self._browser_cdp_version_file_path}.lock", timeout=10):
            browser_cdp_version = get_cdp_version()
            write_json(browser_cdp_version, self._browser_cdp_version_file_path)
            self._logger.debug("Successfully saved browser CDP version.")
        return browser_cdp_version

    def __get_page_data(self, url: str, cookies: dict, mode: str) -> bytes:
        """
        获取网页数据，分为网页 HTML 文本或网页图片。

        :param url: 目标 URL 的链接地址。
        :param cookies: 目标 URL 需要的 Cookies 数据。
        :param mode: 请求执行模式， "requests" 或 "proxyscotch"。
        :return: 目标 URL 的响应字节流，发生异常则返回空字节。
        """
        try:
            if mode == "proxyscotch":
                return fetch_data_by_proxyscotch(url)
            return fetch_data_by_requests(url, self._set_browser_headers(), cookies)
        except Exception as e:
            self._logger.error(f"Request Error: {e}")
        return b""

    def __update_cookies(self) -> None:
        try:
            with FileLock(os.path.join(config.TEMP_DIR, f"{self.domain}_update_cookies.lock"), timeout=0):
                self._logger.info(f"{self.domain} Cookies Update Task Starting.")
                launch_browser_with_cdp()
                self._save_browser_cdp_version()
                self._increment_browser_task_count()
                cookies = {}
                for i in range(3):
                    prepare_verification_page(self._verify_url)
                    if solve_cloudflare_turnstile(self._verify_url, self._verify_selector):
                        cookies = get_domain_cookies(self.domain, True)
                        break
                save_cookies(cookies, self.domain)
                self._logger.info(f"{self.domain} Cookies Update Task Finished.")
        except FileLockTimeoutError:
            self._logger.warning(f"{self.domain} Update Task Already Running.")
        except Exception as e:
            self._logger.error(f"Failed to Update {self.domain} Cookies: {e}")
        finally:
            if self._decrement_browser_task_count() == 0:
                close_browser_service()
        return None

    def _handle_expiration(self) -> str:
        self._logger.warning(f"{self.domain} Cookies Expired.")
        threading.Thread(target=self.__update_cookies).start()
        return "Updating Domain Cookies"
