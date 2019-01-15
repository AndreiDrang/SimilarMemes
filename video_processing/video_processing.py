import collections
import hashlib



def video_processing(video_list: collections.deque)->collections.defaultdict:
    """
    Function cut video file on chunks and count hash

    :param video_list: List of images in folder
                        0 - files name
                        1 - file full path

    :return: Dict of parsed videos
    """
    # prepare result dict
    result_video_dict = collections.defaultdict()

    for video in video_list:

        with open(video[1], 'rb') as video_file:

            hasher = hashlib.md5()

            while True:
                try:
                    buf = video_file.read(128)
                    if buf:
                        hasher.update(buf)
                    else:
                        break
                except Exception as err:
                    print(err)
                    break
                print(hasher.hexdigest())

            print(hasher.hexdigest())

        # hashlib.md5(image_file[0].encode()).hexdigest()

    return collections.defaultdict()
