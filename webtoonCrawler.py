# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import shutil
import requests
from bs4 import BeautifulSoup
import numpy as np
import glob
from PIL import Image


def calculateSize(files):
    size_x = 0
    size_y = []
    cumsum_y = [0]
    file_list = []
    for file in files:
        image = Image.open(file)
        file_list.append(image)
        if size_x ==0:
            size_x = image.size[0]
        
        if size_x!=image.size[0] and size_x!=0:
            size_y.append(int(size_x / image.size[0] * image.size[1]))
        else:
            size_y.append(image.size[1])
    cumsum_y = cumsum_y + np.cumsum(size_y).tolist()
    return file_list, size_x, size_y, cumsum_y


def imageMerge(file_list, x_size, y_size, y_cumsum, file_path):
    new_image = Image.new("RGB", (x_size, y_cumsum[-1]), (256,256,256))
    for index in range(len(file_list)):
        
        if file_list[index].size[0]!=x_size:
            #print(file_list[index].size[0], file_list[index].size[1])
            #print(x_size,y_size[index])
            file_list[index] = file_list[index].resize((x_size, y_size[index]))

        area = (0, y_cumsum[index], x_size, y_cumsum[index]+y_size[index])
        new_image.paste(file_list[index],area)
    new_image.save("./" + file_path +  ".png", "PNG")


def crawl_naver_webtoon(episode_url, i):
    html = requests.get(episode_url).text
    soup = BeautifulSoup(html, 'html.parser')

    comic_title = ' '.join(soup.select('.comicinfo h2')[0].text.split())
    ep_title = ' '.join(soup.select('.tit_area h3')[0].text.split())

    for img_tag in soup.select('.wt_viewer img'):
        image_file_url = img_tag['src']
        image_dir_path = os.path.join(os.path.dirname(__file__), comic_title, ep_title)
        image_file_path = os.path.join(image_dir_path, os.path.basename(image_file_url))

        if not os.path.exists(image_dir_path):
            os.makedirs(image_dir_path)

        print(image_file_path)

        headers = {'Referer': episode_url}
        image_file_data = requests.get(image_file_url, headers=headers).content
        open(image_file_path, 'wb').write(image_file_data)
    
    files = sorted(glob.glob(image_dir_path + "/*IMAG*.jpg"), key=os.path.getmtime)
    file_list, x_size, y_size, y_cumsum = calculateSize(files)
    imageMerge(file_list, x_size, y_size, y_cumsum, image_dir_path)
    shutil.rmtree("./" + image_dir_path)
    print('Completed !')


if __name__ == '__main__':
    episode_url = 'https://comic.naver.com/webtoon/detail.nhn?titleId=651673&no='
    end_url = '&weekday=sat'
    for i in range(0, 513):
        crawl_naver_webtoon(episode_url + str(i) + end_url, i)
