import json
import os.path
from collections import deque
from os import listdir

import config
from utils.logger import get_logger

logger = get_logger()


def read_json(filepath: str) -> dict:
    with open(file=filepath, mode="r", encoding="UTF-8") as f:
        result = json.load(f)
    return result


def write_json(data: dict, filepath: str) -> None:
    with open(file=filepath, mode="w", encoding="UTF-8") as f:
        json.dump(data, f, indent=4, sort_keys=True, ensure_ascii=False)
    return None


def load_cookies(filename: str) -> dict:
    cookies_filepath = os.path.join(config.COOKIES_DIR, filename)
    if os.path.isfile(cookies_filepath):
        result = read_json(cookies_filepath)
        logger.info(f"Cookies Loaded: {result}")
        return result
    logger.warning(f"Cookies File Missing: {cookies_filepath}")
    return {}


def save_cookies(cookies: dict, filename: str) -> None:
    cookies_filepath = os.path.join(config.COOKIES_DIR, filename)
    write_json(cookies, cookies_filepath)
    logger.info(f"Cookies Written: {cookies_filepath}")
    return None


def get_log_names() -> list[str]:
    result = []
    for filename in listdir(config.LOGS_DIR):
        if filename.endswith(".log"):
            result.append(filename)
    result.sort(key=lambda x: os.path.getmtime(os.path.join(config.LOGS_DIR, x)), reverse=True)
    return result


def read_log_content(filename: str, lines: int = 1000) -> list[str]:
    log_filepath = os.path.join(config.LOGS_DIR, filename)
    if os.path.isfile(log_filepath):
        with open(file=log_filepath, mode="r", encoding="UTF-8") as f:
            return list(deque(f, maxlen=lines))
    return [f"Log File Missing: {log_filepath}"]
