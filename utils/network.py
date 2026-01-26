from base64 import b64decode

import requests

from utils.logger import get_logger

logger = get_logger()


def fetch_data_by_proxyscotch(url: str, method: str = "GET") -> bytes:
    """
    通过 Proxyscotch 代理服务器获取目标 URL 的响应数据。
    部分网站不会对 Proxyscotch 代理服务器触发 Cloudflare 人机验证。

    :param url: 目标 URL 的链接地址。
    :param method: 目标 URL 的请求方式。若为 POST 需将请求体拼接到 URL 后。
    :return: 目标 URL 的响应字节流，发生异常则返回空字节。
    """
    proxy_url = "https://proxy.hoppscotch.io/"
    proxy_payload = {"url": url, "method": method, "wantsBinary": True}
    proxy_headers = {"origin": "https://hoppscotch.io"}
    logger.debug(f"Proxyscotch Payload: {proxy_payload}")
    try:
        response = requests.post(proxy_url, json=proxy_payload, headers=proxy_headers, timeout=20)
        logger.info(f"Proxyscotch Success: {url}")
        response_data = response.json().get("data", "")
        missing_padding = len(response_data) % 4
        if missing_padding:
            response_data += "=" * (4 - missing_padding)
        return b64decode(response_data)
    except Exception as e:
        logger.error(f"Proxyscotch Error: {url}, Detail: {e}")
    return b""


def fetch_data_by_requests(url: str, headers: dict = None, cookies: dict = None) -> bytes:
    """
    通过 requests 库获取目标 URL 的响应数据。此方法仅用于 GET 请求。

    :param url: 目标 URL 的链接地址。
    :param headers: 目标 URL 需要的请求头数据。
    :param cookies: 目标 URL 需要的 Cookies 数据。
    :return: 目标 URL 的响应字节流，发生异常则返回空字节。
    """
    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=15)
        logger.info(f"Requests Success: {url}")
        return response.content
    except Exception as e:
        logger.error(f"Requests Error: {url}, Detail: {e}")
    return b""
