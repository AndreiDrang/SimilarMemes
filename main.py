import os
import time
import re
import collections
import hashlib

import imagehash
import numpy as np
from PIL import Image as PIL_Img

from hamming_distance import hamming_distance
from model import Image, Tag, Session


path = '/home/andrei/Downloads/Telegram Desktop/DataExport_06_12_2018/chats/chat_001/photos/'
# precompiled regex to get file extension
file_extension_re = re.compile('([.]\w{3,4}$)')

def is_image(file_name: str)->bool:
    """
    Function check if file is image
    """
    # get file extension by regex
    file_extension = re.findall(file_extension_re, file_name.lower())

    if file_extension:
        return True if file_extension[0] in (".png", ".jpg", ".jpeg", ".bmp", '.jpe', '.dib') else False
    else:
        return False

def is_video(file_name: str)->bool:

    """
    Function check if file is image
    """
    # get file extension by regex
    file_extension = re.findall(file_extension_re, file_name.lower())

    if file_extension:
        return True if file_extension[0] in (".mp4", ".webm") else False
    else:
        return False

def dhash(image): 
	# compute the (relative) horizontal gradient between adjacent
	# column pixels
	diff = image[:, 1:] > image[:, :-1]
 
	# convert the difference image to a hash
	return str(sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v]))

def index_folder_files(path: str)->list:
    """
    Function indexing image/video files in folder

    :param path: Full path adress
    """
    # get folder files
    memes_files = os.listdir(path)

    # TODO change on fast type
    # prepare result dicts
    result_image_dict = collections.defaultdict()
    result_video_dict = collections.defaultdict()

    for index, meme_file in enumerate(memes_files):
        # check if file - image
        if is_image(meme_file):
            # open image
            img = PIL_Img.open(path+meme_file)
            # resize image to 20*19 format
            img.thumbnail(size=(9,8))
            img.convert('LA')
            # get image hash
            hash_result = str(imagehash.dhash(img))

            result_image_dict.update({
                                        index: {
                                            'name': meme_file,
                                            'dhash': hash_result,
                                            'md5_hash': hashlib.md5(meme_file.encode()).hexdigest(),
                                            'size': os.path.getsize(path+meme_file),
                                        }
                                    })
    return result_image_dict, result_video_dict

def save_files(indexed_files: collections.defaultdict, file_type: str):
    """
    Function get files dict and files type and save it to DB

    :param indexed_files: Dict with all indexed files

    :param file_type: Files type - `image` or `video`
    """
    session = Session()

    if file_type=='image':
        print('Save images files to DB')
        for _, image_data in indexed_files.items():
            break
            session.add(Image(image_path=path+image_data['name'],
                              image_dhash=image_data['dhash'],
                              image_md5_hash=image_data['md5_hash'],
                              image_size=image_data['size'])
                        )
    elif file_type=='video':
        print('Save video files to DB')

    session.commit()
    session.close()

start_time = time.time()


result_image_dict, result_video_dict = index_folder_files(path=path)

image_pairs_list = collections.deque((first, second) for first in result_image_dict for second in result_image_dict if first != second)

save_files(result_image_dict, 'image')
save_files(result_video_dict, 'video')
'''
for pair in image_pairs_list:
    result = hamming_distance(first_hash=result_image_dict[pair[0]]['dhash'], 
                              second_hash=result_image_dict[pair[1]]['dhash'])
    if result < 5:
        print(result_image_dict[pair[0]]['name'])
        print(result_image_dict[pair[1]]['name'])
        print('Image similarity (low is better) - ', result)
        print('\n')
'''

print(f'Needed time for {len(result_image_dict)} images - {time.time()-start_time}')