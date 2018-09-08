# -*- encoding:utf-8 -*-

import re
import time
import requests
from lxml import etree
from requests import ConnectionError
import sys


def index_page(page, judge, judge_name, url_kw):
    """
    爬取索引页
    :param page:页码
    :param judge: 用于判断上次爬取位置
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
        
        url = url_kw + str(i)
        headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

        try:
            # 获取索引页
            response_index = requests.get(url, headers = headers)
            response_index.encoding = 'gb2312'
            # time.sleep(2)
            # print(response_index.url)
        except ConnectionError:
            print('index_page_ConnectionError:' + url)

        # 通过xpath获取索引页内的文章列表url
        html_index = etree.HTML(response_index.text)
        source_index = html_index.xpath('//tr//td[@width="97%"]/a/@href')

        # 写入当前爬取到的第一个文章url
        if i == 1 and source_index:
            judge_next = source_index[0]
            with open(sys.path[0] + '/' + judge_name, 'w', encoding = 'utf-8') as f:
                print("judge_next:\t" + judge_next)
                f.write(judge_next)

        for item in source_index:
            # 判断是否爬取到上次爬取位置,是的话judge_last_spider赋值为False      
            if item == judge:
                print("已爬取到上次爬取位置！")
                judge_last_spider = False
                break

            # item: detail.asp?channelid1=110100&id=12399
            # print('item:', item, type(item))
            get_page(item)
        
def get_page(url):
    """
    提取文章内容
    :param url:文章假链接、提供真链接需要的参数
    :param url_kw: 不同分类下的url
    """
    # url:detail.asp?channelid1=110100&id=12399
    # url_full：http://www.cern.ac.cn/2news/detail.asp?channelid1=110100&id=12399
    url_full = 'http://www.cern.ac.cn/2news/' + url
    headers = {'user-agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)'}

    # 获取文章
    response_article = requests.get(url_full, headers = headers)
    response_article.encoding = 'gb2312'
    time.sleep(1)

    # 通过正则表达式获取文章中需要的内容
    pattren_article = re.compile(r'<td align="center" class="content_title">.*<table width="100%" align="center">', re.S)
    source_article = pattren_article.search(response_article.text)

    if source_article:
        source_article = source_article.group()
        # 获取文章中所有的图片url链接: ../manage/ewebeditor/uploadfile/201884173636958.jpg
        pattern_img = re.compile(r'<img(.*?)\ssrc="(.*?)"', re.I)
        findall_img = pattern_img.findall(source_article)
        for kw in findall_img:
            # kw[1]: ../manage/ewebeditor/uploadfile/201884173636958.jpg
            # 判断图片URL是否需要组合
            pattern_judge_img = re.compile(r'http')
            judge_img = pattern_judge_img.search(kw[1])
            # 图片保存名：name_save_img: 201884173636958.jpg
            pattern_name_save_img = re.compile(r'.*?(\w+.[jpbg][pmin]\w+)')
            name_save_img = pattern_name_save_img.search(kw[1]).group(1)
            # print('name_save_img:', name_save_img, type(name_save_img))
            if judge_img is None:
                # 图片网址：url_full_img: http://www.cern.ac.cn/manage/ewebeditor/uploadfile/201884173636958.jpg
                url_full_img = 'http://www.cern.ac.cn' + kw[1].replace('..','')
            else:
                url_full_img = kw[1]
            # print('url_full_img:', url_full_img, type(url_full_img))
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
            # ../manage/ewebeditor/uploadfile/201884173636958.jpg
            pattren_img_local = re.compile(r'.[pjbg][pinm]')
            img_real_name = pattren_img_local.search(match.group())

            if img_real_name:
                img_name  = ' src="./img/' + name_save_img + '"'
                return img_name

        # 匹配文章内容中的图片url，替换为本地图片url
        pattren_img_local = re.compile('\ssrc="(.*?)"')
        source_local = pattren_img_local.sub(url_img_name, source_article)

        # 提取url中的12399作为文件名保存: detail.asp?channelid1=110100&id=12399
        pattren_filename = re.compile(r'id=(.*)')
        filename = pattren_filename.search(url)

        # 保存文章内容 
        save_page(source_local, filename.group(1))

    else:
        print('error:' + url_full)

def save_img(source, filename):
    """
    保存文章中的图片
    :param source: 图片文件
    :param filename: 保存的图片名
    """
    name_save_img = sys.path[0] + '/cern_ac_spider_result/img/' + filename 
    try:
        # 保存图片
        with open(name_save_img, 'wb') as f:
            f.write(source)  
    except OSError as e:
        print('图片保存失败：' + name_save_img +'\n{e}'.format(e = e))

def save_page(source,filename):
    """
    保存到文件
    :param source: 结果
    :param filename: 保存的文件名
    """
    try:
        with open(sys.path[0] + '/cern_ac_spider_result/' + filename + '.html', 'w', encoding = 'utf-8') as f:
            f.write(source)
    except  OSError as e:
        print('内容保存失败：' + filename + '\n{e}'.format(e = e))

def main():
    """
    遍历每一页索引页
    """
    print("cern_ac_spider爬取开始！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

   
    judge_name = 'judge_news.txt'
    url_kw = 'http://www.cern.ac.cn/2news/index.asp?channelid1=110100&page='
    num = 3

    # 读取上次爬取时保存的用于判断爬取位置的字符串
    # with open('cern_ac_spider/' + judge_name, 'r', encoding = 'utf-8') as f:
    #         judge = f.read()
    judge = 2
    index_page(num, judge, judge_name, url_kw)

    print("cern_ac_spider爬取完毕，脚本退出！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))


if __name__ == '__main__':
    main()