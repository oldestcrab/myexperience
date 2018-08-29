# -*- encoding:utf-8 -*-

import re
import time
import requests
from lxml import etree
from requests import ConnectionError


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

        # 判断url是否需要拼接
        if i == 1:
            url = url_kw + 'index.html'
        else:
            url = url_kw + 'index_' + str(i-1) + '.html'
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
        source_index = html_index.xpath('//div[@class="gzdtbox_ej"]//span[@class="floatleft"]/a/@href')

        # 写入当前爬取到的第一个文章url
        if i == 1 and source_index:
            judge_next = source_index[0]
            with open('whiov_ac_spider/' + judge_name, 'w', encoding = 'utf-8') as f:
                print("judge_next:\t" + judge_next)
                f.write(judge_next)

        for item in source_index:
            # 判断是否爬取到上次爬取位置,是的话judge_last_spider赋值为False      
            if item == judge:
                print("已爬取到上次爬取位置！")
                judge_last_spider = False
                break

            # item: ./201804/t20180428_5004366.html
            # print('item:', item, type(item))
            get_page(item, url_kw)
        
def get_page(url, url_kw):
    """
    提取文章内容
    :param url:文章假链接、提供真链接需要的参数
    :param url_kw: 不同分类下的url
    """
    # url:./201804/t20180428_5004366.html
    # url_full：http://www.whiov.ac.cn/xwdt_105286/kydt/201804/t20180428_5004366.html
    url_full = url_kw + url.replace('./','')
    # print(url_full)
    headers = {'user-agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)'}

    # 获取文章
    response_article = requests.get(url_full, headers = headers)
    response_article.encoding = 'utf-8'
    time.sleep(1)

    # 通过正则表达式获取文章中需要的内容
    pattren_article = re.compile(r'<div class="xl_content">.*<div class="fenyedisplay-1"', re.S)
    source_article = pattren_article.search(response_article.text)

    if source_article:
        source_article = source_article.group()
        # url_img.group(1):http://www.whiov.ac.cn/xwdt_105286/kydt/201804
        pattren_url_img = re.compile(r'(.*?)/t')
        url_img = pattren_url_img.search(url_full)

        # 获取文章中所有的图片url链接: ./W020131016426608541479.jpg
        pattern_img = re.compile(r'<img(.*?)\ssrc="(.*?)"', re.S)
        findall_img = pattern_img.findall(source_article)
        for kw in findall_img:
            # kw: ./W020131016426608541479.jpg

            # 判断图片URL是否需要组合
            pattern_judge_img = re.compile(r'http')
            judge_img = pattern_judge_img.search(kw[1])
            # url_full_img:http://www.whiov.ac.cn/xwdt/kydt/201306/W020131016426608541479.jpg
            if judge_img is None:
                # 图片网址：url_full_img
                url_full_img =  url_img.group(1) + kw[1].replace('./','/')
                # 图片保存名：name_save_img: W020131016426608541479.jpg
                name_save_img = kw[1].replace('./','')
            else:
                url_full_img = kw[1]
                pattern_name_save_img = re.compile(r'.*?(\w+.[jpbg][pmin]\w+)')
                name_save_img = pattern_name_save_img.search(kw[1]).group(1)
            # print(url_full_img)
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
            # ./W020131016426608541479.jpg
            pattren_img_local = re.compile(r'.[pjbg][pinm]')
            img_real_name = pattren_img_local.search(match.group())

            if img_real_name:
                img_name  = ' src="./img/' + match.group(1).replace('./','') + '"'
                return img_name

        # 匹配文章内容中的图片url，替换为本地图片url
        pattren_img_local = re.compile('\ssrc="(.*?)"')
        source_local = pattren_img_local.sub(url_img_name, source_article)

        # 提取url中的20180428_5004366.html作为文件名保存: ./201804/t20180428_5004366.html
        pattren_filename = re.compile(r'/t(.*.html)')
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
    name_save_img = 'whiov_ac_spider/whiov_ac_spider_result/img/' + filename 
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
        with open('whiov_ac_spider/whiov_ac_spider_result/' + filename, 'w', encoding = 'utf-8') as f:
            f.write(source)
    except  OSError as e:
        print('内容保存失败：' + filename + '\n{e}'.format(e = e))

def main():
    """
    遍历每一页索引页
    """
    print("whiov_ac_spider爬取开始！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

    # 用for循环遍历爬取不同分类下的文章
    for wd in range(2):
    # 读取上次爬取时保存的用于判断爬取位置的字符串
        if wd == 0:
            judge_name = 'judge_kydt.txt'
            url_kw = 'http://www.whiov.ac.cn/xwdt_105286/kydt/'
            num = 3
        if wd == 1:
            judge_name = 'judge_kyjz.txt'
            url_kw = 'http://www.whiov.ac.cn/kyjz_105338/'
            num = 2

        with open('whiov_ac_spider/' + judge_name, 'r', encoding = 'utf-8') as f:
                judge = f.read()
        index_page(num, judge, judge_name, url_kw)

    print("whiov_ac_spider爬取完毕，脚本退出！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))


if __name__ == '__main__':
    main()