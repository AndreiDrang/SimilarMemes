import collections
import hashlib

from moviepy.editor import *

from .audio_processing import audio_processing


def video_processing(video_list: collections.deque)->collections.defaultdict:
    """
    Function cut video file on chunks and count hash

    :param video_list: List of videos in folder
                        0 - file name
                        1 - file full path

    :return: Dict of parsed videos
    """
    # prepare result dict
    result_video_dict = collections.defaultdict()

    for video in video_list:
        print(video[0])

        # read video from file
        video_clip = VideoFileClip(video[1])
        # try get audio from readed video
        audio_clip = video_clip.audio

        # if sound exist in video_clip - send it to processing
        if audio_clip:
            audio_processing(audio_clip)

        with open(video[1], 'rb') as video_file:

            hasher = hashlib.md5()

            while True:
                try:
                    buf = video_file.read(1028)
                    if buf:
                        hasher.update(buf)
                    else:
                        break
                except Exception as err:
                    print(err)
                    break

        # hashlib.md5(image_file[0].encode()).hexdigest()
        print('Next video\n\n')

    return collections.defaultdict()
