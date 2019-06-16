import os
import hashlib
import collections
import traceback
from multiprocessing import Pool

import cv2
import imageio
import numpy as np


def count_descriptor(image_file):
    vector_size = 64
    try:
        module = cv2.AKAZE_create()

        # if image is GIF
        if image_file[0][-3:].lower() == "gif":
            # read gif
            gif = imageio.mimread(image_file[1] + os.sep + image_file[0])
            # get middle frame from gif
            image = gif[len(gif) // 2]
            # get gif params
            height, width, _ = image.shape
        else:
            image = cv2.imread(image_file[1] + os.sep + image_file[0], 0)

            # get image params
            height, width = image.shape
        # resize image
        image = cv2.resize(image, (250, 250))
        image = image[25:250-25, 25:250-25]
        # detect key-points
        kps = module.detect(image)
        # if we found enough key-points
        if len(kps) >= vector_size:
            kps = sorted(kps, key=lambda x: -x.response)[:vector_size]

            points_data = np.array([point.pt for point in kps])
            return {
                "height": height,
                "width": width,
                "namepath": image_file,
                "image_nn_descriptor": b'',
                "image_features_keys": points_data.tobytes(),
                "md5_hash": hashlib.md5(
                    (image_file[1] + os.sep + image_file[0]).encode()
                ).hexdigest(),
            }
        else:
            return {
                "height": height,
                "width": width,
                "namepath": image_file,
                "image_nn_descriptor": b'',
                "image_features_keys": b'',
                "md5_hash": hashlib.md5(
                    (image_file[1] + os.sep + image_file[0]).encode()
                ).hexdigest(),
            }
    except Exception:
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
    pool = Pool()
    # run tasks in separate process
    res = pool.map(count_descriptor, image_list)

    # filter only indexed files
    processed_files = [file for file in res if file is not None]

    return processed_files
