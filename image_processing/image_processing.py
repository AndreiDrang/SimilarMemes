import collections
import hashlib

import imagehash
from PIL import Image as PIL_Img


def image_processing(image_list: collections.deque, path: str)->collections.defaultdict:
    """
    Function preprocess image files, count hash, dhash and return files info in dict format

    :param image_list: List of images in folder
    :param path: To folder with files

    :return: Dict of parsed images
    """
    # prepare result dict
    result_image_dict = collections.defaultdict()

    for image_file in image_list:
        # open image
        img = PIL_Img.open(path+image_file)
        # resize image to 20*19 format
        img.thumbnail(size=(9,8))
        img.convert('LA')
        # get image hash
        hash_result = str(imagehash.dhash(img))

        result_image_dict.update({
                                    image_file: {
                                        'name': image_file,
                                        'dhash': hash_result,
                                        'md5_hash': hashlib.md5(image_file.encode()).hexdigest(),
                                    }
                                })
    print(len(result_image_dict),' - Images processed.')
    
    return result_image_dict