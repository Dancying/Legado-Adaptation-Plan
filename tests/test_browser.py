import threading
import time

from core.engine.browser_launcher import close_browser_service
from core.engine.browser_launcher import launch_browser_with_cdp
from core.engine.browser_operator import get_domain_cookies
from core.engine.browser_operator import prepare_verification_page
from core.engine.browser_operator import solve_cloudflare_turnstile
from utils.logger import get_logger

logger = get_logger()


def test_start_and_stop():
    launch_browser_with_cdp()
    wait_time = 3
    logger.info(f"Sleep Time: {wait_time}")
    time.sleep(wait_time)
    close_browser_service()
    return None


def __simulate_verification(url: str, selector: str):
    for i in range(0, 3):
        prepare_verification_page(url)
        if solve_cloudflare_turnstile(url, selector):
            get_domain_cookies(url.split("//")[1].split("/")[0])
            break
    return None


def test_cloudflare_verification():
    url_selector_mapping: dict = {
        "https://www.69shuba.com/modules/article/search.php": "div.container>div:last-of-type>div",
        "https://twkan.com/": "div.main-content>div:first-of-type",
        "https://69shux.co/search": "div.main-content>div:first-of-type",
    }
    th_list: list[threading.Thread] = []
    launch_browser_with_cdp()
    for key, value in url_selector_mapping.items():
        th_list.append(threading.Thread(target=__simulate_verification, args=(key, value)))
    for th in th_list:
        th.start()
    return


if __name__ == '__main__':
    # test_start_and_stop()
    # test_cloudflare_verification()
    launch_browser_with_cdp()
    __simulate_verification("https://101kks.com/ajax_novels/chapterlist/22714.html",
                            "div.main-content>div:first-of-type")
