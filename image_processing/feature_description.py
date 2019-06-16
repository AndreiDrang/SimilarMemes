import itertools
from multiprocessing import Pool

from scipy import spatial

from .settings import get_settings

pairs_threshold = 25
knn_r = 4


def count_pairs(pair: tuple):
    result = pair[0][0].count_neighbors(pair[1][0], r=knn_r)

    # if pairs amount more than threshold - create duplicate
    if result >= pairs_threshold:
        return pair[0][1], pair[1][1], round(result/pairs_threshold, 2)


def count_nn_pairs(pair: tuple):
    # similarity threshold
    NN_SIMILARITY_THRESHOLD = get_settings()["nn_similarity_threshold"]

    # count matches between two images descriptors
    math_value = round(pair[0][0] @ pair[1][0], 3)

    # if match value greater than threshold - pair is valid
    if math_value >= NN_SIMILARITY_THRESHOLD:
        # create new pair
        return pair[0][1], pair[1][1], math_value


def feature_description(images_list: tuple, count_type: str = 'kps'):
    """
    Return the Hamming distance between equal-length sequences

    :param images_list: Tuple of lists contains image ORB descriptor and ID:
                            0 - image descriptor
                            1 - image ID
                        Example:
                        (
                            (image_descriptor, image_id),
                        )
    :param count_type: Similarity count type, available variants - `nn` and `kps`;
                        If use `nn` - must send `image_nn_descriptor` from image model
                        If use `kps` - must send `image_features_keys` from image model
    """

    pool = Pool()

    if count_type.lower() == 'nn':
        images_pairs = itertools.combinations(images_list, 2)
        # run tasks in separate process
        pairs = pool.map(count_nn_pairs, images_pairs)
    elif count_type.lower() == 'kps':
        # create cKDTree`s with images points
        trees = [(spatial.cKDTree(data=image_data[0]), image_data[1]) for image_data in images_list]
        images_pairs = itertools.combinations(trees, 2)
        # run tasks in separate process
        pairs = pool.map(count_pairs, images_pairs)
    else:
        raise ValueError('Wrong `count_type` send.')

    # filter only indexed files
    similar_pairs = [pair for pair in pairs if pair is not None]

    return similar_pairs
