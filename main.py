import time

from indexing import index_folder_files
from image_processing import image_processing, feature_description, hamming_distance
from video_processing import video_processing
from database import save_new_files, Image, save_images_duplicates




#path = '/home/andrei/Downloads/Telegram Desktop/DataExport_06_12_2018/chats/chat_001/photos'
path = '/home/andrey.rachalovsky/Pictures/'



start_time = time.time()

print('Folders walked')
print(time.time()-start_time)

# get photo and video files lists
image_files_list, video_files_list = index_folder_files(
                                            path=path, 
                                            max_depth=4,
                                            indexing_type='all'
                                        )

print(image_files_list)
print(video_files_list)

print('Files indexed')


result_image_features_list = feature_description(images_list=image_files_list)
print(result_image_features_list)

print(time.time()-start_time)

result_video_dict = video_processing(video_files_list)
print(result_video_dict)
result_image_dict = image_processing(image_files_list)
print(result_image_dict)

# parse images and get dict
#print(len(result_image_dict),' - Images processed.')

#print(time.time()-start_time)

# save all images to DB
#save_new_files(result_image_dict, 'image')


#image_files_query = Image.get_dhash_id()

# count hamming_distance betwen images hash
#hamming_pairs = hamming_distance(hashes_list=image_files_query)
#print(len(hamming_pairs))
#save_images_duplicates(hamming_pairs=hamming_pairs)

#print(f'Needed time for {len(result_image_dict)} images - {time.time()-start_time}')

