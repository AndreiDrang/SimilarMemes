import collections
import itertools
import os

import cv2

from .settings import get_settings


def feature_description(images_list: collections.deque) -> collections.deque:
    """
    Return the Hamming distance between equal-length sequences

    :param images_list: Tuple of lists contains image ORB descriptor and ID:
                            0 - image descriptor
                            1 - image ID
                        Example:
                        (
                            (image_descriptor, image_id),
                        )

    :return: List of pairs with good feature descriptors values
                Example:
                (
                    (first_image_id, second_image_id, average_match_value)
                )
    """
    bf = cv2.BFMatcher()

    # similarity threshold
    SIMILARITY_THRESHOLD = get_settings()["similarity_threshold"]
    # ratio param
    LOWE_RATIO = get_settings()["lowe_ratio"]
    # make unique photo files combinations
    images_pairs = itertools.combinations(images_list, 2)
    # prepare pairs list
    feature_pairs = collections.deque()
    # prepare good point list
    good_points = collections.deque()
    
    for pair in images_pairs:
        # count mathches between two images descriptors
        matches = bf.knnMatch(pair[0][0], pair[1][0], k=2)
        # find best matched images points
        for m,n in matches:
            if m.distance < LOWE_RATIO*n.distance:
                good_points.append(m)

        # sort images matches by distance, and get lowest 10 values(lower is better)
        match_sorted = sorted(good_points, key=lambda element: element.distance)

        LEN = 10 if len(match_sorted)>10 else len(match_sorted)
        # slice only few points
        match_sorted = match_sorted[:LEN]
        if match_sorted:
            # count summ of sorted matches and get distance average value
            average_match_value = sum(matching.distance for matching in match_sorted)//LEN
            # if average different is less than threashold - add pair
            if average_match_value <= SIMILARITY_THRESHOLD*1.2:
                # create new pair
                feature_pairs.append((pair[0][1], pair[1][1], average_match_value))

        good_points.clear()
    return feature_pairs
