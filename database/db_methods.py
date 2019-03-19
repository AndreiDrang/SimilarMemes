import collections

from database import Image, ImageTag, Video, ImageDuplicates, db_session, select


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
            (duplicate.image_id, image.id)
            for duplicate in ImageDuplicates
            for image in Image
            if duplicate.image_id in (pair[1], pair[0])
            and image.id in (pair[1], pair[0])
        )[:]
        # if current pair not exist
        if not image_duplicates:
            Image[pair[0]].duplicates.create(
                image_id=pair[1], images_similarity=pair[2]
            )
