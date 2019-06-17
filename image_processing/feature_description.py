import itertools
from multiprocessing import Pool

import numpy as np

from .settings import get_settings

similarity_threshold = get_settings()["similarity_threshold"]


def count_pairs(pair: tuple):
    mean = round(
        np.array([z1 @ z2 for z1, z2 in zip(pair[0][0], pair[1][0])]).mean(), 3
    )
    # if pairs amount more than threshold - create duplicate
    if mean >= similarity_threshold:
        return pair[0][1], pair[1][1], mean


def feature_description(images_list: tuple) -> list:
    """
    Return the Hamming distance between equal-length sequences

    :param images_list: Tuple of lists contains image ORB descriptor and ID:
                            0 - image descriptor
                            1 - image ID
                        Example:
                        (
                            (image_descriptor, image_id),
                        )
    :return: List of similar images pairs:
            0 - first similar image ID
            1 - second similar image ID
            2 - images similarity
            Example:
            [
                (first_image_id, second_image_id, similarity),
            ]
    """

    images_pairs = itertools.combinations(images_list, 2)

    pool = Pool()

    # run tasks in separate process
    pairs = pool.map(count_pairs, images_pairs)

    # filter only indexed files
    similar_pairs = [pair for pair in pairs if pair is not None]

    return similar_pairs
