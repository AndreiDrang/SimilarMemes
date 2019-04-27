import collections

from database import Image, Video, ImageDuplicates, db_session, select


@db_session(retry=3)
def save_new_files(indexed_files: collections.defaultdict, file_type: str):
    """
    Function get files dict and files type and save it to DB

    :param indexed_files: Dict with all indexed files

    :param file_type: Files type - `image` or `video`
    """

    if file_type == "image":
        for _, image_data in indexed_files.items():
            # if current md5_hash not exist
            if not Image.get(image_md5_hash=image_data["md5_hash"]):
                Image(
                    image_name=image_data["namepath"][0],
                    image_path=image_data["namepath"][1],
                    image_orb_descriptor=image_data["orb_descriptor"],
                    image_md5_hash=image_data["md5_hash"],
                )

    elif file_type == "video":
        for _, video_data in indexed_files.items():
            # if current video+path not exist
            if not Video.get(video_path=video_data["namepath"][1]):
                Video(
                    video_name=video_data["namepath"][0],
                    video_path=video_data["namepath"][1],
                )


@db_session(retry=3)
def save_images_duplicates(pairs: collections.deque):
    """
    Function get image files list and save them to DB

    :param pairs: List of iamges ID's and images similarity, like:
                        (
                            (image_id, image_id, similarity),
                            (image_id, image_id, similarity),
                        )

    """
    for pair in pairs:
        # try select pair from already exist data
        image_duplicates = select(
            duplicate.id
            for duplicate in ImageDuplicates
            if duplicate.image_src_id in (pair[1], pair[0])
            and duplicate.image_dup.id in (pair[1], pair[0])
        )[:]
        # if current pair not exist
        if not image_duplicates:
            ImageDuplicates(
                image_src_id=pair[0],
                image_dup=Image[pair[1]],
                images_similarity=pair[2],
            )


@db_session(retry=3)
def get_image_duplicates(
    image_id: int, similarity_threshold: float
) -> [(Image, float)]:
    """
    Return list of Image-objects - duplicates of certain image

    :param image_id: ID of image to search it's duplicates
    :param similarity_threshold: Similarity threshold to images sorting

    :return: List of Images-objects and similarity param
    """
    # find image duplicates pairs which contains `image_id`
    duplicates = select(
        duplicate
        for duplicate in ImageDuplicates
        if (duplicate.image_src_id == image_id or duplicate.image_dup.id == image_id)
        and duplicate.images_similarity < similarity_threshold
    ).sort_by(ImageDuplicates.images_similarity)[:]

    # filter duplicates pairs and get only new(image!=src_image) images from pair
    duplicates_images = [
        (
            duplicate.image_src_id
            if duplicate.image_src_id != image_id
            else duplicate.image_dup.id,
            duplicate.images_similarity,
        )
        for duplicate in duplicates
    ]

    return [(Image[img_id], similarity) for img_id, similarity in duplicates_images]


@db_session(retry=3)
def group_image_files() -> dict:
    """
    Function group image files to dict with key - path, value - images in this path

    :return: Dict with path's and files
                {
                    <path name>: [
                        (<filename>, <image ID>),
                        (<filename>, <image ID>),
                    ],
                    <path name>: [
                        (<filename>, <image ID>),
                        (<filename>, <image ID>),
                    ]
                }
    """
    result = {}
    all_images_paths = Image.group_images_paths()
    for path in all_images_paths:
        path_files = select(
            (image.image_name, image.id) for image in Image if image.image_path == path
        )[:]
        result.update({path: path_files})

    return result


@db_session(retry=3)
def group_video_files() -> dict:
    """
    Function group video files to dict with key - path, value - video in this path

    :return: Dict with path's and files
                {
                    <path name>: [
                        (<filename>, <video ID>),
                        (<filename>, <video ID>),
                    ],
                    <path name>: [
                        (<filename>, <video ID>),
                        (<filename>, <video ID>),
                    ]
                }
    """
    result = {}
    all_video_paths = Video.group_video_paths()
    for path in all_video_paths:
        path_files = select(
            (video.video_name, video.id) for video in Video if video.video_path == path
        )[:]
        result.update({path: path_files})

    return result
