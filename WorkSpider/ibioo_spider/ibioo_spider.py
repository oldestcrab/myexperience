# -*- encoding:utf-8 -*-

import re
import time
import requests
from lxml import etree
from requests import ConnectionError
import sys
import random
import os


def index_page(judge_last_time, judge_name, url_kw):
    """
    爬取索引页
    :param judge_last_time: 用于判断上次爬取位置
    :param judge_name: 判断爬取位置的数据保存名
    :param url_kw: 不同分类下的url
    """
    
    # judge_last_spider：用于判断是否爬取到上次爬取位置
    judge_last_spider = True
    
    for i in range(1,2):    
        # 如果judge_last_spider为False，则退出循环！
        if not judge_last_spider:
            break
        print('正在爬取第' + str(i) + '页！\t' + judge_name)
        with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
            list_user_agents = f.readlines()
            user_agent = random.choice(list_user_agents).strip()
        headers = {'user-agent':user_agent}
        try:
            # 获取索引页
            response_index = requests.get(url_kw, headers = headers)
            response_index.encoding = 'utf-8'
            # time.sleep(2)
            # print(response_index.url)
        except ConnectionError:
            print('index_page_ConnectionError:' + url_kw)

        # 通过xpath获取索引页内的文章列表url
        html_index = etree.HTML(response_index.text)
        source_index = html_index.xpath('//ul[@class="news-txtul"]/li/a/@href')
        # print(source_index)
        # 写入当前爬取到的第一个文章url
        if i == 1 and source_index:
            # /medicine/report/16451.html
            judge_next = source_index[0]
            with open(sys.path[0] + '/' + judge_name, 'w', encoding = 'utf-8') as f:
                print("judge_next:\t" + judge_next)
                f.write(judge_next)

        for item in source_index:
            # print(item)
            # 判断是否爬取到上次爬取位置,是的话judge_last_spider赋值为False 
            if item == judge_last_time:
                print("已爬取到上次爬取位置！")
                judge_last_spider = False
                break
            # item: /medicine/report/16451.html            
            get_page(item)
        
def get_page(url_page):
    """
    提取文章内容
    :param page_url: 文章部分链接
    """
    # url_page: /medicine/report/16451.html   
    with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
        list_user_agents = f.readlines()
        user_agent = random.choice(list_user_agents).strip()
    headers = {'user-agent':user_agent}
    # 获取文章
    url_article = 'http://www.ibioo.com' + url_page
    response_article = requests.get(url_article, headers = headers)
    response_article.encoding = 'gb2312'
    time.sleep(1)
    # print(response_article.url)

    # 通过正则表达式获取文章中需要的内容
    pattren_article = re.compile(r'<div class="article-body">.*<div class="article-extra clearfix">', re.I|re.S)
    source_article = pattren_article.search(response_article.text)
    # print(source_article.group)
    if source_article:
        source_article = source_article.group()
        # 获取文章中所有的图片url链接: /upimg/allimg/180914/1541513332-0.png
        pattern_img = re.compile(r'<img(.*?)\ssrc="(.*?)"', re.I)
        findall_img = pattern_img.findall(source_article)
        # print(findall_img)
        for kw in findall_img:
            # kw[1]: /upimg/allimg/180914/1541513332-0.png
            # 判断图片URL是否需要组合
            pattern_judge_img = re.compile(r'http', re.I)
            judge_img = pattern_judge_img.search(kw[1])
            if judge_img:
                url_full_img = kw[1]
            else:
                # 图片网址:url_full_img: http://www.ibioo.com/upimg/allimg/180914/1541513332-0.png
                url_full_img =  'http://www.ibioo.com' + kw[1]
                # 图片保存名：name_save_img: 1541513332-0.png
            # print(url_full_img)
            pattern_name_save_img = re.compile(r'.*\/(.*.[jpbg][pmin]\w+)', re.I)
            name_save_img = pattern_name_save_img.search(kw[1]).group(1)
            # print(name_save_img)
            try:
                # 获取图片
                response_img = requests.get(url_full_img, headers = headers).content
                # 保存图片
                save_img(response_img, name_save_img)
            except ConnectionError:
                print('图片网址有误:' + url_full_img)

        def url_img_name(match):
            """
            匹配文章内容中的图片url，替换为本地url
            """
            # /upimg/allimg/180914/1541513332-0.png
            pattren_img_local = re.compile(r'.[pjbg][pinm]', re.I)
            img_real_name = pattren_img_local.search(match.group())

            if img_real_name:
                pattern_kw_name_save_img = re.compile(r'.*\/(.*.[jpbg][pmin]\w+)', re.I)
                kw_img_name = pattern_kw_name_save_img.search(match.group(1)).group(1)
                img_name = ' src="./img/' + kw_img_name + '"'
                # else:
                    # img_name  = ' src="./img/' + match.group(1).replace('/imagewatermark/UploadFile/','') + '"'

                # print(img_name)
                return img_name

        # 匹配文章内容中的图片url，替换为本地图片url
        pattren_img_local = re.compile('\ssrc="(.*?)"')
        source_local = pattren_img_local.sub(url_img_name, source_article)

        # 提取url中的201895191925743.htm作为文件名保存: ./2018-9/201895191925743.htm
        # pattren_filename = re.compile(r'.*?(\w+.[h]\w+)', re.I)
        pattren_filename = re.compile(r'.*\/(.*.[h]\w+)', re.I)
        filename = pattren_filename.search(url_page)
        # print(filename.group(1))

        # 保存文章内容 
        save_page(source_local, filename.group(1))

    else:
        print('get_page_error:' + url_article)

def save_img(source, filename):
    """
    保存文章中的图片
    :param source: 图片文件
    :param filename: 保存的图片名
    """
    dir_save_img= sys.path[0] + '/ibioo_spider_result/img/'
    if not os.path.exists(dir_save_img):
        os.makedirs(dir_save_img)
    try:
        # 保存图片
        with open(dir_save_img + filename, 'wb') as f:
            f.write(source)  
    except OSError as e:
        print('图片保存失败：' +  filename +'\n{e}'.format(e = e))

def save_page(source,filename):
    """
    保存到文件
    :param page_title:文章标题
    :param source: 结果
    :param filename: 保存的文件名
    """
    dir_save_page = sys.path[0] + '/ibioo_spider_result/'
    if not os.path.exists(dir_save_page):
        os.makedirs(dir_save_page)
    try:
        with open(dir_save_page + filename, 'w', encoding = 'utf-8') as f:
            f.write(source)
    except  OSError as e:
        print('内容保存失败：' + filename + '\n{e}'.format(e = e))

def main():
    """
    遍历每一页索引页
    """
    print("ibioo_spider爬取开始！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

    # 用for循环遍历爬取不同分类下的文章
    for wd in range(1):
        if wd == 0:
            judge_name = 'judge_newarticle.txt'
            url_kw = 'http://www.ibioo.com/newarticle.php'
        # 读取上次爬取时保存的用于判断爬取位置的字符串
        dir_judge = sys.path[0] + '/' + judge_name
        if not os.path.exists(dir_judge):
            with open(dir_judge, 'w', encoding = 'utf-8'):
                print('创建文件：' + dir_judge)
        with open(dir_judge, 'r', encoding = 'utf-8') as f:
            judge_last_time = f.read()
        # judge_last_time = 1
        index_page(judge_last_time, judge_name, url_kw)

    print("ibioo_spider爬取完毕，脚本退出！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))


if __name__ == '__main__':
    main()