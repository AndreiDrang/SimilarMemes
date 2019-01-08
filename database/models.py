from datetime import datetime

from pony.orm import *

db = Database()

db.bind(provider='sqlite', filename='./database.sqlite', create_db=True)



class Image(db.Entity):
    """
    Image model
    """
    # image path
    image_path = Required(str, unique=True)
    # image dhash
    image_dhash = Required(str)
    # image md5 hash
    image_md5_hash = Required(str, unique=True)
    # image creation datetime(in DB)
    image_creation = Required(datetime, default=datetime.now)
    # image tags
    #image_tags = relationship('Tag', secondary=association_table, backref="images")
        
    @staticmethod
    @db_session   
    def insert_new(image_path, image_dhash, image_md5_hash):
        if Image.get(image_md5_hash=image_md5_hash):
            return False
        else:
            Image(image_path=image_path,
                  image_dhash=image_dhash,
                  image_md5_hash=image_md5_hash)
            return True

db.generate_mapping(create_tables=True)
