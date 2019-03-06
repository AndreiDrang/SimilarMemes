import collections
from datetime import datetime

from pony.orm import *

db = Database()

db.bind(provider='postgres', 
        user='similar_memes',
        password='veryhardpass',
        host='85.255.8.26',
        #host='localhost',
        database='similar_memes_db')


class Image(db.Entity):
    """
    Image model
    """

    _table_ = 'Image'

    # image path
    image_path = Required(str, unique=True)
    # image name
    image_name = Required(str)
    # image dhash
    image_dhash = Required(str)
    # image md5 hash
    image_md5_hash = Required(str)
    # image creation datetime(in DB)
    image_creation = Required(datetime, default=datetime.now)
    # image tags
    image_tags = Set('ImageTag', nullable=True)
    # image duplicates
    image_duplicates = Set('ImageDuplicates', nullable=True)

    composite_key(image_path, image_md5_hash)

    @staticmethod
    @db_session(retry=3)
    def get_dhash_id()->collections.deque:
        return collections.deque(select((image.image_dhash, image.id) for image in Image)[:])

class Video(db.Entity):
    """
    Video model
    """

    _table_ = 'Video'

    # video path
    video_path = Required(str, unique=True)
    # video name
    video_name = Required(str)
    # video tags
    video_tags = Set('VideoTag', nullable=True)
    # video duplicates
    video_duplicates = Set('VideoDuplicates', nullable=True)


class ImageTag(db.Entity):
    """
    Image tag model
    """

    _table_ = 'Image_Tag'
    
    # image tags
    tag_text = Required(str, max_len=40)
    # tag images list
    tag_images = Set(Image, nullable=True)


class VideoTag(db.Entity):
    """
    Video tag model
    """

    _table_ = 'Video_Tag'
    
    # image tags
    tag_text = Required(str, max_len=40)
    # tag video list
    tag_video = Set(Video, nullable=True)


class ImageDuplicates(db.Entity):
    """
    Duplicates model
    """

    _table_ = 'Images_Duplicates'
    
    # bounded image id
    image_hamming_id = Required(int)
    # hamming distance param
    images_hamming_distance = Required(int)
    # images duplicates
    image_duplicates = Set(Image)


class VideoDuplicates(db.Entity):
    """
    Duplicates model
    """

    _table_ = 'Video_Duplicates'
    
    # video duplicates
    video_duplicates = Set(Video)


db.generate_mapping(create_tables=True)

print("Все таблицы в БД успешно созданы")
