# -*- encoding:utf-8 -*-

import re
import time
import requests
from lxml import etree
from requests import ConnectionError
import sys
import os

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
        source_index = html_index.xpath('//tr[@class="outline_right_list2"]')

        # 写入当前爬取到的第一个文章url
        if i == 1:
            judge_next = html_index.xpath('//td[@class = "right_wrap" ]//td[@align = "left"]//a/@href')[0]
            # print(type(judge_next))
            with open(sys.path[0] + '/' + judge_name, 'w', encoding = 'utf-8') as f:
                print("judge_next:\t" + judge_next)
                f.write(judge_next)

        for item in source_index:
            # 判断是否爬取到上次爬取位置,是的话judge_last_spider赋值为False      
            if item == judge:
                print("已爬取到上次爬取位置！")
                judge_last_spider = False
                break
            url = item.xpath('.//a/@href')[0]
            source_time = item.xpath('.//td[@class="list_date2"]')[0].text.replace('(','').replace(')','')
            # item: ./201804/t20180424_5001331.html
            # print(type(str(url)))
            get_page(url, url_kw, source_time)
        
def get_page(url, url_kw, source_time):
    """
    提取文章内容
    :param url:文章假链接、提供真链接需要的参数
    :param url_kw: 不同分类下的url
    :param source_time: 文章发布时间
    """
    # url:./201804/t20180424_5001331.html
    # url_full：http://www.genetics.ac.cn/xwzx/kyjz/201808/t20180817_5056985.html
    url_full = url_kw + url.replace('./','')
    # print(url_full)
    headers = {'user-agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)'}

    # 获取文章
    response_article = requests.get(url_full, headers = headers)
    response_article.encoding = 'utf-8'
    time.sleep(1)

    # 通过正则表达式获取文章中需要的内容
    pattren_article = re.compile(r'<td align="center" valign="top" bgcolor="#FFFFFF" class="right_wrap">.*<td align="center" class="article_page">', re.S)
    source_article = pattren_article.search(response_article.text)

    if source_article:
        source_article = source_article.group()
        # url_img.group(1):http://www.genetics.ac.cn/xwzx/kyjz/201808
        pattren_url_img = re.compile(r'(.*?)/t')
        url_img = pattren_url_img.search(url_full)

        # 获取文章中所有的图片url链接:'./W020180817816737248277.jpg'
        pattern_img = re.compile(r'<img(.*?)\ssrc="(.*?)"', re.I)
        findall_img = pattern_img.findall(source_article)
        for kw in findall_img:
            # kw[1]: http://www.bio360.net/storage/image/2018/08/FG3XNGQGmD2HxBMqFgNNmiuLNXjTWHU9cnblI8TV.png
                # 判断图片URL是否需要组合
                pattern_judge_img = re.compile(r'http', re.I)
                judge_img = pattern_judge_img.search(kw[1])
                if judge_img:
                    url_full_img = kw[1]
                else:
                    url_full_img =  url_img.group(1) + kw[1].replace('./','/')

                # 图片保存名：dwNNY7cwzRcOcsjRwMFcceLF9qTvhyDP8HiHTgQc.png
                pattern_name_save_img = re.compile(r'.*\/(.*\.[jpbg][pmin]\w+)', re.I)
                try:
                    name_save_img = pattern_name_save_img.search(kw[1]).group(1).replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','')
                    # 获取图片
                    response_img = requests.get(url_full_img, headers = headers).content

                    # 保存图片
                    save_img(response_img, name_save_img)

                except:
                    print('图片网址有误:' + '\n' + url_full_img + '\n' + url_full)


        # 提取url中的20180424_5001331.html作为文件名保存: ./201804/t20180424_5001331.html
        pattren_filename = re.compile(r'/t(.*).html')
        filename = pattren_filename.search(url).group(1) + '.xml'
        filename = filename.replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','')
        # print(filename)

        # 解析文章，提取有用的内容，剔除不需要的，返回内容列表
        list_article = parse_page(source_article, source_time)
        # 保存文章内容 
        save_page(list_article, filename)

    else:
        print('error:' + url_full)

