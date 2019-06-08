import os
import hashlib
import collections
from multiprocessing import Pool

import cv2
import imageio
import numpy as np

from database import save_new_files


def count_descriptor(image_file):
    orb = cv2.ORB_create()

    # if image is GIF
    if image_file[0][-3:].lower() == "gif":
        # read gif
        gif = imageio.mimread(image_file[1] + os.sep + image_file[0])
        # get middle frame from gif
        image = gif[len(gif) // 2]
    else:
        image = cv2.imread(image_file[1] + os.sep + image_file[0], 0)

    # count image descriptor
    _, orb_descriptor = orb.detectAndCompute(image, None)

    # check if orb_descriptor is counted
    if type(orb_descriptor) == np.ndarray:
        # if orb_descriptor find many points - save them
        if orb_descriptor.shape[0] > 2:
            return {
                "namepath": image_file,
                "orb_descriptor": orb_descriptor.tobytes(),
                "md5_hash": hashlib.md5(
                    (image_file[1] + os.sep + image_file[0]).encode()
                ).hexdigest(),
            }
    return None


def image_processing(image_list: collections.deque):
    """
	Function preprocess image files, count hash, count images descriptor(using ORB)
		and return files info in dict format

	:param image_list: List of images in folder
						0 - files name
						1 - file full path
	"""
    pool = Pool()
    # run tasks in separate process
    res = pool.map(count_descriptor, image_list)

    # filter only indexed files
    indexed_files = [file for file in res if file is not None]

    save_new_files(indexed_files=indexed_files, file_type="image")
