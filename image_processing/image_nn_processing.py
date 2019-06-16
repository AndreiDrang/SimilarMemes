import os
import hashlib
import collections
import traceback
from multiprocessing.dummy import Pool

from keras.applications.mobilenet import MobileNet
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
import numpy as np

model = MobileNet(weights='imagenet', include_top=False)
model._make_predict_function()


def count_descriptor(image_file):
    try:
        # read and resize image
        img = image.load_img(image_file[1] + os.sep + image_file[0], target_size=(299, 299))
        img = image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)

        features = model.predict(img)
        # create one array
        features = np.array(features)
        features = features.flatten()
        # Normalize array data
        features = features / np.linalg.norm(features)

        # check if image_features_keys is counted
        if type(features) == np.ndarray:
            return {
                "height": 0,
                "width": 0,
                "namepath": image_file,
                "image_nn_descriptor": features.tobytes(),
                "image_features_keys": b'',
                "md5_hash": hashlib.md5(
                    (image_file[1] + os.sep + image_file[0]).encode()
                ).hexdigest(),
            }
    except Exception:
        print(traceback.format_exc())
        return None


def image_nn_processing(image_list: collections.deque) -> list:
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
