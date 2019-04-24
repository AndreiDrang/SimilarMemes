import collections
import itertools
import os

import cv2
import imageio

from .settings import get_settings


def feature_description(images_list: collections.deque) -> collections.deque:
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
    bf = cv2.BFMatcher()

    # similarity param
    SIMILARITY_PARAM = get_settings()["SIMILARITY_PARAM"]
    # match param
    MATCH_PARAM = get_settings()["MATCH_PARAM"]
    # make unique photo files combinations
    images_pairs = itertools.combinations(images_list, 2)
    # prepare pairs list
    feature_pairs = collections.deque()
    # prepare good point list
    good_points = collections.deque()
    
    for pair in images_pairs:
        # if first image is GIF
        if pair[0][0][-3:].lower()=='gif':
            # read gif
            gif = imageio.mimread(pair[0][1] + os.sep + pair[0][0])
            # get middle frame from gif
            first_image = gif[len(gif)//2]
        else:
            first_image = cv2.imread(pair[0][1] + os.sep + pair[0][0], 0)

        # if second image is GIF
        if pair[1][0][-3:].lower()=='gif':
            # read gif
            gif = imageio.mimread(pair[1][1] + os.sep + pair[1][0])
            # get middle frame from gif
            second_image = gif[len(gif)//2]
        else:
            second_image = cv2.imread(pair[1][1] + os.sep + pair[1][0], 0)

        _, descriptor_first = orb.detectAndCompute(first_image, None)
        _, descriptor_second = orb.detectAndCompute(second_image, None)

        # if detector not find any element on image - pass this pair
        if descriptor_first is not None and descriptor_second is not None:
            matches = bf.knnMatch(descriptor_first, descriptor_second, k=2)
            # find good points
            for m,n in matches:
                if m.distance < MATCH_PARAM*n.distance:
                    good_points.append(m)

            # sort images matches by distance, and get lowest 10 values(lower is better)
            match_sorted = sorted(good_points, key=lambda element: element.distance)

            LEN = 10 if len(match_sorted)>10 else len(match_sorted)
            # slice only few points
            match_sorted = match_sorted[:LEN]
            if match_sorted:
                # count summ of sorted matches and get distance average value
                average_match_value = sum(matching.distance for matching in match_sorted)//LEN
                # save hash different
                feature_pairs.append((pair[0][2], pair[1][2], average_match_value))

        good_points.clear()
    return feature_pairs
