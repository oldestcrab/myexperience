# -*- encoding:utf-8 -*-

import re
import time
import requests
from pyquery import PyQuery as pq
from lxml import etree
from requests import ConnectionError
import chardet
import os
import random
import pymysql
import sys
sys.path.append(r'C:/Users/CRAB/Desktop/myexperience/WorkSpider/spider')
# sys.path.append(r'/home/bmnars/spider_porject/spider')
from article_spider_pattern import RequestsParams as RP, ParseArticleSource as PAS, SaveArticleSource as SAS


def get_index_page(index_page, last_judge, last_judge_name, index_url):
    """
    获取索引页
    :param index_page:索引页码
    :param last_judge: 获取上次爬取位置
    :param last_judge_name: 保存爬取位置的文件名
    :param index_url: 爬取index_url
    """
    
    # LAST_THRESHOLD：用于判断是否爬取到上次爬取位置
    LAST_THRESHOLD = True
    
    # 爬取全部索引页
    for index_page in range(1,index_page):    
        
        # 如果LAST_THRESHOLD为False，则退出循环！
        if not LAST_THRESHOLD:
            break
        print('正在爬取第' + str(index_page) + '页！')

        # 拼接url
        index_full_url = index_url + str(index_page)
        # print('index_full_url', index_full_url)
        # 获取Headers
        requests_params = RP()
        headers = {'user-agent':requests_params.user_agent()}
        # print(headers)
        sess = requests.Session()
        sess.get('http://www.med.tsinghua.edu.cn/MoreServlet?newsClass=12', headers = headers)
        try:
            # 获取索引页
            index_response = sess.get(index_full_url, headers = headers)
            cod = chardet.detect(index_response.content)
            index_response.encoding = cod['encoding']
            time.sleep(3)
            # print(response_index.url)
        except Exception as e:
            # 打印报错信息
            print(e.args)
            index_response = ''
            print('get index page error: ' + index_full_url)
        # print(index_response.text)
        if index_response:
            # 通过xpath获取索引页内的文章列表url
            index_html = pq(index_response.text)
            index_source_list = index_html('h4 a')
            print(index_source_list.attr('href'))
            # 写入当前爬取到的第一个文章url
            if index_page == 1 and index_source_list:
                next_judge = index_source_list.attr('href')
                with open(sys.path[0] + '/' + last_judge_name, 'w', encoding = 'utf-8') as f:
                    print("next_judge: " + next_judge)
                    f.write(next_judge)

            for index_source in index_source_list.items():
                # 判断是否爬取到上次爬取位置,是的话LAST_THRESHOLD赋值为False      
                if index_source.attr('href') == last_judge:
                    print("已爬取到上次爬取位置！")
                    LAST_THRESHOLD = False
                    break
                # 获取文章部分url
                page_url = 'http://www.med.tsinghua.edu.cn/' + index_source.attr('href')
                # print('page_url', page_url)
                # 获取索引页
                get_article_page(page_url)
        
