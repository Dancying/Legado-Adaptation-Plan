import json
import os.path

import config
from utils.file_io import read_json
from utils.logger import get_logger

logger = get_logger()


def get_latest_source() -> str:
    source_dir = config.RES_DIR
    source_jsons = []
    for filename in os.listdir(source_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(source_dir, filename)
            logger.info(f"Reading BookSource : {filepath}")
            source_jsons.append(read_json(filepath))
    source_jsons.sort(key=lambda item: item.get("customOrder", float("inf")))
    return json.dumps(source_jsons, indent=4, sort_keys=True, ensure_ascii=False)
