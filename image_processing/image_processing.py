import os
import hashlib
import collections
import traceback
from multiprocessing import Pool

import cv2
import imageio
import numpy as np


class ColorDescriptor:
    def __init__(self, bins):
        # store the number of bins for the 3D histogram
        self.bins = bins

    def describe(self, image):
        # convert the image to the HSV color space and initialize
        # the features used to quantify the image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        features = []

        # grab the dimensions and compute the center of the image
        (h, w) = image.shape[:2]
        (cX, cY) = (int(w * 0.5), int(h * 0.5))
        # divide the image into four rectangles/segments (top-left,
        # top-right, bottom-right, bottom-left)
        segments = [(0, cX, 0, cY), (cX, w, 0, cY), (cX, w, cY, h), (0, cX, cY, h)]

        # construct an elliptical mask representing the center of the
        # image
        (axesX, axesY) = (int(w * 0.75) // 2, int(h * 0.75) // 2)
        ellipMask = np.zeros(image.shape[:2], dtype="uint8")
        cv2.ellipse(ellipMask, (cX, cY), (axesX, axesY), 0, 0, 360, 255, -1)

        # loop over the segments
        for (startX, endX, startY, endY) in segments:
            # construct a mask for each corner of the image, subtracting
            # the elliptical center from it
            cornerMask = np.zeros(image.shape[:2], dtype="uint8")
            cv2.rectangle(cornerMask, (startX, startY), (endX, endY), 255, -1)
            cornerMask = cv2.subtract(cornerMask, ellipMask)

            # extract a color histogram from the image, then update the
            # feature vector
            hist = self.histogram(image, cornerMask)
            features.append(hist)

        # extract a color histogram from the elliptical region and
        # update the feature vector
        hist = self.histogram(image, ellipMask)
        features.append(hist)

        # return the feature vector
        return features

    def histogram(self, image, mask):
        # extract a 3D color histogram from the masked region of the
        # image, using the supplied number of bins per channel
        hist = cv2.calcHist(
            [image], [0, 1, 2], mask, self.bins, [0, 180, 0, 256, 0, 256]
        )

        hist = cv2.normalize(hist, hist).flatten()

        # return the histogram
        return hist


module = ColorDescriptor((8, 12, 3))


def count_descriptor(image_file):
    try:
        # if image is GIF
        if image_file[0][-3:].lower() == "gif":
            # read gif
            gif = imageio.mimread(image_file[1] + os.sep + image_file[0])
            # get middle frame from gif
            image = gif[len(gif) // 2]
            # get gif params
            height, width, _ = image.shape
        else:
            image = cv2.imread(image_file[1] + os.sep + image_file[0])

            # get image params
            height, width, _ = image.shape

        features = np.array(module.describe(image=image), dtype=np.float32)
        return {
            "height": height,
            "width": width,
            "namepath": image_file,
            "image_descriptor": features.tobytes(),
            "md5_hash": hashlib.md5(
                (image_file[1] + os.sep + image_file[0]).encode()
            ).hexdigest(),
        }
    except Exception:
        print(traceback.format_exc())
        return None


def image_processing(image_list: collections.deque) -> list:
    """
    Function preprocess image files, count hash, count images descriptor(using ORB)
    and return files info in dict format

    :param image_list: List of images in folder
                        0 - files name
                        1 - file full path
    :return: Dict of parsed images and images data
    """
    pool = Pool()
    # run tasks in separate process
    res = pool.map(count_descriptor, image_list)

    # filter only indexed files
    processed_files = [file for file in res if file is not None]

    return processed_files