def get_article_page(page_url):
    """
    获取文章内容
    :param page_url:文章url
    """

    requests_params = RP()
    headers = {'user-agent':requests_params.user_agent()}
    # print(headers)
    print(page_url)
    # 获取文章
    article_response = requests.get(page_url, headers = headers)
    try:
        article_response = requests.get(page_url, headers = headers, timeout = 7)
        cod = chardet.detect(article_response.content)
        article_response.encoding = cod['encoding']
        time.sleep(3)
    except:
        article_response = ''
        print('get article page error: ' + page_url)

    if article_response:
        # 通过正则表达式获取文章中需要的内容
        article_pattren = re.compile(r'<div class="article_con">(.*)<div class="article_to">', re.S|re.I)
        article_source = article_pattren.search(article_response.text)
        # print(article_source.group(1))

        if article_source:
            article_source = article_source.group(1)

            # 解析文章类5
            parse_page = PAS()
            # 储存类
            save_source = SAS(PAGE_SAVE_DIR, ARTICLE_ORIGIN_WEBSITE)

            # 获取文章中所有的图片url链接
            img_pattern = re.compile(r'<img(.*?)\ssrc="(.*?)"', re.I|re.S)
            img_url_list = img_pattern.findall(article_source)
            # print('img_url_list: ', img_url_list)

            # IMG_EXISTS:判断能否获取图片
            IMG_EXISTS = True

            for img_part_url in img_url_list:
                # print('img_part_url[1]: ',img_part_url[1])
                
                # 判断图片URL是否需要组合，获取图片url
                img_judge_pattern = re.compile(r'http', re.I)
                img_judge = img_judge_pattern.search(img_part_url[1])
                if img_judge:
                    img_url = img_part_url[1]
                else:
                    img_url = 'http://www.med.tsinghua.edu.cn/' + img_part_url[1].replace('..','')
                # print('img_url: ',img_url)

                img_save_name_pattern = re.compile(r'.*\/(.*\.[jpbg][pmin]\w+)', re.I)
                try:
                    # 图片保存名
                    img_save_name = img_save_name_pattern.search(img_part_url[1]).group(1).replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','').replace('%','')
                    # print('img_save_name: ',  img_save_name)

                    # 获取图片
                    response_img = requests.get(img_url, headers = headers).content

                    # 保存图片
                    save_source.save_article_img(response_img, img_save_name)
                except:
                    print('图片网址有误: ' + img_url)
                    # 如果图片获取不到，则赋值为false
                    IMG_EXISTS = False
                    break

            # 如果获取得到图片，再进行下一步
            if IMG_EXISTS:

                # 提取文件名
                filename_pattern = re.compile(r'.*\=(.*)?', re.I)
                filename = filename_pattern.search(page_url).group(1) + '.html'
                filename = filename.replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','').replace('/page','')
                # print('filename: ',  filename)

                # 解析文章，提取有用的内容，剔除不需要的，返回内容列表
                article_sub_content = parse_page.sub_article_content(article_source, IMG_CHANGE_DIR)
                # print(article_sub_content)

                article_html = etree.HTML(article_response.text)
                # 获取文章标题
                article_title = article_html.xpath('//h2[@class="article_title clearfix"]')[0].text.strip()
                # print('article_title', article_title)
                # 获取文章作者
                article_user = ''
                # print('article_user', article_user)
                # 获取文章更新时间
                try:
                    article_update_time_pattern = re.compile(r'时间：.*(\d{4}-\d{2}-\d{2})')
                    article_update_time = article_update_time_pattern.search(article_response.text).group(1)
                except:
                    article_update_time = ''
                # print('article_update_time', article_update_time)
                # 获取文章来源
                article_origin = ''
                # print('article_origin', article_origin)

                article_content_list = parse_page.join_article_content(article_sub_content, article_title, article_user, article_update_time, article_origin)
                # print(article_content_list)

                # 保存文章内容 
                save_source.save_article_page(article_content_list, filename)
                # 存入mysql
                save_source.save_mysql(page_url, filename)
            else:
                print('获取不到图片', page_url)
        else:
            print('get_page content error', page_url)

# 判断运行位置，1表示本地运行
run_as = 1
if run_as == 1:
    # 图片替换路径
    IMG_CHANGE_DIR = './img/'
    # 文件存储路径
    PAGE_SAVE_DIR = sys.path[0] + '/med_tsinghua_edu_spider_result/'
else:
    IMG_CHANGE_DIR = '/home/bmnars/data/med_tsinghua_edu_spider_result/img/'
    PAGE_SAVE_DIR = '/home/bmnars/data/med_tsinghua_edu_spider_result/'

# 文章来源网站
ARTICLE_ORIGIN_WEBSITE = 'http://www.med.tsinghua.edu.cn'


def main():
    """
    遍历每一页索引页
    """
    print("med_tsinghua_edu_spider爬取开始！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    start_time = time.time()

    # 用for循环遍历爬取不同分类下的文章
    for wd in range(1):

        if wd == 0:
            # 保存爬取位置的文件名
            last_judge_name = 'judge.txt'
            # 索引url
            index_url = 'http://www.med.tsinghua.edu.cn/MoreServlet?rowCount=105&curPage='
            # 要爬取的索引总页数
            index_page = 4

        # 读取上次爬取时保存的用于判断爬取位置的字符串,如果不存在则创建
        judge_dir = sys.path[0] + '/' + last_judge_name
        if not os.path.exists(judge_dir):
            with open(judge_dir, 'w', encoding = 'utf-8'):
                print('创建文件：' + judge_dir) 
        # with open(judge_dir, 'r', encoding = 'utf-8') as f:
                # last_judge = f.read()
        last_judge = 1

        # 获取索引页
        get_index_page(index_page, last_judge, last_judge_name, index_url)

    print("med_tsinghua_edu_spider爬取完毕，脚本退出！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    print('共用时：', time.time()-start_time)


if __name__ == '__main__':
    main()