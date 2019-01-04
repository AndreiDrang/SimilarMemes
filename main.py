import os
import time
import re

import imagehash
from PIL import Image

from hamming_distance import hamming_distance


path = '/home/andrei/Pictures/'
# precompiled regex to get file extension
file_extension_re = re.compile('([.]\w{3,4}$)')

def is_image(file_name: str)->bool:
    """
    Function check if file is image
    """
    # get file extension by regex
    file_extension = re.findall(file_extension_re, file_name.lower())

    if file_extension:
        return True if file_extension[0] in (".png", ".jpg", ".jpeg", ".bmp", ".gif") else False
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

def index_folder_files(path: str)->list:
    # get folder files
    memes_files = os.listdir(path)

    # TODO change on fast type
    # prepare result dicts
    result_image_dict = {}
    result_video_dict = {}

    for index, meme_file in enumerate(memes_files):
        # check if file - image
        if is_image(meme_file):
            # delete file format from image
            no_format_meme_image = re.sub(file_extension_re, '', meme_file)
            # open image file and convert it to grayscale
            img = Image.open(path+meme_file).convert('LA')
            # resize image to 9*8 format
            img.thumbnail(size=(80,80))
            # get image hash
            hash_result = str(imagehash.dhash(img))

            result_image_dict.update({
                                    index: {
                                        'name': no_format_meme_image,
                                        'hash': hash_result,
                                        'size': os.path.getsize(path+meme_file),
                                        'auto_tags': no_format_meme_image.split('_') if '_' in no_format_meme_image else no_format_meme_image.split(' ')
                                    }
                                })
    return result_image_dict, result_video_dict

start_time = time.time()


result_image_dict, result_video_dict = index_folder_files(path=path)

print(result_image_dict)

print(f'Needed time for {len(result_image_dict)} images - {time.time()-start_time}')

# find similar imgs
for first in result_image_dict:
    for second in result_image_dict:
        if first!=second:
            result = hamming_distance(first_hash=result_image_dict[first]['hash'], 
                                      second_hash=result_image_dict[second]['hash'])
            if result <= 10:
                print(result_image_dict[first]['name'])
                print(result_image_dict[second]['name'])
                print('Image similarity (low is better) - ', result)
                print('\n\n')

