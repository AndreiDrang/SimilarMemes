import os
import json
import collections
from datetime import datetime

import numpy as np
from pony.orm import Required, Set, Database, select, composite_key, delete

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

    def full_path(self) -> str:
        """
        Method return full image path
        :return: String with image full path
        """
        return os.path.join(self.image_path, self.image_name)

    def custom_delete(self):
        """
        Custom image delete. Delete file from OS and image from database
        """
        try:
            os.remove(self.image_path + os.sep + self.image_name)
        except FileNotFoundError:
            pass
        # clean images duplicates
        delete(duplicate for duplicate in ImageDuplicates
               if duplicate.image_src_id == self.id
               or duplicate.image_dup.id == self.id)
        self.delete()

    @staticmethod
    def all() -> list:
        """
        Return all images data from DB
        """
        return select(image for image in Image)[:]

    @staticmethod
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

    def custom_delete(self):
        """
        Custom video delete. Delete file from OS and video from database
        """
        try:
            os.remove(self.image_path + os.sep + self.image_name)
        except FileNotFoundError:
            pass
        self.delete()

    @staticmethod
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


def connection():
    """
    Function get user custom DB connect params
    """
    with open("database/db_config.json", "rt") as configs:
        configs_data = json.loads(configs.read())

    if configs_data["provider"] == "sqlite":
        db.bind(provider="sqlite", filename=configs_data["filename"], create_db=True)
    elif configs_data["provider"] == "postgres":
        # bind to DB with provider and settings
        db.bind(
            provider="postgres",
            user=configs_data["user"],
            password=configs_data["password"],
            host=configs_data["host"],
            port=configs_data["port"],
            database=configs_data["database"],
            create_db=True,
        )
    elif configs_data["provider"] == "mysql":
        # bind to DB with provider and settings
        db.bind(
            provider="mysql",
            user=configs_data["user"],
            passwd=configs_data["password"],
            host=configs_data["host"],
            port=configs_data["port"],
            db=configs_data["database"],
            create_db=True,
        )

    db.generate_mapping(create_tables=True, allow_auto_upgrade=True)

    print("Все таблицы в БД успешно созданы")
