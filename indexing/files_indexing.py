from indexing import os, collections, re, IMAGE_FORMATS, VIDEO_FORMATS, FILE_EXTENSION_RE


def is_image(file_name: str)->bool:
    """
    Function check if file is image
    """
    # get file extension by regex
    file_extension = re.findall(re.compile(FILE_EXTENSION_RE), file_name.lower())

    if file_extension:
        return True if file_extension[0] in IMAGE_FORMATS else False
    else:
        return False

def is_video(file_name: str)->bool:
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
    depth = len(end_path.split('/'))-len(start_path.split('/'))
    
    return depth

def index_folder_files(path: collections.deque, max_depth: int = 3, indexing_type: str = 'all')->(collections.deque, collections.deque):
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
        if get_depth(path, data[0])<=max_depth:
            for file_ in data[2]:
                # check if file - image
                if is_image(file_) and indexing_type in ('image', 'all'):
                    # add to image list
                    image_files_list.append((file_, data[0]))

                # if file - video
                elif is_video(file_) and indexing_type in ('video', 'all'):
                    # add to video list
                    video_files_list.append((file_, data[0]))
        else:
            break

    return image_files_list, video_files_list
