# -*- coding:utf-8 -*-
import config
import time
import os
import sys
import random
import requests
from lxml import etree

def get_index_page(page):
    """
    爬取页面
    :param page:页码数
    """
    # dir_judge_page : 保存上次爬取的页数
    dir_judge_page = sys.path[0] + '/judge_page.txt'
    if not os.path.exists(dir_judge_page):
        with open(dir_judge_page, 'w', encoding = 'utf-8') as f:
            f.write('1')
        print('创建文件：' + dir_judge_page + ',并赋值page_next_start = 1')

    # 如果是新爬取的，则起始页为1，否则读取上次爬取时的页数，并作为起始页
    if config.tumblr_likes_judge_new:
        page_next_start = 1
    else:
        with open(dir_judge_page, 'r', encoding = 'utf-8') as f:
            page_next_start = int(f.readline())

    # config.tumblr_likes_username : 爬取用户名
    for i in range(page_next_start, page):
        # 保存当前爬取页数
        with open(dir_judge_page, 'w', encoding = 'utf-8') as f:
            f.write(str(i))
        # url : https://oldestcrab.tumblr.com/likes/page/1
        url = 'https://' + config.tumblr_likes_username + '.tumblr.com/likes/page/' + str(i)

        with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
            list_user_agents = f.readlines()
            user_agent = random.choice(list_user_agents).strip()
        headers = {'user-agent':user_agent}
        try:
            response_index = requests.get(url, headers = headers)
            response_index.encoding = 'utf-8'
            time.sleep(1)
        except:
            print('get page error:' + url)
            response_index = requests.get('https://www.baidu.com', headers = headers)

        page_html = etree.HTML(response_index.text)
        list_source = page_html.xpath('//div[@class="video-wrapper"]//iframe')
        print(list_source)
        for i in list_source:
            url_video = i.xpath('@src')[0]
            # print(url_video)
            get_video_page(url_video)

def get_video_page(url_video):
    """
    爬取视频页面
    :param url_video:视频框架页面
    """
    with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
        list_user_agents = f.readlines()
        user_agent = random.choice(list_user_agents).strip()
    headers = {'user-agent':user_agent}
    try:
        response_video_page = requests.get(url_video, headers = headers)
        response_video_page.encoding = 'utf-8'
        time.sleep(1)
    except:
        print('get video page error:' + url_video)
        response_video_page = requests.get('https://www.baidu.com', headers = headers)

    video_html = etree.HTML(response_video_page.text)
    video_source = video_html.xpath('//video//source/@src')[0]
    print(video_source)
    try:
        response_video = requests.get(url_video, headers = headers)
        response_video.encoding = 'utf-8'
        time.sleep(1)
    except:
        print('get video page error:' + url_video)
        response_video = requests.get('https://www.baidu.com', headers = headers)

    save_content(response_video.content)

def save_content(video_source):
    """
    爬取视频页面
    :param video_source:视频链接
    """   
    dir_save_vedio = sys.path[0] + '/'  + config.tumblr_likes_username + '_result/'
    if not os.path.exists(dir_save_vedio):
        os.makedirs(dir_save_vedio)
    try:
        # 保存图片
        print('sdgsljsjl')
        with open(dir_save_vedio + '111.mp4', 'wb') as f:
            f.write(video_source)  
    except OSError as e:
        print('图片保存失败：' + '111.mp4' +'\n{e}'.format(e = e))


def main():
    print('tumblr_likes_spider爬取开始！')
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

    # config.tumblr_likes_page : 爬取页数    
    get_index_page(config.tumblr_likes_page)

    print('tumblr_likes_spider爬取结束！')
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

if __name__ == '__main__':
    main()