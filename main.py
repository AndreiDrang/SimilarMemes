import time
import collections
import sqlite3

import sqlalchemy
from image_processing import hamming_distance
from model import Image, Tag, Session
from indexing import index_folder_files, index_folders
from image_processing import image_processing


#path = '/home/andrei/Downloads/Telegram Desktop/DataExport_06_12_2018/chats/chat_001/photos/'
#path = '/home/andrei/Pictures/'
path = '/home/andrei/Documents/My Drawings/'

def save_files(indexed_files: collections.defaultdict, file_type: str):
    """
    Function get files dict and files type and save it to DB

    :param indexed_files: Dict with all indexed files

    :param file_type: Files type - `image` or `video`
    """
    session = Session()

    try:
        if file_type=='image':
            for _, image_data in indexed_files.items():
                session.add(Image(image_path=path+image_data['name'],
                                  image_dhash=image_data['dhash'],
                                  image_md5_hash=image_data['md5_hash'])
                                 )

            print('Image saved to DB')
        elif file_type=='video':
            print('Save video files to DB')

        session.commit()

    except Exception as err:
        print(err)
    finally:
        session.close()

start_time = time.time()

# get photo and video files lists
image_files_list, video_files_list = index_folder_files(path=path)

# parse images and get dict
result_image_dict = image_processing(image_files_list, path)

print('Images pairs list created')

# save all images to DB
#save_files(result_image_dict, 'image')


# count hamming_distance betwen images hash
hamming_pairs = hamming_distance(images_dict=result_image_dict)


print(f'Needed time for {len(result_image_dict)} images - {time.time()-start_time}')

