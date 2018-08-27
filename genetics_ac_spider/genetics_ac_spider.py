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
    
    # judge_last_spider：用于判断是否爬取到上次爬取位置
    judge_last_spider = True
    
    for i in range(1,page):    
        print('正在爬取第' + str(i) + '页！')

        if not judge_last_spider:
            break

        # 判断url是否需要拼接
        judge_times = True
        if i == 1:
            url = 'http://www.genetics.ac.cn/xwzx/kyjz/index.html'
        else:
            url = 'http://www.genetics.ac.cn/xwzx/kyjz/index_' + str(i-1) + '.html'
        headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

        try:
            # 获取索引页
            response_index = requests.get(url, headers = headers)
            response_index.encoding = 'utf-8'
            # time.sleep(2)
            # print(response_index.url)
        except ConnectionError:
            print('index_page_ConnectionError:' + url)

        # 通过xpath获取索引页内的文章列表url
        html_index = etree.HTML(response_index.text)
        source_index = html_index.xpath('//td[@class = "right_wrap" ]//td[@align = "left"]//a/@href')

        # 写入当前爬取到的第一个文章url
        if i == 1:
            next_judge = source_index[0]
            with open('genetics_ac_spider/judge.txt', 'w', encoding = 'utf-8') as f:
                print("next_judge:\t" + next_judge)
                f.write(next_judge)

        for item in source_index:
            # 判断是否爬取到上次爬取位置,是的话judge_last_spider赋值为False      
            if item == judge:
                print("已爬取到上次爬取位置！")
                judge_last_spider = False
                break

            # item: ./201804/t20180424_5001331.html
            # print('item:', item, type(item))
            get_page(item)
        

def get_page(url):
    """
    提取文章内容
    :param url:文章假链接、提供真链接需要的参数
    """
    # item:./201804/t20180424_5001331.html
    # url_full：http://www.genetics.ac.cn/xwzx/kyjz/201808/t20180817_5056985.html
    url_replace = url.replace('./','')
    url_full = 'http://www.genetics.ac.cn/xwzx/kyjz/' + url_replace
    # print(url_full)
    headers = {'user-agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)'}

    # 获取文章
    article_response = requests.get(url_full, headers = headers)
    article_response.encoding = 'utf-8'
    time.sleep(1)

    # 通过正则表达式获取文章中需要的内容
    article_pattern = re.compile(r'<td align="center" valign="top" bgcolor="#FFFFFF" class="right_wrap">.*<td align="center" class="article_page">', re.S)

    article_result = article_pattern.search(article_response.text)
    if article_result:
        article_source = article_result.group()

        # 提取url中的t20160705_4635185作为文件名保存:'./201804/t20180424_5001331.html
        filename_pattren = re.compile(r'/t(.*.html)')
        filename = filename_pattren.search(url)
        print(filename.group(1))

        # 完整图片url:http://www.genetics.ac.cn/xwzx/kyjz/201808/W020180817816737360251.jpg
        # img_url.group(1):http://www.genetics.ac.cn/xwzx/kyjz/201808
        img_url_pattern = re.compile(r'(.*?)/t')
        img_url = img_url_pattern.search(url_full)
        print(img_url.group(1))
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
    print("genetics_ac_spider爬取开始！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

    # 读取上次爬取时保存的用于判断爬取位置的字符串
    # with open('genetics_ac_spider/judge.txt', 'r', encoding = 'utf-8') as f:
    #         judge = f.read()
    judge = 2
    index_page(2, judge)

    print("genetics_ac_spider爬取完毕，脚本退出！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))


if __name__ == '__main__':
    main()