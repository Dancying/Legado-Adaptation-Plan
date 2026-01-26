from flask import Blueprint
from flask import make_response
from flask import render_template
from flask import request

import config
from core.engine.source_manager import get_latest_source
from core.scrapers.factory import Factory
from utils.file_io import get_log_names
from utils.file_io import read_log_content
from utils.logger import get_logger

legado_api = Blueprint("legado_api", __name__, url_prefix=config.API_PREFIX, template_folder="templates")

logger = get_logger()

SEARCH_ROUTE = "/search"
PROXY_ROUTE = "/proxy"


@legado_api.route("/", methods=["GET"])
def legado_api_index():
    logger.info(f"[{request.remote_addr}] >>> Request Index >> index.html")
    base_url = config.BASE_URL.rstrip("/")
    api_prefix = config.API_PREFIX.rstrip("/")
    source_url = f"{base_url}{api_prefix}/BookSource.json"
    return render_template("index.html", source_url=source_url)


@legado_api.route(SEARCH_ROUTE, methods=["GET"])
def legado_search():
    logger.info(f"[{request.remote_addr}] >>> Request Search >> {request.form}")
    url = request.values.get("url")
    keywords = request.values.get("keywords")
    if not url or not keywords:
        return {"Error": "Parameter Error", "Message": "Invalid Url Or Keywords", "Details": f"Url: {url}, Keywords: {keywords}"}, 400
    scraper = Factory.create(url, keywords)
    if not scraper:
        return {"Error": "Parameter Error", "Message": "Invalid Url Or Keywords", "Details": f"Url: {url}, Keywords: {keywords}"}, 400
    return scraper.search()


@legado_api.route(PROXY_ROUTE, methods=["GET"])
def legado_proxy():
    logger.info(f"[{request.remote_addr}] >>> Request Proxy >> {request.args}")
    url = request.values.get("url")
    if not url:
        return {"Error": "Parameter Error", "Message": "Invalid Url", "Details": f"Url: {url}"}, 400
    scraper = Factory.create(url)
    if not scraper:
        return {"Error": "Parameter Error", "Message": "Invalid Url", "Details": f"Url: {url}"}, 400
    response = scraper.proxy()
    if isinstance(response, bytes):
        image_res = make_response(response)
        image_res.headers.set("Content-Type", "image/jpeg")
        return image_res
    return response


@legado_api.route("/BookSource.json", methods=["GET"])
def legado_book_source():
    logger.info(f"[{request.remote_addr}] >>> Request BookSource >> BookSource.json")
    target_url = f"{config.BASE_URL}{config.API_PREFIX}"
    result = get_latest_source()
    result = result.replace("https://api.dancying.cn/legado/search", f"{target_url}{SEARCH_ROUTE}")
    result = result.replace("https://api.dancying.cn/legado/proxy", f"{target_url}{PROXY_ROUTE}")
    return result


@legado_api.app_errorhandler(404)
def handle_404(e):
    logger.warning(f"[{request.remote_addr}] >>> 404 Not Found >> {request.url}")
    site = request.form.get("site") or request.args.get("site")
    return render_template("404.html", url=request.url, site=site), 404


@legado_api.route("logs", methods=["GET"])
def legado_logs():
    logger.debug(f"[{request.remote_addr}] >>> Request Logs >> {request.args}")
    current_file = request.args.get('filename', 'novelservice.log')
    line_count = int(request.args.get('lines', 1000))
    log_files = get_log_names()
    logs = read_log_content(current_file, line_count)
    return render_template(
        'logs.html',
        logs=logs,
        log_files=log_files,
        current_file=current_file,
        line_count=line_count
    )
