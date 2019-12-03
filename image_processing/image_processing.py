import os
import hashlib
import logging
import collections
import traceback
from multiprocessing import Pool

import cv2
import imageio
import numpy as np

from .color_descriptor import ColorDescriptor
from .settings import CPUS


logger = logging.getLogger(__name__)

module = ColorDescriptor((8, 12, 3))


def count_descriptor(image_file):
    try:
        # if image is GIF
        if image_file[0][-3:].lower() == "gif":
            # read gif
            gif = imageio.mimread(image_file[1] + os.sep + image_file[0])
            # get middle frame from gif
            image = gif[len(gif) // 2]
        else:
            image = cv2.imread(image_file[1] + os.sep + image_file[0])

        # if read image success
        if image is not None:
            # get image params
            height, width, _ = image.shape
            features = np.array(module.describe(image=image), dtype=np.float32)
            return {
                "height": height,
                "width": width,
                "namepath": image_file,
                "image_descriptor": features.tobytes(),
                "md5_hash": hashlib.md5(
                    (image_file[1] + os.sep + image_file[0]).encode()
                ).hexdigest(),
            }
        else:
            logger.warning(
                f"Can`t read image while `count_descriptor`, full path - {image_file[1] + os.sep + image_file[0]}"
            )
            return None
    except Exception:
        logger.error(traceback.format_exc())
        print(traceback.format_exc())
        return None


def image_processing(image_list: collections.deque) -> list:
    """
    Function preprocess image files, count hash, count images descriptor(using ORB)
    and return files info in dict format

    :param image_list: List of images in folder
                        0 - files name
                        1 - file full path
    :return: Dict of parsed images and images data
    """
    processed_files = []
    try:
        with Pool(processes=CPUS-1) as pool:
            # run tasks in separate process
            res = pool.map(count_descriptor, image_list)

        # filter only indexed files
        processed_files = [file for file in res if file is not None]
    except Exception:
        logger.critical(traceback.format_exc())
    finally:
        return processed_files
