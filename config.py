from pathlib import Path

# Basic path settings
PROJECT_ROOT = Path(__file__).resolve().parent
RES_DIR = PROJECT_ROOT / "res"
TEMP_DIR = PROJECT_ROOT / "temp"
COOKIES_DIR = TEMP_DIR / "cookies"
LOGS_DIR = TEMP_DIR / "logs"
BROWSER_PROFILE_DIR = TEMP_DIR / "profile"

# Logs settings
LOGS_LEVEL = "INFO"
LOGS_FORMAT = "%(asctime)s | %(levelname)-8s | PID:%(process)d | %(module)-18s:%(lineno)-3d - %(message)s"

# Browser cdp settings
BROWSER_CDP_HOST = "http://localhost"
BROWSER_CDP_PORT = 9222

# Deploy settings
BASE_URL = "https://api.dancying.cn"
API_PREFIX = "/legado"
