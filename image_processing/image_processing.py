import collections
import hashlib
import os

from PIL import Image as PIL_Img


def image_processing(image_list: collections.deque) -> collections.defaultdict:
    """
    Function preprocess image files, count hash and return files info in dict format

    :param image_list: List of images in folder
                        0 - files name
                        1 - file full path

    :return: Dict of parsed images
    """
    # prepare result dict
    result_image_dict = collections.defaultdict()

    for index, image_file in enumerate(image_list):
        # open image
        img = PIL_Img.open(image_file[1] + os.sep + image_file[0])
        # resize image to 20*19 format
        img.thumbnail(size=(9, 8))
        img.convert("LA")

        result_image_dict.update(
            {
                index: {
                    "namepath": image_file,
                    "md5_hash": hashlib.md5(
                        (image_file[1] + os.sep + image_file[0]).encode()
                    ).hexdigest(),
                }
            }
        )

    return result_image_dict
