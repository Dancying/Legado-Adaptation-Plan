import os.path
import time

from filelock import FileLock
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

import config
from utils.logger import get_logger

logger = get_logger()
ENDPOINT_URL = f"{config.BROWSER_CDP_HOST}:{config.BROWSER_CDP_PORT}"
BROWSER_LOCK = FileLock(os.path.join(config.TEMP_DIR, "browser_operation.lock"), timeout=180)


def prepare_verification_page(validation_url: str) -> None:
    """
    连接浏览器并打开新的 Cloudflare Turnstile 人机验证页面。

    :param validation_url: 可以触发人机验证的目标 URL 链接地址。
    :return: 无。

    交互操作：
        - 查询页面：若已有打开的目标 URL 验证页面则将其关闭。
        - 清除缓存：打开链接地址前清除缓存以确保能触发验证页面。
    """
    with BROWSER_LOCK:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(ENDPOINT_URL)
            context = browser.contexts[0]
            page = next((i for i in context.pages if i.url == validation_url), None)
            if page:
                logger.debug(f"Closed Duplicate Page: {validation_url}")
                page.close()
            page = context.new_page()
            page.context.new_cdp_session(page).send("Network.clearBrowserCache")
            page.goto(validation_url, wait_until="commit")
            logger.info(f"Verification Page Prepared: {validation_url}")
            browser.close()
        logger.debug(f"Waiting for page resources to load (5s)...")
        time.sleep(5)
    return None


def solve_cloudflare_turnstile(validation_url: str, selector: str) -> bool:
    """
    连接浏览器并处理 Cloudflare Turnstile 人机验证。

    :param validation_url: 目标人机验证页面的 URL 链接地址。
    :param selector: 人机验证框元素的 CSS 选择器。
    :return: 验证成功返回 True 值，验证失败返回 False 值。

    验证通过 (Return True):
        - 定位超时：在 10 秒内未定位到目标元素（未触发验证页面）。
        - 点击成功：点击后 10 秒内元素从页面中移除（验证通过）。
    验证失败 (Return False):
        - 页面丢失：在浏览器中没有发现目标 URL 的验证页面。
        - 验证超时：点击后 10 秒内页面中依然存在目标元素。
        - 程序异常：代码执行过程中出现未知错误。
    """
    logger.info(f"Starting Cloudflare Turnstile verification for {validation_url}")
    with BROWSER_LOCK:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(ENDPOINT_URL)
            context = browser.contexts[0]
            page = next((i for i in context.pages if i.url == validation_url), None)
            if page is None:
                logger.error(f"Browser Page Not Found: {validation_url}")
                return False
            try:
                element = page.locator(selector)
                logger.debug(f"Locating Element: {selector} (Timeout: 10s)...")
                element.wait_for(state="visible", timeout=10 * 1000)
                cf_verify_box = element.bounding_box()
                x_coordinate = cf_verify_box["x"] + 75
                y_coordinate = cf_verify_box["y"] + (cf_verify_box["height"] / 2)
                page.mouse.click(x_coordinate, y_coordinate)
                logger.info("Waiting for verification to pass...")
                element.wait_for(state="detached", timeout=10 * 1000)
            except PlaywrightTimeoutError:
                if element.count() == 0:
                    logger.debug("Element hidden. Verification completed.")
                else:
                    logger.warning(f"Verification Timeout: {selector}")
                    return False
            except Exception as e:
                logger.error(f"Unexpected Verification Error: {e}")
                return False
            finally:
                browser.close()
    logger.info("Cloudflare Turnstile verification successful.")
    return True


def get_domain_cookies(domain: str, clear_cookies: bool = True) -> dict:
    """
    连接浏览器并保存目标域名的 cookies 数据。

    :param domain: 需要保存 cookies 的目标域名。
    :param clear_cookies: 清除 cookies 以确保下次能触发验证页面。
    :return: 返回字典格式的 cookies 数据。
    """
    logger.info(f"Fetching Cookies: {domain}")
    result = {}
    with BROWSER_LOCK:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(ENDPOINT_URL)
            context = browser.contexts[0]
            all_cookies = context.cookies()
            for cookie in all_cookies:
                cookie_domain = cookie.get("domain", "")
                if domain in cookie_domain:
                    result[cookie["name"]] = cookie["value"]
            if clear_cookies and result:
                logger.info(f"Purging Browser Cookies: {domain}")
                context.clear_cookies(domain=domain)
                context.clear_cookies(domain=f".{domain}")
            browser.close()
    logger.info(f"Cookies Result: {result}")
    return result
