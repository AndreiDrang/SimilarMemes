from indexing import os, collections, re


# precompiled regex to get file extension
FILE_EXTENSION_RE = re.compile('([.]\w{3,4}$)')


def is_image(file_name: str)->bool:
    """
    Function check if file is image
    """
    # get file extension by regex
    file_extension = re.findall(FILE_EXTENSION_RE, file_name.lower())

    if file_extension:
        return True if file_extension[0] in (".png", ".jpg", ".jpeg", ".bmp", '.jpe', '.dib', '.gif') else False
    else:
        return False

def is_video(file_name: str)->bool:
    """
    Function check if file is image
    """
    # get file extension by regex
    file_extension = re.findall(FILE_EXTENSION_RE, file_name.lower())

    if file_extension:
        return True if file_extension[0] in (".mp4", ".webm") else False
    else:
        return False


def index_folder_files(files_paths: collections.deque)->(collections.deque, collections.deque):
    """
    Function indexing image/video files in folder

    :param files_paths: List of full files path adresses
                            0 - file name
                            1 - file full path

    :return: List of two lists: image files and video files
                0 - file name
                1 - file full path
    """

    # prepare video and photo files lists
    image_files_list = collections.deque()
    video_files_list = collections.deque()

    for file_ in files_paths:
        # check if file - image
        if is_image(file_[0]):
            # add to image list
            image_files_list.append(file_)

        # if file - video
        elif is_video(file_[0]):
            # add to video list
            video_files_list.append(file_)


    return image_files_list, video_files_list
