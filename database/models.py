import collections
from datetime import datetime

import numpy as np
from pony.orm import Required, Set, Database, db_session, select, composite_key

db = Database()


class Image(db.Entity):
    """
    Image model
    """

    _table_ = "Image"

    # image path
    image_path = Required(str)
    # image name
    image_name = Required(str)
    # image md5 hash
    image_md5_hash = Required(str, unique=True)
    # image ORB descriptor
    image_orb_descriptor = Required(bytes)
    # image creation datetime(in DB)
    image_creation = Required(datetime, default=datetime.now)
    # image tags
    image_tags = Set("ImageTag", nullable=True)
    # image duplicates
    duplicates = Set("ImageDuplicates", nullable=True)

    composite_key(image_path, image_md5_hash)

    @staticmethod
    @db_session(retry=3)
    def get_images_descriptors() -> [(np.ndarray, int)]:
        """
        Return all images descriptors and ID's
        """
        result = collections.deque(
            select((image.image_orb_descriptor, image.id) for image in Image)[:]
        )
        # restore descriptor from bytes
        frombuffer_result = [
            (np.frombuffer(descriptor, dtype=np.uint8), id_)
            for descriptor, id_ in result
        ]
        # reshape descriptor in src shape - (x, 32)
        reshaped_result = [
            (descriptor.reshape((descriptor.shape[0] // 32, 32)), id_)
            for descriptor, id_ in frombuffer_result
        ]

        return reshaped_result

    @staticmethod
    @db_session(retry=3)
    def group_images_paths() -> collections.deque:
        """
        Return unique paths from Images
        """
        return collections.deque(select(image.image_path for image in Image)[:])


class Video(db.Entity):
    """
    Video model
    """

    _table_ = "Video"

    # video path
    video_path = Required(str)
    # video name
    video_name = Required(str)
    # video tags
    video_tags = Set("VideoTag", nullable=True)
    # video duplicates
    video_duplicates = Set("VideoDuplicates", nullable=True)

    @staticmethod
    @db_session(retry=3)
    def group_video_paths() -> collections.deque:
        """
        Return unique paths from Video
        """
        return collections.deque(select(video.video_path for video in Video)[:])


class ImageTag(db.Entity):
    """
    Image tag model
    """

    _table_ = "Image_Tag"

    # image tags
    tag_text = Required(str, max_len=40)
    # tag images list
    tag_images = Set(Image, nullable=True)


class VideoTag(db.Entity):
    """
    Video tag model
    """

    _table_ = "Video_Tag"

    # image tags
    tag_text = Required(str, max_len=40)
    # tag video list
    tag_video = Set(Video, nullable=True)


class ImageDuplicates(db.Entity):
    """
    Duplicates model
    """

    _table_ = "Images_Duplicates"

    # source image
    image_src_id = Required(int)
    # src image duplicate
    image_dup = Required(Image)
    # similarity param
    images_similarity = Required(float)


class VideoDuplicates(db.Entity):
    """
    Duplicates model
    """

    _table_ = "Video_Duplicates"

    # video duplicates
    video_duplicates = Set(Video)


def connection(
    provider: str = "sqlite",
    settings: dict = {"filename": "memes.sqlite", "create_db": True},
):
    """
    Function get user custom DB connect params

    :param provider: DB type, available variants - `sqlite / postgres / mysql`
    :param settings: Dict with connection params; 
                        For `sqlite` - {
                                        filename: <DB file name>, 
                                        create_db: <True - create new DB file; False - connect to exist DB file>
                                       }
                        For `postgres` - {
                                            user: <User name>, 
                                            password: <User password>,
                                            host: <Host addres>
                                            database: <DB name>
                                        }
                        For `mysql` - {
                                        user: <User name>, 
                                        passwd: <User password>,
                                        host: <Host addres>
                                        db: <DB name>
                                      }
    """
    # bind to DB with provider and settings
    db.bind(provider=provider, **settings)
    db.generate_mapping(create_tables=True)

    print("Все таблицы в БД успешно созданы")
