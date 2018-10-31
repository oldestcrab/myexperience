# -*- coding:utf-8 -*-
import config
import time
import os
import sys
import random
import requests
from lxml import etree
import re

def get_index_page(page_end):
    """
    爬取页面
    :param page_end:页码数
    """
    # dir_judge_start_page : 保存上次最后爬取的页数
    dir_judge_start_page = sys.path[0] + '/judge_share_start_page.txt'
    if not os.path.exists(dir_judge_start_page):
        with open(dir_judge_start_page, 'w', encoding = 'utf-8') as f:
            f.write('1')
        print('创建文件：' + dir_judge_start_page + ',并赋值page_next_start = 1')

    # 如果是新爬取的，True，则起始页为1，否则读取上次爬取时的页数，并作为起始页
    # config.tumblr_share_judge_new : True|False
    if config.tumblr_share_judge_new:
        page_start = 1
    else:
        with open(dir_judge_start_page, 'r', encoding = 'utf-8') as f:
            page_start = int(f.readline())

    # config.tumblr_likes_username : 爬取用户名
    for i in range(page_start, page_end):
        # 保存当前爬取页数
        print('当前爬取页码数：' + str(i))
        with open(dir_judge_start_page, 'w', encoding = 'utf-8') as f:
            f.write(str(i))
        # url : https://oldestcrab.tumblr.com/likes/page/1
        url = 'https://' + config.tumblr_share_username + '.tumblr.com/page/' + str(i)
        print(url)
        with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
            list_user_agents = f.readlines()
            user_agent = random.choice(list_user_agents).strip()
        headers = {'user-agent':user_agent}

        # 获取框架页面url列表
        try:
            response_index = requests.get(url, headers = headers)
            response_index.encoding = 'utf-8'
            time.sleep(1)
        except:
            print('get page error:' + url)
            response_index = requests.get('https://www.baidu.com', headers = headers)

        html_iframe = etree.HTML(response_index.text)

        try:
            list_source_1 = html_iframe.xpath('//div[@class="video-wrapper"]//iframe')
            
        except:
            print('get list_source_1 error!')
            list_source_1 = []

        try:
            list_source_2 = html_iframe.xpath('//div[@class="reblog-list"]')
            # list_source_2 = html_iframe.xpath('//div[@class="reblog-list"]')
            
        except:
            print('get list_source_2 error!')
            list_source_2 = []
        # print(list_source_2)
        if list_source_1:
            for i in list_source_1:
                get_video_page_1(i)

        if list_source_2:
            for i in list_source_2:
                get_video_page_2(i)

def get_video_page_1(content_lxml):
    """
    爬取视频页面
    :param content_lxml:通过xpath获取的内容
    """
    # url_iframe : https://everythingfox.tumblr.com/video_file/t:TQ_U5i4OlLu9TxRYtxAdzg/179493447941/tumblr_ph9x0xr04g1vmobp0/480
    url_iframe = content_lxml.xpath('@src')[0]
    # print(url_iframe)
    with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
        list_user_agents = f.readlines()
        user_agent = random.choice(list_user_agents).strip()
    headers = {'user-agent':user_agent}

    # 获取框架页面
    try:
        response_video_iframe_page = requests.get(url_iframe, headers = headers)
        response_video_iframe_page.encoding = 'utf-8'
        time.sleep(1)
    except:
        print('get video page error:' + url_iframe)
        response_video_iframe_page = requests.get('https://www.baidu.com', headers = headers)

    try:
        video_iframe_html = etree.HTML(response_video_iframe_page.text)
        url_video_iframe = video_iframe_html.xpath('//video//source/@src')[0]
        # print(url_video_iframe)
    except:
        url_video_iframe = ''
    
    if url_video_iframe:
        try:
            response_video_iframe = requests.get(url_video_iframe, headers = headers)
            response_video_iframe.encoding = 'utf-8'
            time.sleep(1)
            # print(response_video_iframe.url)
        except:
            print('get video page error:' + url_video_iframe)
            response_video_iframe = requests.get('https://www.baidu.com', headers = headers)

        # url_video : https://vf.media.tumblr.com/tumblr_ph9x0xr04g1vmobp0_480.mp4
        url_video = response_video_iframe.url
        print(url_video)
        pattren_name_video = re.compile(r'.*\/(.*)?', re.I)
        name_video = pattren_name_video.search(url_video).group(1) 
        # print(name_video)

        # html_video = etree.HTML(response_video_iframe.content)
        # print(html_video)
        # url_video = html_video.xpath('//source/@src')[0]
        # print(url_video)
        try:
            response_video = requests.get(url_video, headers = headers)
            response_video.encoding = 'utf-8'
            time.sleep(1)
        except:
            print('get video page error:' + url_video)
            response_video = requests.get('https://www.baidu.com', headers = headers)

        save_content(name_video, response_video.content)

def get_video_page_2(content_lxml):
    """
    爬取视频页面
    :param content_lxml:通过xpath获取的内容
    """
    # url_iframe : https://everythingfox.tumblr.com/video_file/t:TQ_U5i4OlLu9TxRYtxAdzg/179493447941/tumblr_ph9x0xr04g1vmobp0/480
    url_video = content_lxml.xpath('./div[@class = "post-reblog-trail-item original-reblog-content"]/div[@class="post-reblog-content"]//source/@src')[0]
    # name_video = ''.join(content_lxml.xpath('./div[@class="post-reblog-content"]//p/text()')) 
    list_name_1 = content_lxml.xpath('./div[@class = "post-reblog-trail-item original-reblog-content"]/div[@class="post-reblog-content"]//p/text()')
    list_name_2 = content_lxml.xpath('./div[@class = "post-reblog-trail-item"]//p/text()')
    if list_name_1 and len(list_name_1)<3:
        name_video = ''.join(list_name_1) + '.mp4'
    elif list_name_2 and len(list_name_2)<3:
        name_video = ''.join(list_name_2) + '.mp4'
    else:
        pattren_name_video = re.compile(r'.*\/(.*)?', re.I)
        name_video = pattren_name_video.search(url_video).group(1) 

    print(name_video)
    print(url_video)
    print(type(name_video))
    with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
        list_user_agents = f.readlines()
        user_agent = random.choice(list_user_agents).strip()
    headers = {'user-agent':user_agent}

    try:
        response_video = requests.get(url_video, headers = headers)
        response_video.encoding = 'utf-8'
        time.sleep(1)
    except:
        print('get video page error:' + url_video)
        response_video = requests.get('https://www.baidu.com', headers = headers)
        
    save_content(name_video, response_video.content)

def save_content(name_video, content_video):
    """
    爬取视频页面
    :param name_video:视频保存名字
    :param content_video:视频链接
    """   
    dir_save_vedio = sys.path[0] + '/'  + config.tumblr_likes_username + '_result/'
    if not os.path.exists(dir_save_vedio):
        os.makedirs(dir_save_vedio)
    try:
        # 保存图片
        with open(dir_save_vedio + name_video, 'wb') as f:
            f.write(content_video)  
    except OSError as e:
        print('图片保存失败：' + name_video +'\n{e}'.format(e = e))


def main():
    print('tumblr_likes_spider爬取开始！')
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

    # config.tumblr_likes_page : 爬取总页数    
    get_index_page(config.tumblr_share_page)

    print('tumblr_likes_spider爬取结束！')
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

if __name__ == '__main__':
    main()