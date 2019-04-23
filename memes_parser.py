import re
import os
import time

import requests
from bs4 import BeautifulSoup
from collections import defaultdict

GLOBAL_HREF = 'https://imgflip.com'

MEMES = defaultdict(list)


def parse_memes_pages():
    memes_file = open('memes_pages_links.txt', 'w')
    memes_names = open('memes_names.txt', 'w')
    # get list of memes pages
    for i in range(1, 22):
        # open each page
        response = requests.get(f'{GLOBAL_HREF}/memetemplates?page={i}')
        if response.status_code==200:
            # read page content and get memes pages links and page name
            content = response.content
            soup = BeautifulSoup(content, features="lxml")

            for link in soup.find_all('h3', 'mt-title'):
                # write 
                memes_file.writelines(link.find('a')['href']+'\n')
                memes_names.writelines(link.text.replace('\n', '')+'\n')

        else:
            print(response.status_code)
    
    # close files
    memes_file.close()
    memes_names.close()

def parse_memes_src():
    # get list of memes from page and save it to dict
    pages_links = open('memes_pages_links.txt', 'r')
    links_names = open('memes_names.txt', 'r')
            
    for name in links_names.readlines():
        clear_name = name.replace('\n', '')

        url = GLOBAL_HREF+pages_links.readline().replace('\n', '')

        headers = {
            'cache-control': "no-cache",
        }

        # open each page
        response = requests.request("GET", url, headers=headers)

        if response.status_code==200:
            # read page content and get memes pages links and page name
            content = response.content

            soup = BeautifulSoup(content, features="lxml")

            # get all images src
            for img_src in soup.find_all('img', 'base-img'):
                clear_img_src = img_src['src'].replace('//', '')
                # prepare images folder
                os.makedirs(f'memes_dataset/{clear_name}', exist_ok=True)
                image_response = requests.get('https://'+clear_img_src)
                with open(f'memes_dataset/{clear_name}/{clear_name}_{time.time()}.jpg', 'wb') as image:
                    image.write(image_response.content)                   

        else:
            print(response.status_code)
        

#parse_memes_pages()
parse_memes_src()

