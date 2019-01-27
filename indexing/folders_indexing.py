from indexing import os, collections


def get_depth(start_path: str, end_path: str):
    """
    Get start path and current path - count current path walk depth
    """
    depth = len(end_path.split('/'))-len(start_path.split('/'))
    
    return depth


def folders_files_walk(path: str, max_depth: int = 3)->collections.deque:
    """
    Function walking trought folder and indexing image/video files

    :param path: Full path adress
    :param max_depth: Folders walking max depth

    :return: List of images/videos files full path
                0 - files name
                1 - file full path
    """
    # create folders tree
    tree = os.walk(path)

    # prepare video and photo files lists
    folders_files = collections.deque()

    # looping throught tree
    for data in tree:
        # if max depth not reached
        if get_depth(path, data[0])<=max_depth:
            # append path+files to list
            for file_ in data[2]:
                folders_files.append((file_, data[0]+'/'+file_))
        # if max depth reached
        else:
            break

    return folders_files
