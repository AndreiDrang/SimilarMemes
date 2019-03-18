import collections
import itertools
import os

import cv2

from .settings import get_settings


def feature_description(images_list: collections.deque)->collections.deque:
    """
    Return the Hamming distance between equal-length sequences

    :param images_list: List of two lists contains images name and path:
                            0 - image name
                            1 - image path
                        Example:
                        (
                            (image_name, image_path, image_id),
                            (image_name, image_path, image_id)
                        )

    :return: List of pairs with good feature descriptors values
                Example:
                (
                    (first_image_id, second_image_id, average_match_value)
                )
    """
    orb = cv2.ORB_create()
    # BFMatcher with default params
    bf_match = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    # read param
    FEATURE_PARAM = get_settings()['feature_description']
    # make unique photo files combinations
    images_pairs = itertools.combinations(images_list, 2)
    # prepare
    feature_pairs = collections.deque()

    for pair in images_pairs:
        # get hash values for images in pair
        first_image = cv2.imread(pair[0][1]+os.sep+pair[0][0], 0)
        second_image = cv2.imread(pair[1][1]+os.sep+pair[1][0], 0)

        _, descriptor_first = orb.detectAndCompute(first_image, None)
        _, descriptor_second = orb.detectAndCompute(second_image, None)
        
        # count matches between two images
        match = bf_match.match(descriptor_first, descriptor_second)
        # sort images matches by distance, and get lowest 10 values(lower is better)
        match_sorted = sorted(match, key=lambda element: element.distance)[:10]

        #print(match_sorted[0].distance)
        average_match_value = sum(matching.distance for matching in match_sorted)//10
        
        if average_match_value < FEATURE_PARAM:
            # save hash different
            feature_pairs.append((pair[0][2], pair[1][2], average_match_value))

    return feature_pairs
