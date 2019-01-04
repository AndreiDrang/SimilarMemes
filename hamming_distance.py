def hamming_distance(first_hash: str, second_hash: str)->int:
    """
    Return the Hamming distance between equal-length sequences
    """
    if len(first_hash) != len(second_hash):
        raise ValueError("Undefined for sequences of unequal length")
    return sum(el1 != el2 for el1, el2 in zip(first_hash, second_hash))
