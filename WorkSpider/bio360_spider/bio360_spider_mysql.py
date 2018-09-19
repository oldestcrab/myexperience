# -*- encoding:utf-8 -*-

import re
import time
import requests
from lxml import etree
from requests import ConnectionError
import sys
import random
import os
import pymysql

def index_page(page, judge_last_time, judge_name, url_kw):
    """
    爬取索引页
    :param page:页码
    :param judge_last_time: 用于判断上次爬取位置
    :param judge_name: 判断爬取位置的数据保存名
    :param url_kw: 不同分类下的url
    """
    
    # judge_last_spider：用于判断是否爬取到上次爬取位置
    judge_last_spider = True
    
    for i in range(1,page):    
        # 如果judge_last_spider为False，则退出循环！
        if not judge_last_spider:
            break
        print('正在爬取第' + str(i) + '页！\t' + judge_name)
        # 完整url 
        url = url_kw + str(i) 
        # print('url:', type(url), url)
        with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
            list_user_agents = f.readlines()
            user_agent = random.choice(list_user_agents).strip()
        headers = {'user-agent':user_agent}
        try:
            # 获取索引页
            response_index = requests.get(url, headers = headers)
            response_index.encoding = 'utf-8'
            # time.sleep(2)
            # print('response_index:', type(response_index), response_index.url)
        except ConnectionError:
            print('index_page_ConnectionError:' + url_kw)

        # 通过xpath获取索引页内的文章列表url
        html_index = etree.HTML(response_index.text)
        source_index = html_index.xpath('//h3/a/@href')
        # print('source_index:', type(source_index), source_index)
        # 写入当前爬取到的第一个文章url
        if i == 1 and source_index:
            # http://www.bio360.net/article/154727
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
            # item: http://www.bio360.net/article/154727 
            get_page(item)
        
def get_page(url_page):
    """
    提取文章内容
    :param page_url: 文章部分链接
    """
    # print(url_page)
    # url_page: http://www.bio360.net/article/154727
    with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
        list_user_agents = f.readlines()
        user_agent = random.choice(list_user_agents).strip()
    headers = {'user-agent':user_agent}
    # 获取文章
    # url_article = 'http://www.ibioo.com' + url_page
    response_article = requests.get(url_page, headers = headers)
    response_article.encoding = 'utf-8'
    time.sleep(1)
    # print('response_article:', type(response_article), response_article.url)

    # 通过正则表达式获取文章中需要的内容
    pattren_article = re.compile(r'<div class="article-header">.*不代表本站立场', re.I|re.S)
    source_article = pattren_article.search(response_article.text)
    # print('source_article.group():', type(source_article.group()), source_article.group())
    if source_article:
        source_article = source_article.group()
        # 获取文章中所有的图片url链接: http://www.bio360.net/storage/image/2018/08/FG3XNGQGmD2HxBMqFgNNmiuLNXjTWHU9cnblI8TV.png
        pattern_img = re.compile(r'<img(.*?)\ssrc="(.*?)"', re.I)
        findall_img = pattern_img.findall(source_article)
        # print('findall_img:', type(findall_img), findall_img)
        for kw in findall_img:
            # kw[1]: http://www.bio360.net/storage/image/2018/08/FG3XNGQGmD2HxBMqFgNNmiuLNXjTWHU9cnblI8TV.png
            # 判断图片URL是否需要组合
            # print('kw[1]',kw[1])
            pattern_judge_img = re.compile(r'http', re.I)
            judge_img = pattern_judge_img.search(kw[1])
            if judge_img:
                url_full_img = kw[1]
            else:
                # 图片网址:url_full_img: http://www.bio360.net/storage/image/2018/08/FG3XNGQGmD2HxBMqFgNNmiuLNXjTWHU9cnblI8TV.png
                url_full_img =  'http://www.bio360.net' + kw[1]
                # 图片保存名：dwNNY7cwzRcOcsjRwMFcceLF9qTvhyDP8HiHTgQc.png
            url_full_img = url_full_img.replace('&#10;','')
            # print('url_full_img:', type(url_full_img), url_full_img)
            pattern_name_save_img = re.compile(r'.*\/(.*\.[jpbg][pmin]\w+)', re.I)
            try:
                name_save_img = pattern_name_save_img.search(kw[1]).group(1)
                # print('name_save_img:', type(name_save_img), name_save_img)
                # 获取图片
                response_img = requests.get(url_full_img, headers = headers).content
                # 保存图片
                save_img(response_img, name_save_img)
            except:
                print('图片网址有误:' + url_full_img)

        def url_img_name(match):
            """
            匹配文章内容中的图片url，替换为本地url
            """
            # http://www.bio360.net/storage/image/2018/08/FG3XNGQGmD2HxBMqFgNNmiuLNXjTWHU9cnblI8TV.png
            pattren_img_local = re.compile(r'\.[pjbg][pinm]', re.I)
            img_real_name = pattren_img_local.search(match.group())
            # print('match.group(1)', match.group(1))
            if img_real_name and match.group(1):
                pattern_kw_name_save_img = re.compile(r'.*\/(.*\.[jpbg][pmin]\w+)', re.I)
                kw_img_name = pattern_kw_name_save_img.search(match.group(1)).group(1)
                img_name = ' src="/home/bmnars/data/bio360_spider_result/img/' + kw_img_name + '"'
                # print('img_name:', type(img_name), img_name)
                return img_name

        # 匹配文章内容中的图片url，替换为本地图片url
        pattren_img_local = re.compile('\ssrc="(.*?)"')
        source_local = pattren_img_local.sub(url_img_name, source_article)

        # 提取url中的154727作为文件名保存: http://www.bio360.net/article/154727
        pattren_filename = re.compile(r'.*\/(.*)?', re.I)
        filename = pattren_filename.search(url_page)
        # print('filename.group(1):', type(filename.group(1)), filename.group(1))

        # 保存文章内容 
        save_page(source_local, filename.group(1))
        save_mysql(url_page, filename.group(1))

    else:
        print('get_page_error:' + url_page)

