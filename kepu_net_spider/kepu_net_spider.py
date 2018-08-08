# -*- encoding:utf-8 -*-

import re
import time
import requests
from lxml import etree
from requests import ConnectionError


def index_page(page, judge):
    """
    爬取索引页
    :param page:页码
    :param judge: 用于判断上次爬取位置
    """
    if page == 0:
        url = 'http://www.kepu.net.cn/gb/overview/index.html'
    else:
        url = 'http://www.kepu.net.cn/gb/overview/index_' + str(page) + '.html'
    print('正在爬取第' + str(page+1) + '页索引页')

    # 获取索引页
    headers = {'user-agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; Zune 4.0; InfoPath.3; MS-RTC LM 8; .NET4.0C; .NET4.0E)'}
    try:
        response = requests.get(url, headers = headers)
        response.encoding = 'utf-8'
        time.sleep(1)
    except ConnectionError:
        print('index_page_ConnectionError:' + url)

    # 通过xpath获取索引页内的文章列表
    index_html = etree.HTML(response.text)
    index_source = index_html.xpath('//div[@id = "wq_nr_left1"]/a[1]')

    # 写入当前爬取到的第一个文章url
    if page == 0:
        next_judge = index_source[0].xpath('@href')[0].replace('./','/',)
        # print('next_judge', next_judge, type(next_judge))
        
        with open('./kepu_net_spider/judge.txt', 'w', encoding = 'utf-8') as f:
            print("next_judge:\t" + next_judge)
            f.write(next_judge)

    for item in index_source:
        # 获取索引页内所有文章的url:'./201703/t20170303_25849.html'|/201703/t20170303_25849.html
        index_url = item.xpath('@href')[0].replace('./','/',)
        # print("index_url", type(index_url), index_url)

        # 判断是否爬取到上次爬取位置，是的话返回1
        if index_url == judge:
            print("已爬取到上次爬取位置！")
            return 1
            break

        get_page(index_url)

def get_page(url):
    """
    提取文章内容
    :param url:文章链接
    """
    # 组合url
    full_url = 'http://www.kepu.net.cn/gb/overview' + url
    # print("full_url", type(full_url), full_url)

    # 获取文章内容
    headers = {'user-agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)'}

    article_response = requests.get(full_url, headers = headers)
    article_response.encoding = 'utf-8'
    time.sleep(1)

    # 通过正则表达式获取文章中需要的内容
    article_pattern = re.compile(r'<div class="noticecaption1">.*</a></strong></p>', re.S)

    article_result = article_pattern.search(article_response.text)
    if article_result:
        article_source = article_result.group()

        # 提取url中的t20160705_4635185作为文件名保存:'./201703/t20170303_25849.html'
        filename_pattren = re.compile(r'/t(.*html)')
        filename = filename_pattren.search(url)
        # print("filename", type(filename), filename)

        # 完整图片url:'./W020161207373102355111.jpg'|http://www.kepu.net.cn/gb/overview/201612/W020161207373102364508.jpg
        # 获取图片url中的'/201612/'
        img_url_pattern = re.compile(r'(.*?)t')
        img_url = img_url_pattern.search(url)
        # print("img_url", type(img_url), img_url)

        # 获取文章中所有的图片url链接:'./W020161207373102355111.jpg'
        img_pattern = re.compile(r'<img style(.*?) src="./(.*?)"', re.S)
        img_findall = img_pattern.findall(article_source)
        for kw in img_findall:
            # 组合url
            # img_url.group(1):'/201703/', kw[1]:'W020170303482818708456.png'
            img_full_url = 'http://www.kepu.net.cn/gb/overview' + img_url.group(1) + kw[1]
            # print("img_full_url", type(img_full_url), img_full_url)
            
            try:
                # 获取图片
                img_response = requests.get(img_full_url, headers = headers).content
                img_save_name = kw[1]

                # 保存图片
                save_img(img_response, img_save_name)
            except ConnectionError:
                print('图片网址有误:' + img_full_url)

        def img_url_name(match):
            """
            匹配文章内容中的图片url，替换为本地url
            """
            # ./W020170303482818708456.png
            img_real_pattern = re.compile(r'.[pjb][pnm]')
            img_real_name = img_real_pattern.search(match.group())
            # print("img_real_name", type(img_real_name), img_real_name)

            if img_real_name is not None:
                img_sub_pattern = re.compile('.*\/(\w+.*?\.\w+)')
                img_sub_name = img_sub_pattern.search(match.group())
                img_name  = ' src="./img/' + img_sub_name.group(1) + '"'
                # print("img_name", type(img_name), img_name)

                return img_name

        # 匹配文章内容中的图片url，替换为本地图片url
        # img_pattern = re.compile(r'<img(.*?)\ssrc="(.*?)"', re.S)
        img_real_pattern = re.compile('\ssrc="(.*?)"')
        real_result = img_real_pattern.sub(img_url_name, article_source)

        # 保存文章内容 
        save_page(real_result, filename.group(1))

    else:
        print('get_page_error:' + full_url)

def save_img(result, filename):
    """
    保存文章中的图片
    :param result: 图片文件
    :param filename: 保存的图片名
    """
    img_save_full_name = './kepu_net_spider/kepu_net_spider_result/img/' + filename 
    with open(img_save_full_name, 'wb') as f:
        f.write(result)  
        
def save_page(html,filename):
    """
    保存到文件
    :param html: 结果
    """
    with open('./kepu_net_spider/kepu_net_spider_result/' + filename, 'w', encoding = 'utf-8') as f:
        f.write(html)

def main():
    """
    遍历每一页索引页
    """
    # 读取上次爬取时保存的用于判断爬取位置的字符串
    with open('./kepu_net_spider/judge.txt', 'r', encoding = 'utf-8') as f:
            judge = f.read()
    # judge = 2

    for i in range(6):
        params = index_page(i, judge)
        if params == 1:
            break
        print('保存第', str(i+1), '页索引页所有文章成功')  

    print("爬取完毕，脚本退出！")

if __name__ == '__main__':
    main()