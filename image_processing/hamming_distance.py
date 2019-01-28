import collections
import itertools

from .settings import get_settings


def hamming_distance(hashes_list: collections.deque)->collections.deque:
    """
    Return the Hamming distance between equal-length sequences

    :param hashes_list: List contains hashes and DB image ID list:
                            0 - dhash
                            1 - image unique ID

    :return: List of pair with hamming distance param
    """
    HAMMING_PARAM = get_settings()['hamming_param']
    # make unique photo files combinations
    images_pairs = itertools.combinations(hashes_list, 2)

    hamming_pairs = collections.deque()
    
    for pair in images_pairs:
        # get hash values for images in pair
        first_hash = pair[0][0]
        second_hash = pair[1][0]

        if len(first_hash) != len(second_hash):
            print("Undefined for sequences of unequal length")
        else:
            # count dhash different
            diff = sum(element_1 != element_2 for element_1, element_2 in zip(first_hash, second_hash))
            # if dhahs different < HAMMING_PARAM(presetted param) - images ar similar
            if diff<HAMMING_PARAM:
                # save hash different
                hamming_pairs.append((pair, diff))

    return hamming_pairs
