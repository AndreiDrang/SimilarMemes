import collections
import itertools

import numpy as np

def hamming_distance(images_dict: collections.defaultdict)->collections.deque:
    """
    Return the Hamming distance between equal-length sequences

    :param images_dict: Dict with full image info

    :return: List of pair with hamming distance param
    """
    # make unique photo files combinations
    images_pairs = itertools.combinations(images_dict, 2)

    hamming_pairs = collections.deque()
    
    for pair in images_pairs:
        # get hash values for images in pair
        first_hash = images_dict[pair[0]]['dhash']
        second_hash = images_dict[pair[1]]['dhash']

        if len(first_hash) != len(second_hash):
            print("Undefined for sequences of unequal length")
        else:
            # get hash different
            hamming_pairs.append((pair, sum(element_1 != element_2 for element_1, element_2 in zip(first_hash, second_hash))))

    return hamming_pairs
