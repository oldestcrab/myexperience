# -*- encoding:utf-8 -*-

import re
import time
import requests
from lxml import etree
from requests import ConnectionError
import sys
import os
import random


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
        
        with open(sys.path[0] + '/judge.txt', 'w', encoding = 'utf-8') as f:
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
    with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
        list_user_agents = f.readlines()
        user_agent = random.choice(list_user_agents).strip()
    headers = {'user-agent':user_agent}
    article_response = requests.get(full_url, headers = headers)
    article_response.encoding = 'utf-8'
    time.sleep(1)

    # 通过正则表达式获取文章中需要的内容
    article_pattern = re.compile(r'<div class="noticecaption1">(.*)</a></strong></p>', re.S)

    article_result = article_pattern.search(article_response.text)
    if article_result:
        article_source = article_result.group(1)

        # 提取url中的t20160705_4635185作为文件名保存:'./201703/t20170303_25849.html'
        filename_pattren = re.compile(r'/t(.*).html')
        filename = filename_pattren.search(url).group(1)+ '.html'
        filename = filename.replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','')
        print(filename)

        # 完整图片url:'./W020161207373102355111.jpg'|http://www.kepu.net.cn/gb/overview/201612/W020161207373102364508.jpg
        # 获取图片url中的'/201612/'
        img_url_pattern = re.compile(r'(.*?)t')
        img_url = img_url_pattern.search(url)
        # print("img_url", type(img_url), img_url)

        # 获取文章中所有的图片url链接:'./W020161207373102355111.jpg'
        img_pattern = re.compile(r'<img style(.*?) src="./(.*?)"', re.S)
        img_findall = img_pattern.findall(article_source)
        judge_img_get = True
        for kw in img_findall:
            # 组合url
            # img_url.group(1):'/201703/', kw[1]:'W020170303482818708456.png'
            img_full_url = 'http://www.kepu.net.cn/gb/overview' + img_url.group(1) + kw[1]
            print("img_full_url", type(img_full_url), img_full_url)
            
            try:
                # 获取图片
                img_response = requests.get(img_full_url, headers = headers).content
                img_save_name = kw[1]

                # 保存图片
                save_img(img_response, img_save_name)
            except ConnectionError:
                print('图片网址有误:' + img_full_url)
                break
        if judge_img_get:
            list_article = parse_page(article_source)
            # 保存文章内容 
            save_page(list_article, filename)
        else:
            print('获取不到图片：' + full_url)
    else:
        print('get_page_error:' + full_url)

def parse_page(source_local):
    """
    提取文章内容
    :param source_local: 文章内容
    """
    # 需要的内容保存到列表里，写入为.xml文件
    list_article = []
    list_article.append('<!DOCTYPE html>\n' + '<html>\n' + '<head>\n' + '<meta charset="utf-8"/>\n')

    # 利用etree.HTML，将字符串解析为HTML文档
    html_source_local = etree.HTML(source_local) 
    # print(type(html_source_local),html_source_local)

    # title_article: 第四届发育和疾病的表观遗传学上海国际研讨会在沪隆重开幕
    title_article = html_source_local.xpath('//td [@class="black14600"]')[0].text
    title_article = '<title>' + title_article + '</title>\n' + '</head>\n'
    list_article.append(title_article)
    # print(type(title_article),title_article)

    # source_article：来源： 中科普瑞 / 作者：  2018-09-11
    source_article = html_source_local.xpath('//td[@class="hui12_sj2"]')[1].text
    pattern_search_source = re.compile(r'来源：(.*?)\|{1}', re.I|re.S)
    result_source = pattern_search_source.search(source_article).group(1).strip()
    pattern_search_time = re.compile(r'发布日期：(.*?)\|{1}', re.I|re.S)
    result_time = pattern_search_time.search(source_article).group(1).strip()
    # print(result_source,result_time)
    # pattern_search_user_ = re.compile(r'作者：(.*?)\d\d\d\d-\d\d-\d\d', re.I|re.S)
    # result_user = pattern_search_user_.search(source_article).group(1).replace('/','').replace('时间：','').strip()
    source_article = '<body>\n' + '<div class = "source">' + result_source + '</div>\n' + '<div class = "user">'  + '</div>\n' + '<div class = "time">' + result_time + '</div>\n' + '<content>\n'
    list_article.append(source_article)
    # print(type(source_article),source_article)

    # 通过正则表达式获取文章中需要的内容，即正文部分
    pattren_article_content = re.compile(r'<div class=TRS_Editor>(.*)<td align="center" style="padding-top:10px"', re.I|re.S)
    source_article = pattren_article_content.search(source_local)

    if source_article:
        source_article = source_article.group(1)
        # print('2')
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
    
        # 剔除所有除</ap>外的</>标签
        pattren_article_change_1 = re.compile(r'</[^pa].*?>{1}', re.I)
        source_local = pattren_article_change_1.sub('', source_local)
    
        # 剔除<P>标签的样式
        pattren_article_change_2 = re.compile(r'<p.*?>{1}', re.I)
        source_local = pattren_article_change_2.sub('<p>', source_local)
    
        # 剔除一些杂乱的样式
        source_local = source_local.replace('&nbsp;','').replace('id="content">','').strip()
        pattern_del_part_1 = re.compile(r'.TRS_Editor.*;font-size:10.5pt;}', re.I|re.S)
        # 清洗后的正文
        source_local = pattern_del_part_1.sub('',source_local)
        # print(source_local)
        source_local = source_local + '\n</content>\n' + '</body>\n' + '</html>\n'
        list_article.append(source_local)
    # print('1')
    return list_article

def save_img(source, filename):
    """
    保存文章中的图片
    :param source: 图片文件
    :param filename: 保存的图片名
    """
    dir_save_img = sys.path[0] + '/kepu_net_spider_result/img/'
    if not os.path.exists(dir_save_img):
        os.makedirs(dir_save_img)
    try:
        # 保存图片
        with open(dir_save_img + filename, 'wb') as f:
            f.write(source)  
    except OSError as e:
        print('图片保存失败：' + filename +'\n{e}'.format(e = e))

        
def save_page(list_article,filename):
    """
    保存到文件
    :param list_article: 结果
    :param filename: 保存的文件名
    """
    dir_save_page = sys.path[0] + '/kepu_net_spider_result/'
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
    judge_name = 'judge.txt'
    dir_judge = sys.path[0] + '/' + judge_name
    if not os.path.exists(dir_judge):
        with open(dir_judge, 'w', encoding = 'utf-8'):
            print('创建文件：' + dir_judge) 
    # 读取上次爬取时保存的用于判断爬取位置的字符串
    # with open(dir_judge, 'r', encoding = 'utf-8') as f:
            # judge = f.read()
    judge = 2

    for i in range(6):
        params = index_page(i, judge)
        if params == 1:
            break
        print('保存第', str(i+1), '页索引页所有文章成功')  

    print("爬取完毕，脚本退出！")

if __name__ == '__main__':
    main()