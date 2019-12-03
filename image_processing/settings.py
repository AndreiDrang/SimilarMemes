import os
import json
import logging
import traceback
from multiprocessing import cpu_count


logger = logging.getLogger(__name__)

CPUS = cpu_count()


def get_settings() -> dict:
    """
    Function open settings.json file and read data.

    :return: Dict with params from file
    """
    try:
        with open(f"image_processing{os.sep}settings.json", "r") as settings_file:
            settings_data = json.loads(settings_file.read())

        return settings_data
    except Exception:
        logger.critical(traceback.format_exc())
