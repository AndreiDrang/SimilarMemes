import datetime

from sqlalchemy import create_engine, update
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils.types.choice import ChoiceType

Base = declarative_base()

engine = create_engine('sqlite:///similar_memes.db')

Session = sessionmaker(bind=engine)

association_table = Table('association', Base.metadata,
    Column('association_image_id', Integer, ForeignKey('Image.id')),
    Column('association_tag_id', Integer, ForeignKey('Tag.id'))
)

class Image(Base):
    """
    Image model
    """
    __tablename__ = 'Image'
    # unique image ID
    id = Column(Integer, primary_key=True)
    # image creation datetime(in DB)
    image_creation = Column(DateTime(timezone=False), default=datetime.datetime.now)
    # image path
    image_path = Column(String(200))
    # image dhash
    image_dhash = Column(String(200))
    # image md5 hash
    image_md5_hash = Column(String(200), unique=True)
    # image tags
    image_tags = relationship('Tag', secondary=association_table, backref="images")
    
    def __init__(self, image_path, image_dhash, image_md5_hash):
        self.image_path = image_path
        self.image_dhash = image_dhash
        self.image_md5_hash = image_md5_hash

class Tag(Base):
    """
    Tag model
    """
    __tablename__ = 'Tag'
    # tag id
    id = Column(Integer, primary_key=True)
    # image tags
    tag_text = Column(String(20))
    # tag images list
    tag_images = relationship('Image', secondary=association_table, backref="tags")

    def __init__(self, tag_image: str):
        self.tag_image = tag_image

# create DB
Base.metadata.create_all(engine)

print("Все таблицы в БД успешно созданы")
