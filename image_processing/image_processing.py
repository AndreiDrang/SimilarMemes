import collections
import hashlib
import os

import cv2
import imageio
import numpy as np


def image_processing(image_list: collections.deque) -> collections.defaultdict:
    """
    Function preprocess image files, count hash, count images descriptor(using ORB)
        and return files info in dict format

    :param image_list: List of images in folder
                        0 - files name
                        1 - file full path

    :return: Dict of parsed images
    """
    # prepare result dict
    result_image_dict = collections.defaultdict()
    # prepare ORB to count images descriptor
    orb = cv2.ORB_create()

    for index, image_file in enumerate(image_list):

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
            # if orb_descriptor find too few points - pass this image
            if orb_descriptor.shape[0] < 2:
                continue
            # write result to dict
            result_image_dict.update(
                {
                    index: {
                        "namepath": image_file,
                        "orb_descriptor": orb_descriptor.tobytes(),
                        "md5_hash": hashlib.md5(
                            (image_file[1] + os.sep + image_file[0]).encode()
                        ).hexdigest(),
                    }
                }
            )

    return result_image_dict
