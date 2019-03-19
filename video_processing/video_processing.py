import os
import collections
import hashlib


from .audio_processing import audio_processing
from .settings import get_settings


def video_processing(video_list: collections.deque) -> collections.defaultdict:
    """
    Function cut video file on chunks and count hash

    :param video_list: List of videos in folder
                        0 - file name
                        1 - file full path

    :return: Dict of parsed videos
    """
    # prepare result dict
    result_video_dict = collections.defaultdict()

    # video parts amount to separate
    video_parts = get_settings()["video_parts"]

    for video in video_list:
        # get video size and separate on `video_parts` parts and read them + get video parts hash
        read_byte_step = os.path.getsize(video[1]) // video_parts + 1

        # read video file
        with open(video[1] + os.sep + video[0], "rb") as video_file:
            # prepare hash
            hasher = hashlib.md5()

            while True:
                # strip file bytes by prepared `read_byte_step`
                buf = video_file.read(read_byte_step)
                # if bytes is available - insert in hash
                if buf:
                    hasher.update(buf)
                # if file is ended - stop reading
                else:
                    break

                # TODO write hash-data to DB
                # print(hasher.hexdigest())

        print("Next video\n\n")

    return collections.defaultdict()
