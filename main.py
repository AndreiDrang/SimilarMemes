import time
from pony.orm import db_session

from indexing import index_folder_files, reindex_image_files, reindex_video_files
from image_processing import image_processing, feature_description
from video_processing import video_processing
from database import Image, save_images_duplicates, get_image_duplicates, connection


# if connect ot postgres/mysql
"""
connection(provider='postgres',
           settings={
                'user': "similar_memes",
                'password': "veryhardpass",
                'host': "85.255.8.26",
                'database': "similar_memes_db",
           })
"""
# if connect to sqlite
connection()

# path = '/home/andrei/Downloads/Telegram Desktop/DataExport_06_12_2018/chats/chat_001/photos'
path = "/home/andrei/Pictures/"


# reindex DB image files
reindex_image_files()

# reindex DB video files
reindex_video_files()


start_time = time.time()

print("Folders walked")
print(time.time() - start_time)

# get photo and video files lists
image_files_list, video_files_list = index_folder_files(
    path=path, max_depth=4, indexing_type="all"
)

#print(image_files_list)
#print(video_files_list)

print("Files indexed")


#video_processing(video_files_list)
print(len(image_files_list))
image_processing(image_files_list)
print((time.time() - start_time)/len(image_files_list))


with db_session():
    image_files_query = Image.get_descriptors()


feature_description(images_list=image_files_query)
print((time.time() - start_time)/len(image_files_query))
raise Exception

print(len(image_files_list))
print(len(image_files_query))


# get certain image all duplicates
result = get_image_duplicates(image_id=8, similarity_threshold=150)
print(result)
