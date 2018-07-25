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
        url = 'http://www.ioz.ac.cn/xwzx/kyjz/index.html'
    else:
        url = 'http://www.ioz.ac.cn/xwzx/kyjz/index_' + str(page) + '.html'
    print('正在爬取第' + str(page+1) + '页索引页')

    # 获取索引页
    headers = {'user-agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; Zune 4.0; InfoPath.3; MS-RTC LM 8; .NET4.0C; .NET4.0E)'}
    try:
        response = requests.get(url, headers = headers)
        response.encoding = 'utf-8'
        time.sleep(1)
    except ConnectionError:
        print('ConnectionError:' + url)

    # 通过xpath获取索引页内的文章列表
    index_html = etree.HTML(response.text)
    index_source = index_html.xpath('//table[@class = "hui12_sj2"]//a')

    # 写入当前爬取到的第一个文章url
    if page == 0:
        next_judge = index_source[0].xpath('@href')[0].replace('./','/',)
        with open('./ioz_ac_spider/judge.txt', 'w', encoding = 'utf-8') as f:
            print("next_judge:\t" + next_judge)
            f.write(next_judge)

    for item in index_source:
        # 获取索引页内所有文章的标题
        # index_title = item.text
        # 获取索引页内所有文章的url:'./201607/t20160705_4635185.html'
        index_url = item.xpath('@href')[0].replace('./','/',)
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
    full_url = 'http://www.ioz.ac.cn/xwzx/kyjz' + url
    # 获取文章内容
    headers = {'user-agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)'}

    article_response = requests.get(full_url, headers = headers)
    article_response.encoding = 'utf-8'
    time.sleep(1)

    # 通过正则表达式获取文章中需要的内容
    # article_pattern = re.compile(r'<table width="650" border="0" align="center" cellpadding="0" cellspacing="0">.*?<td class="bk_d1"></td>.*?<table width=', re.S)
    article_pattern = re.compile(r'<table width="650" border="0" align="center" cellpadding="0" cellspacing="0">.*createPageHTML', re.S)

    article_result = article_pattern.search(article_response.text)
    if article_result:
        article_source = article_result.group()

        # 提取url中的t20160705_4635185作为文件名保存:'./201607/t20160705_4635185.html'
        filename_pattren = re.compile(r'/t(.*).html')
        filename = filename_pattren.search(url)

        # 完整图片url:'http://www.ioz.ac.cn/xwzx/kyjz/201607/W020160705346461105213.jpg'
        # 获取图片url中的'/201607/'
        img_url_pattern = re.compile(r'(.*?)t')
        img_url = img_url_pattern.search(url)

        # 获取文章中所有的图片url链接:'W020180629309956323903.jpg'
        img_pattern = re.compile(r'<img style(.*?)src="(.*?)"', re.S)
        img_findall = img_pattern.findall(article_source)
        for kw in img_findall:
            # 组合url
            img_full_url = 'http://www.ioz.ac.cn/xwzx/kyjz' + img_url.group(1) + kw[1]

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
            # ./img/W020180622376479527977.jpg
            img_name  = 'src="./img/W' + match.group(1)
            # img_sub = img_pattern.sub(img_name, match)
            return img_name

        # 匹配文章内容中的图片url，替换为本地图片url
        img_name_pattern = re.compile(r'src="./W(.*?.[jpg, png]")',re.I)
        real_result = img_name_pattern.sub(img_url_name, article_source)

        # 保存文章内容 
        save_page(real_result, filename.group(1))
    else:
        print('error:' + full_url)

def save_img(result, filename):
    """
    保存文章中的图片
    :param result: 图片文件
    :param filename: 保存的图片名
    """
    img_save_full_name = './ioz_ac_spider/ioz_ac_spider_result/img/' + filename 
    with open(img_save_full_name, 'wb') as f:
        f.write(result)  
        
def save_page(html,filename):
    """
    保存到文件
    :param html: 结果
    """
    with open('./ioz_ac_spider/ioz_ac_spider_result/' + filename + '.html', 'w', encoding = 'utf-8') as f:
        f.write(html)

def main():
    """
    遍历每一页索引页
    """
    # 读取上次爬取时保存的用于判断爬取位置的字符串
    with open('./ioz_ac_spider/judge.txt', 'r', encoding = 'utf-8') as f:
            judge = f.read()

    for i in range(9):
        params = index_page(i, judge)
        print('保存第', str(i+1), '页索引页所有文章成功')  
        if params == 1:
            break

    print("爬取完毕，脚本退出！")

if __name__ == '__main__':
    main()
