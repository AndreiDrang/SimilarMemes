import os
import random
import time
from collections import defaultdict

import numpy as np
import cv2

orb = cv2.ORB_create()
bf = cv2.BFMatcher()

main_path = 'memes_dataset'

# create folders tree
main_tree = os.walk(main_path)

main_dict = defaultdict(str)

# looping throught tree and creating dict
for main_data in main_tree:
    main_dict[main_data[0]] = main_data[2]

# get all folders strarting second(cause first is core folder)
available_keys = [key for key in main_dict.keys()][1:]

with open('resultfile.txt', 'w') as logs:
    logs.write(f'{"First image":^60} | {"Second image":^60} | {"Similarity":^20} | {"Match param":^20}\n')

for i in range(1, 9000):
        first_key = random.choice(available_keys)
        second_key = random.choice(available_keys)

        if first_key == second_key:
            print(second_key)
            print('BINGO')

        first_file = random.choice(main_dict[first_key])
        second_file = random.choice(main_dict[second_key])

        img1 = cv2.imread(first_key+'/'+first_file, 0)
        img2 = cv2.imread(second_key+'/'+second_file, 0)

        if img1.any() and img2.any():

            _, des1 = orb.detectAndCompute(img1, None)
            _, des2 = orb.detectAndCompute(img2, None)
            
            try:
                matches12 = bf.knnMatch(des1, des2, k=2)
            except cv2.error as err:
                print(first_file)
                print(first_key+'/'+first_file)
                print(second_file)
                print(second_key+'/'+second_file)
                print(err)
                continue
        
            for param in range(77, 80):
                good=[]
                for m,n in matches12:
                    if m.distance < param/100*n.distance:
                        good.append(m)

                # sort images matches by distance, and get lowest 10 values(lower is better)
                match_sorted = sorted(good, key=lambda element: element.distance)

                LEN = 10 if len(match_sorted)>10 else len(match_sorted)

                match_sorted = match_sorted[:LEN]

                if match_sorted:

                    # count summ of sorted matches and get distance average value
                    average_match_value = sum(matching.distance for matching in match_sorted)//LEN
                    with open('resultfile.txt', 'a') as logs:
                        logs.write(f'{first_file[:50]:^60} | {second_file[:50]:^60} | {average_match_value:^20} | {param/100:^20}\n')