def save_img(source, filename):
    """
    保存文章中的图片
    :param source: 图片文件
    :param filename: 保存的图片名
    """
    dir_save_img= '/home/bmnars/data/bio360_spider_result/img/'
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
    dir_save_page ='/home/bmnars/data/bio360_spider_result/'
    if not os.path.exists(dir_save_page):
        os.makedirs(dir_save_page)
    try:
        with open(dir_save_page + filename + '.html', 'w', encoding = 'utf-8') as f:
            f.write(source)
    except  OSError as e:
        print('内容保存失败：' + filename + '\n{e}'.format(e = e))


def save_mysql(url_source, url_local):
    """
    保存到文件
    :param url_source: 文章来源url
    :param url_local: 文章本地url
    """
    db = pymysql.connect(host='localhost', user='bmnars', password='vi93nwYV', port=3306, db='bmnars')
    cursor = db.cursor()
    url_local_full = '/home/bmnars/data/bio360_spider_result/' + url_local  + '.html'
    update_time = time.strftime('%Y-%m-%d',time.localtime())
    data = {
        'source_url':url_source,
        'local_url':url_local_full,
        'source':'www.bio360.net',
	    'update_time':update_time
    }
    table = '_cs_bmnars_link'
    keys = ','.join(data.keys())
    values = ','.join(['%s']*len(data))
    sql = 'INSERT INTO {table}({keys}) VALUES ({values}) on duplicate key update '.format(table=table, keys=keys, values=values)
    update = ', '.join(['{key} = %s'.format(key=key) for key in data]) + ';'
    sql += update
    # print(sql)
    try:
        if cursor.execute(sql,tuple(data.values())*2):
            db.commit()
    except:
        print("save_mysql_failed:" + url_source)
        db.rollback()
    
    finally:
        cursor.close()      
        db.close()

def main():
    """
    遍历每一页索引页
    """
    print("bio360_spider爬取开始！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

    # 用for循环遍历爬取不同分类下的文章
    for wd in range(1):
        if wd == 0:
            judge_name = 'judge_article.txt'
            url_kw = 'http://www.bio360.net/article/ajax?&page='
            num = 9
        # 读取上次爬取时保存的用于判断爬取位置的字符串
        dir_judge = sys.path[0] + '/' + judge_name
        if not os.path.exists(dir_judge):
            with open(dir_judge, 'w', encoding = 'utf-8'):
                print('创建文件：' + dir_judge)
        with open(dir_judge, 'r', encoding = 'utf-8') as f:
            judge_last_time = f.read()
        # judge_last_time = 1
        index_page(num, judge_last_time, judge_name, url_kw)

    print("bio360_spider爬取完毕，脚本退出！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))


if __name__ == '__main__':
    main()