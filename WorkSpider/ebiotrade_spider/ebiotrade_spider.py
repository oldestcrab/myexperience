# -*- encoding:utf-8 -*-

import re
import time
import requests
from lxml import etree
from requests import ConnectionError
import sys
import random
import os


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
        url = url_kw + '&page=' + str(i) 
        # headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
            list_user_agents = f.readlines()
            user_agent = random.choice(list_user_agents).strip()
        headers = {'user-agent':user_agent}
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
        source_index = html_index.xpath('//ul[@class="news-list"]//a')
        # print(source_index)
        # 写入当前爬取到的第一个文章url
        if i == 1 and source_index:
            judge_next = source_index[0].xpath('@href')[0]
            with open(sys.path[0] + '/' + judge_name, 'w', encoding = 'utf-8') as f:
                print("judge_next:\t" + judge_next)
                f.write(judge_next)

        for item in source_index:
            # item_title: Science综述：DNA读写和分子记录仪的新兴应用（四）
            item_title = item.text
            # item_url: ./2018-9/201895191925743.htm
            item_url = item.xpath('@href')[0]
            # print(item_title,item_url)
            # 判断是否爬取到上次爬取位置,是的话judge_last_spider赋值为False 
            if item_url == judge_last_time:
                print("已爬取到上次爬取位置！")
                judge_last_spider = False
                break
            get_page(item_title, item_url)
        
def get_page(page_title, page_url):
    """
    提取文章内容
    :param page_title:文章标题
    :param page_url: 文章部分链接
    """
    # print(page_title)
    # url: ./2018-9/201895191925743.htm
    # url_full：http://www.ebiotrade.com/newsf/2018-9/201895191925743.htm
    url_full = 'http://www.ebiotrade.com/newsf/' + page_url.replace('./','')
    # headers = {'user-agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)'}
    with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
        list_user_agents = f.readlines()
        user_agent = random.choice(list_user_agents).strip()
    headers = {'user-agent':user_agent}
    # 获取文章
    response_article = requests.get(url_full, headers = headers)
    response_article.encoding = 'gb2312'
    time.sleep(1)
    # print(response_article.url)

    # 通过正则表达式获取文章中需要的内容
    pattren_article = re.compile(r'<P.*<div class=\'nav-pagination\'>', re.I|re.S)
    source_article = pattren_article.search(response_article.text)
    # print(source_article.group)
    if source_article:
        source_article = source_article.group()
        # 获取图片前半部分网址
        # # url_img.group(1):http://www.whiov.ac.cn/xwdt_105286/kydt/201804
        # pattren_url_img = re.compile(r'(.*?)/t')
        # url_img = pattren_url_img.search(url_full)

        # 获取文章中所有的图片url链接: /imagewatermark/UploadFile/2018090519171730.JPG
        pattern_img = re.compile(r'<img(.*?)\ssrc="(.*?)"', re.I)
        findall_img = pattern_img.findall(source_article)
        # print(findall_img)
        for kw in findall_img:
            # kw[1]: /imagewatermark/UploadFile/2018090519171730.JPG
            # 判断图片URL是否需要组合
            pattern_judge_img = re.compile(r'http', re.I)
            judge_img = pattern_judge_img.search(kw[1])
            if judge_img:
                url_full_img = kw[1]
            else:
                # 图片网址:url_full_img: http://www.ebiotrade.com/imagewatermark/UploadFile/2018090519171730.JPG
                url_full_img =  'http://www.ebiotrade.com' + kw[1]
                # 图片保存名：name_save_img: 2018090519171730.JPG
                # name_save_img = kw[1].replace('./','')

            pattern_name_save_img = re.compile(r'.*?(\w+.[jpbg][pmin]\w+)', re.I)
            name_save_img = pattern_name_save_img.search(kw[1]).group(1)
            # print(url_full_img,name_save_img)
            try:
                # 获取图片
                response_img = requests.get(url_full_img, headers = headers).content
                # 保存图片
                # print(url_full_img)
                save_img(response_img, name_save_img)
            except ConnectionError:
                print('图片网址有误:' + url_full_img)

        def url_img_name(match):
            """
            匹配文章内容中的图片url，替换为本地url
            """
            # /imagewatermark/UploadFile/2018090519171730.JPG
            pattren_img_local = re.compile(r'.[pjbg][pinm]', re.I)
            img_real_name = pattren_img_local.search(match.group())

            if img_real_name:
                # pattern_judge_img_real_name = re.compile(r'http')
                # judge_img_real_name = pattern_judge_img_real_name.search(match.group(1))
                # if judge_img_real_name:
                pattern_kw_name_save_img = re.compile(r'.*?(\w+.[jpbg][pmin]\w+)', re.I)
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
        pattren_filename = re.compile(r'.*?(\w+.[h]\w+)', re.I)
        filename = pattren_filename.search(page_url)
        # print(filename)

        # 保存文章内容 
        save_page(page_title, source_local, filename.group(1))

    else:
        print('get_page_error:' + url_full)

