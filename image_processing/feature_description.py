import collections
import itertools
from multiprocessing import Pool

import cv2
import time
from database import save_images_duplicates

from .settings import get_settings


def count_pairs(pair: tuple):
    # similarity threshold
    SIMILARITY_THRESHOLD = get_settings()["similarity_threshold"]
    # ratio param
    LOWE_RATIO = get_settings()["lowe_ratio"]
    # create matcher
    bf = cv2.BFMatcher()
    # prepare deque for points matching
    good_points = collections.deque()

    # count matches between two images descriptors
    matches = bf.knnMatch(pair[0][0], pair[1][0], k=2)
    # find best matched images points
    for m, n in matches:
        if m.distance < LOWE_RATIO * n.distance:
            good_points.append(m)

    # sort images matches by distance, and get lowest 10 values(lower is better)
    match_sorted = sorted(good_points, key=lambda element: element.distance)

    LEN = 10 if len(match_sorted) > 10 else len(match_sorted)
    # slice only few points
    match_sorted = match_sorted[:LEN]
    if match_sorted:
        # count summ of sorted matches and get distance average value
        average_match_value = sum(matching.distance for matching in match_sorted) // LEN
        # if average different is less than threashold - add pair
        if average_match_value <= SIMILARITY_THRESHOLD * 1.2:
            # create new pair
            return pair[0][1], pair[1][1], average_match_value


def feature_description(images_list: collections.deque):
    """
    Return the Hamming distance between equal-length sequences

    :param images_list: Tuple of lists contains image ORB descriptor and ID:
                            0 - image descriptor
                            1 - image ID
                        Example:
                        (
                            (image_descriptor, image_id),
                        )
    """
    # make unique photo files combinations
    images_pairs = itertools.combinations(images_list, 2)

    pool = Pool()
    # run tasks in separate process
    pairs = pool.map(count_pairs, images_pairs)

    # filter only indexed files
    similar_pairs = [pair for pair in pairs if pair is not None]

    save_images_duplicates(pairs=similar_pairs)
