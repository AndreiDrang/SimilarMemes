import sys
import os
import collections
import re

from indexing import (
    IMAGE_FORMATS,
    VIDEO_FORMATS,
    FILE_EXTENSION_RE,
)

sys.path.append('.')
from database import group_image_files, group_video_files, Image, Video, delete, db_session, select


def is_image(file_name: str) -> bool:
    """
    Function check if file is image
    """
    # get file extension by regex
    file_extension = re.findall(re.compile(FILE_EXTENSION_RE), file_name.lower())

    if file_extension:
        return True if file_extension[0] in IMAGE_FORMATS else False
    else:
        return False


def is_video(file_name: str) -> bool:
    """
    Function check if file is image
    """
    # get file extension by regex
    file_extension = re.findall(re.compile(FILE_EXTENSION_RE), file_name.lower())

    if file_extension:
        return True if file_extension[0] in VIDEO_FORMATS else False
    else:
        return False


def get_depth(start_path: str, end_path: str):
    """
    Get start path and current path - count current path walk depth
    """
    depth = len(end_path.split(os.sep)) - len(start_path.split(os.sep))

    return depth


def index_folder_files(
    path: collections.deque, max_depth: int = 3, indexing_type: str = "all"
) -> (collections.deque, collections.deque):
    """
    Function indexing image/video files in folder

    :param path: Folder full path
    :param max_depth: Folders walking max depth
    :param indexing_type: File type to index; Available params - `image` / `video` / `all`;

    :return: List of two lists: image files and video files
                0 - file name
                1 - file full path
    """
    # create folders tree
    tree = os.walk(path)

    # prepare video and photo files lists
    image_files_list = collections.deque()
    video_files_list = collections.deque()

    # looping throught tree
    for data in tree:
        # if max depth not reached
        if get_depth(path, data[0]) <= max_depth:
            for file_ in data[2]:
                # check if file - image
                if is_image(file_) and indexing_type in ("image", "all"):
                    # add to image list
                    image_files_list.append((file_, data[0]))

                # if file - video
                elif is_video(file_) and indexing_type in ("video", "all"):
                    # add to video list
                    video_files_list.append((file_, data[0]))
        else:
            break

    return image_files_list, video_files_list


@db_session(retry=3)
def reindex_image_files():
    """
    Function reindex all Image files in DB
    
    Function check if path exist, if not - delete all images from this path
    Function check if image exist in this folder, if not - make not exist images ID's list and delete them from DB
    """
    image_files = group_image_files()
    # get path and file name
    for path, files in image_files.items():
        # check if path exist
        if os.path.exists(path):
            # get path files
            path_files = os.listdir(path)
            # filter files
            # if files not exist in FS but exist in DB - they deleted by user
            # and we need clean DB
            deletable_files = (image[1] for image in files if image[0] not in path_files)
            # looping in cycle and delete already deleted files(in FS) from DB
            for deleted_file in deletable_files:
                # delete file selected by ID
                Image[deleted_file].delete()
    
        else:
            # delete path if not exist
            delete(image for image in Image if image.image_path == path)


@db_session(retry=3)
def reindex_video_files():
    """
    Function reindex all Video files in DB
    
    Function check if path exist, if not - delete all videos from this path
    Function check if video exist in this folder, if not - make not exist videos ID's list and delete them from DB
    """
    video_files = group_video_files()
    # get path and file name
    for path, files in video_files.items():
        # check if path exist
        if os.path.exists(path):
            # get path files
            path_files = os.listdir(path)
            # filter files
            # if files not exist in FS but exist in DB - they deleted by user
            # and we need clean DB
            deletable_files = (video[1] for video in files if video[0] not in path_files)
            # looping in cycle and delete already deleted files(in FS) from DB
            for deleted_file in deletable_files:
                # delete file selected by ID
                Video[deleted_file].delete()
    
        else:
            # delete path if not exist
            delete(video for video in Video if video.video_path == path)

