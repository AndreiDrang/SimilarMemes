import collections
import itertools


def hamming_distance(hashes_list: list)->collections.deque:
    """
    Return the Hamming distance between equal-length sequences

    :param hashes_list: List contains hashes list:
                            0 - dhash
                            1 - md5 unique hash

    :return: List of pair with hamming distance param
    """
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
            # if dhahs different < 10 - images ar similar
            if diff<10:
                # get hash different
                hamming_pairs.append((pair, diff))

    return hamming_pairs