def save_img(source, filename):
    """
    保存文章中的图片
    :param source: 图片文件
    :param filename: 保存的图片名
    """
    dir_save_img= sys.path[0] + '/ebiotrade_spider_result/img/'
    if not os.path.exists(dir_save_img):
        os.makedirs(dir_save_img)
    try:
        # 保存图片
        with open(dir_save_img + filename, 'wb') as f:
            f.write(source)  
    except OSError as e:
        print('图片保存失败：' +  filename +'\n{e}'.format(e = e))

def save_page(page_title,source,filename):
    """
    保存到文件
    :param page_title:文章标题
    :param source: 结果
    :param filename: 保存的文件名
    """
    dir_save_page = sys.path[0] + '/ebiotrade_spider_result/'
    if not os.path.exists(dir_save_page):
        os.makedirs(dir_save_page)
    try:
        with open(dir_save_page + filename, 'w', encoding = 'utf-8') as f:
            f.write('<h2>'+page_title+'</h2>')  
            f.write(source)
    except  OSError as e:
        print('内容保存失败：' + filename + '\n{e}'.format(e = e))

def main():
    """
    遍历每一页索引页
    """
    print("ebiotrade_spider爬取开始！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

    # 用for循环遍历爬取不同分类下的文章
    for wd in range(5):
        if wd == 0:
            judge_name = 'judge_rdzm.txt'
            url_kw = 'http://www.ebiotrade.com/newsf/list.asp?boardid=46'
            num = 6
        if wd == 1:
            judge_name = 'judge_kp.txt'
            url_kw = 'http://www.ebiotrade.com/newsf/list.asp?boardid=10'
            num = 5 
        if wd == 2:
            judge_name = 'judge_sthb.txt'
            url_kw = 'http://www.ebiotrade.com/newsf/list.asp?boardid=8'
            num = 2
        if wd == 3:
            judge_name = 'judge_yjjz.txt'
            url_kw = 'http://www.ebiotrade.com/newsf/list.asp?boardid=3'
            num = 26
        if wd == 4:
            judge_name = 'judge_kydt.txt'
            url_kw = 'http://www.ebiotrade.com/newsf/list.asp?boardid=0'
            num = 41                   
        # 读取上次爬取时保存的用于判断爬取位置的字符串
        dir_judge = sys.path[0] + '/' + judge_name
        if not os.path.exists(dir_judge):
            with open(dir_judge, 'w', encoding = 'utf-8'):
                print('创建文件：' + dir_judge)
        with open(dir_judge, 'r', encoding = 'utf-8') as f:
                judge_last_time = f.read()
        # judge_last_time = 1
        index_page(num, judge_last_time, judge_name, url_kw)

    print("ebiotrade_spider爬取完毕，脚本退出！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))


if __name__ == '__main__':
    main()