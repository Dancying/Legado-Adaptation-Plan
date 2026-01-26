import os.path
import platform
import subprocess
import time

import requests
from filelock import FileLock

import config
from utils.logger import get_logger

logger = get_logger()
os_name = platform.system()


def launch_browser_with_cdp() -> None:
    with (FileLock(os.path.join(config.TEMP_DIR, "launch_browser_with_cdp.lock"), timeout=30)):
        if get_cdp_version():
            return None
        browser_path_mapping = {
            "Windows": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "Linux": r"/usr/bin/microsoft-edge-stable",
        }
        executable_path = browser_path_mapping.get(os_name)
        command = [
            executable_path,
            f"--remote-debugging-port={config.BROWSER_CDP_PORT}",
            f"--user-data-dir={config.BROWSER_PROFILE_DIR}",
            "--window-size=800,600",
            "--disable-extensions",
            "--disable-sync",
            "--no-first-run",
            "--disable-infobars",
            "--disable-gpu",
            "--no-session-restore",
            "--disable-session-crashed-bubble",
            "--mute-audio",
            "--disable-background-networking",
            "--no-default-browser-check",
            "--safeBrowse-disable-auto-update",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--enable-unsafe-swiftshader",
        ]
        if os_name == "Linux":
            command = ["xvfb-run", "-a", "--server-args=-screen 0 800x600x24"] + command
        logger.info(f"Starting browser service on port {config.BROWSER_CDP_PORT}...")
        subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(15):
            time.sleep(1)
            if get_cdp_version():
                logger.info("Browser CDP Service Ready.")
                return None
        logger.error("Browser startup timeout: CDP service not responding.")
    return None


def close_browser_service() -> None:
    logger.info(f"Terminating browser service on port {config.BROWSER_CDP_PORT}...")
    try:
        if os_name == "Windows":
            cmd = f"netstat -ano | findstr :{config.BROWSER_CDP_PORT}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            pids = {line.split()[-1] for line in result.stdout.strip().split('\n') if len(line.split()) > 4}
            for pid in pids:
                subprocess.run(["taskkill", "/F", "/PID", pid],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
        else:
            subprocess.run(["fuser", "-k", f"{config.BROWSER_CDP_PORT}/tcp"],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        logger.info("Browser service terminated.")
    except Exception as e:
        logger.error(f"Terminate Failed: {e}")
    return None


def get_cdp_version() -> dict:
    version_info_url = f"{config.BROWSER_CDP_HOST}:{config.BROWSER_CDP_PORT}/json/version"
    try:
        response = requests.get(version_info_url, timeout=2)
        version_info = response.json()
        logger.debug(f"CDP Version Verified: {version_info.get('Browser')}")
        return version_info
    except (requests.exceptions.RequestException, Exception):
        logger.warning("CDP Service Offline.")
    return {}
