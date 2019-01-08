import time
import collections
import sqlite3

import sqlalchemy
from image_processing import hamming_distance
from indexing import index_folder_files, folders_files_walk
from image_processing import image_processing
from database import Image


#path = '/home/andrei/Downloads/Telegram Desktop/DataExport_06_12_2018/chats/chat_001/photos/'
#path = '/home/andrei/Pictures/'
path = '/home/andrei/Pictures'

def save_files(indexed_files: collections.defaultdict, file_type: str):
    """
    Function get files dict and files type and save it to DB

    :param indexed_files: Dict with all indexed files

    :param file_type: Files type - `image` or `video`
    """

    try:
        if file_type=='image':
            for _, image_data in indexed_files.items():
                Image.insert_new(image_path=image_data['namepath'][1],
                                 image_dhash=image_data['dhash'],
                                 image_md5_hash=image_data['md5_hash'])

            print('Image saved to DB')
        elif file_type=='video':
            print('Save video files to DB')


    except Exception as err:
        print(err)

start_time = time.time()

files_paths = folders_files_walk(path=path)
print(files_paths)

# get photo and video files lists
image_files_list, video_files_list = index_folder_files(files_paths=files_paths)
print(image_files_list)
# parse images and get dict
result_image_dict = image_processing(image_files_list)
print(result_image_dict)

print('Images pairs list created')

# save all images to DB
save_files(result_image_dict, 'image')


# count hamming_distance betwen images hash
#hamming_pairs = hamming_distance(images_dict=result_image_dict)


print(f'Needed time for {len(result_image_dict)} images - {time.time()-start_time}')

