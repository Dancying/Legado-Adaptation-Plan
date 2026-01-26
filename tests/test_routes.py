import random
import time
from concurrent.futures import ProcessPoolExecutor

import requests

from utils.logger import get_logger

# 模拟生产环境的配置参数
BASE_URL = "http://127.0.0.1:39966"
API_PREFIX = "/legado"
SEARCH_ROUTE = f"{BASE_URL}{API_PREFIX}/search2026"
PROXY_ROUTE = f"{BASE_URL}{API_PREFIX}/proxy2026"
SOURCE_ROUTE = f"{BASE_URL}{API_PREFIX}/BookSource.json"

logger = get_logger()

# 测试数据池
SITES = ["shuba", "piaotian", "twkan", "shux"]
KEYWORDS = ["魔法少女", "剑徒", "诡秘", "凡人", "蘑菇", "魔王", "修仙"]
TEST_URLS = [
    {"site": "piaotian", "url": "https://www.piaotia.com/html/15/15303/11483961.html"},
    {"site": "piaotian", "url": "https://www.piaotia.abc/html/15/15303/11483961.html"},
    {"site": "shuba", "url": "https://www.69shuba.com/txt/90438/40989039"},
    {"site": "shuba", "url": "https://www.69shuba.aaa/txt/90438/40989039"},
    {"site": "twkan", "url": "https://twkan.com/txt/83202/53323077"},
    {"site": "twkan", "url": "https://twkan.bbb/txt/83202/53323077"},
    {"site": "shux", "url": "https://69shux.co/txt/70698/30593380.html"},
    {"site": "shux", "url": "https://69shux.ccc/txt/70698/30593380.html"},
]


def __simulate_request(task_id):
    """模拟单个用户的随机请求行为"""
    time.sleep(random.uniform(0.5, 2.0))  # 降低瞬时并发
    try:
        action = random.choice(["search", "proxy", "source"])
        if action == "search":
            site = random.choice(SITES)
            keyword = random.choice(KEYWORDS)
            logger.info(f"Task-{task_id}: [Search] site={site}, keyword={keyword}")
            response = requests.post(SEARCH_ROUTE, data={"site": site, "keyword": keyword}, timeout=30)
        elif action == "proxy":
            item = random.choice(TEST_URLS)
            logger.info(f"Task-{task_id}: [Proxy] site={item['site']}, url={item['url']}")
            response = requests.get(PROXY_ROUTE, params={"site": item['site'], "url": item['url']}, timeout=30)
        else:
            logger.info(f"Task-{task_id}: [Source] Requesting BookSource.json")
            response = requests.get(SOURCE_ROUTE, timeout=10)
        status = "Success" if response.status_code == 200 else f"Failed({response.status_code})"
        return f"Task-{task_id}: {action} -> {status}"
    except Exception as e:
        return f"Task-{task_id}: Error -> {str(e)}"


def test_multiple_run(process_count=4, request_total=20):
    """
    启动多进程并发测试
    :param process_count: 模拟的进程数（并发用户数）
    :param request_total: 总计发送的请求数量
    """
    logger.info(f"Starting Concurrent Test: Processes={process_count}, Total Requests={request_total}")
    start_time = time.time()
    with ProcessPoolExecutor(max_workers=process_count) as executor:
        results = list(executor.map(__simulate_request, range(request_total)))
    end_time = time.time()
    for res in results:
        print(res)
    logger.info(f"Test Finished in {end_time - start_time:.2f} seconds.")


if __name__ == '__main__':
    test_multiple_run(process_count=1, request_total=10)