def parse_page(source_local, source_time):
    """
    提取文章内容
    :param source_local: 文章内容
    :param source_time: 文章发布时间
    """
    # 需要的内容保存到列表里，写入为.xml文件
    list_article = []
    list_article.append('<Document>')

    # 利用etree.HTML，将字符串解析为HTML文档
    html_source_local = etree.HTML(source_local) 
    # print(type(html_source_local),html_source_local)

    # title_article: 第四届发育和疾病的表观遗传学上海国际研讨会在沪隆重开幕
    title_article = html_source_local.xpath('//td[@class = "detail_title"]')[0].text
    title_article = '<title>' + title_article + '</title>\n'
    list_article.append(title_article)
    # print(type(title_article),title_article)

    # source_article：来源： 中科普瑞 / 作者：  2018-09-11
    # source_article = html_source_local.xpath('//div[@id = "date"]')[0].text
    source_article = '<source>' + '<source>'  + '</source>' + '<user>' + '</user>' + '<time>' + source_time + '</time>' + '</source>\n'
    list_article.append(source_article)
    # print(type(source_article),source_article)

    # 通过正则表达式获取文章中需要的内容，即正文部分
    pattren_article_content = re.compile(r'<div class=TRS_Editor>(.*)<td align="center"', re.I|re.S)
    source_article = pattren_article_content.search(source_local)

    if source_article:
        source_article = source_article.group(1)
        # print(source_article)
        def img_url_name(match):
            """
            匹配文章内容中的图片url，替换为本地url
            """
            # http://www.bio360.net/storage/image/2018/08/FG3XNGQGmD2HxBMqFgNNmiuLNXjTWHU9cnblI8TV.png
            pattren_img_local = re.compile(r'\.[pjbg][pinm]', re.I)
            img_real_name = pattren_img_local.search(match.group())
            # print('match.group(1)', match.group())

            if img_real_name and match.group(1):
                pattern_kw_name_save_img = re.compile(r'.*\/(.*\.[jpbg][pmin]\w+)', re.I)
                kw_img_name = pattern_kw_name_save_img.search(match.group(1)).group(1).replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','')
                img_name = '<img src="./img/' + kw_img_name + '" />'
                # print('img_name:', type(img_name), img_name)
                return img_name

        # 匹配文章内容中的图片url，替换为本地图片url
        pattren_img_local = re.compile(r'<img.*?\ssrc="(.*?)".*?>{1}', re.I|re.S)
        source_local = pattren_img_local.sub(img_url_name, source_article)

        # 剔除文章中不需要的内容
        def article_change(match):
            """
            匹配文章内容中的所有标签（a、img、p）除外，剔除掉
            """
            # <p src="./img/13SsuHuXECVJ<p style="text-align: center;"> p
            # print(match.group(),match.group(1))
            name_tag = ''
            return name_tag

        pattren_article_change = re.compile(r'<([^/aip]\w*)\s*.*?>{1}', re.I)
        source_local = pattren_article_change.sub(article_change, source_local)

        # 剔除所有除</p>外的</>标签
        pattren_article_change_1 = re.compile(r'</[^p].*?>{1}', re.I)
        source_local = pattren_article_change_1.sub('', source_local)

        # 剔除<P>标签的样式
        pattren_article_change_2 = re.compile(r'<p.*?>{1}', re.I)
        source_local = pattren_article_change_2.sub('<p>', source_local)

        # 剔除一些杂乱的样式
        source_local = source_local.replace('&nbsp;','').replace('<i>','').strip().replace('&','&amp;')

        # 清洗后的正文
        # print(source_local)
        source_local = '<content>\n' + source_local + '</content>\n'
        list_article.append(source_local)
        list_article.append('</Document>')

    return list_article

def save_img(source, filename):
    """
    保存文章中的图片
    :param source: 图片文件
    :param filename: 保存的图片名
    """
    img_save_full_name = sys.path[0] + '/genetics_ac_spider_result/img/'
    if not os.path.exists(img_save_full_name):
        os.makedirs(img_save_full_name)
    try:
        with open(img_save_full_name + filename, 'wb') as f:
            f.write(source)  
    except:
        print('图片保存错误：' + filename)
        
def save_page(list_article,filename):
    """
    保存到文件
    :param list_article: 结果
    :param filename: 保存的文件名
    """
    dir_save_page = sys.path[0] + '/genetics_ac_spider_result/'
    if not os.path.exists(dir_save_page):
        os.makedirs(dir_save_page)
    try:
        with open(dir_save_page + filename , 'w', encoding = 'utf-8') as f:
            for i in list_article:
                f.write(i)
    except  OSError as e:
        print('内容保存失败：' + filename + '\n{e}'.format(e = e))

def main():
    """
    遍历每一页索引页
    """
    print("genetics_ac_spider爬取开始！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

    # 用for循环遍历爬取不同分类下的文章
    for wd in range(2):
    # 读取上次爬取时保存的用于判断爬取位置的字符串
        if wd == 0:
            judge_name = 'judge_xwzx.txt'
            url_kw = 'http://www.genetics.ac.cn/xwzx/'
            num = 2
        if wd == 1:
            judge_name = 'judge_kyjz.txt'
            url_kw = 'http://www.genetics.ac.cn/xwzx/kyjz/'
            num = 3

        dir_judge = sys.path[0] + '/' + judge_name
        if not os.path.exists(dir_judge):
            with open(dir_judge, 'w', encoding = 'utf-8'):
                print('创建文件：' + dir_judge)
        # with open(dir_judge, 'r', encoding = 'utf-8') as f:
            # judge = f.read()
        judge = 2
        index_page(num, judge, judge_name, url_kw)

    print("genetics_ac_spider爬取完毕，脚本退出！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))


if __name__ == '__main__':
    main()