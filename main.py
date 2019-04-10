import time

from indexing import index_folder_files, reindex_image_files, reindex_video_files
from image_processing import image_processing, feature_description
from video_processing import video_processing
from database import save_new_files, Image, save_images_duplicates, get_image_duplicates, connection


# if connect ot postgres/mysql
'''
connection(provider='postgres',
           settings={
                'user': "similar_memes",
                'password': "veryhardpass",
                'host': "85.255.8.26",
                'database': "similar_memes_db",
           })
'''
# if connect to sqlite
connection(provider='sqlite', settings={'filename': 'db.sqlite', 'create_db': True})

#path = '/home/andrei/Downloads/Telegram Desktop/DataExport_06_12_2018/chats/chat_001/photos'
path = '/home/andrei/Pictures/'


# reindex DB image files
reindex_image_files()

# reindex DB video files
reindex_video_files()


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


result_video_dict = video_processing(video_files_list)
print(result_video_dict)
result_image_dict = image_processing(image_files_list)
print(result_image_dict)

# save all images to DB
save_new_files(result_image_dict, 'image')
# save all videos to DB
save_new_files(result_video_dict, 'video')


image_files_query = Image.get_images_paths()


result_image_features_list = feature_description(images_list=image_files_query)

print(result_image_features_list)
print(time.time()-start_time)

save_images_duplicates(pairs=result_image_features_list)

print(f'Needed time for {len(result_image_dict)} images - {time.time()-start_time}')

print(len(image_files_list))
print(len(result_image_dict))
print(len(image_files_query))


# get certain image all duplicates
result = get_image_duplicates(image_id=8)
print(result)