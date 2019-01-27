import time

from indexing import index_folder_files, folders_files_walk
from image_processing import hamming_distance, image_processing
from video_processing import video_processing
from database import save_new_files, Image, save_images_duplicates




path = '/home/andrei/Downloads/Telegram Desktop/DataExport_06_12_2018/chats/chat_001/photos'
#path = '/home/andrei/Pictures'



start_time = time.time()

files_paths = folders_files_walk(path=path)

print('Folders walked')
print(time.time()-start_time)

# get photo and video files lists
image_files_list, video_files_list = index_folder_files(files_paths=files_paths)

print('Images indexed')
print(time.time()-start_time)

# parse images and get dict
result_image_dict = image_processing(image_files_list)
print(len(result_image_dict),' - Images processed.')

print(time.time()-start_time)

# save all images to DB
save_new_files(result_image_dict, 'image')


image_files_query = Image.get_dhash_id()

# count hamming_distance betwen images hash
hamming_pairs = hamming_distance(hashes_list=image_files_query)
print(len(hamming_pairs))
save_images_duplicates(hamming_pairs=hamming_pairs)

print(f'Needed time for {len(result_image_dict)} images - {time.time()-start_time}')

