import collections
import itertools

import cv2

from .settings import get_settings


def feature_description(images_list: collections.deque)->collections.deque:
    """
    Return the Hamming distance between equal-length sequences

    :param images_list: List contains images name and path:
                            0 - image name
                            1 - image path

    :return: List of pair with good feature descriptors values
    """
    orb = cv2.ORB_create()
    # read param
    FEATURE_PARAM = get_settings()['feature_description']
    # make unique photo files combinations
    images_pairs = itertools.combinations(images_list, 2)
    # prepare
    feature_pairs = collections.deque()

    for pair in images_pairs:
        # get hash values for images in pair
        first_image = cv2.imread(pair[0][1], 0)
        second_image = cv2.imread(pair[1][1], 0)

        _, descriptor_first = orb.detectAndCompute(first_image, None)
        _, descriptor_second = orb.detectAndCompute(second_image, None)

        bf_match = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        # count matches between two images
        match = bf_match.match(descriptor_first, descriptor_second)
        if len(match) > FEATURE_PARAM:
            print(len(match))
            print(pair)
            # save hash different
            feature_pairs.append(pair)

    return feature_pairs
