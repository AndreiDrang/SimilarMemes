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


def index_folder_files(path: str)->list:
    """
    Function indexing image/video files in folder

    :param path: Full path adress

    :return: List of two lists: image files and video files
    """
    # get folder files
    memes_files = os.listdir(path)

    # prepare video and photo files lists
    image_files_list = collections.deque()
    video_files_list = collections.deque()

    for meme_file in memes_files:
        # check if file - image
        if is_image(meme_file):
            # add to image list
            image_files_list.append(meme_file)

        # if file - video
        elif is_video(meme_file):
            # add to video list
            video_files_list.append(meme_file)


    return image_files_list, video_files_list
