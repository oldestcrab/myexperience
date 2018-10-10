# -*- encoding:utf-8 -*-

import re
import time
import requests
from lxml import etree
from requests import ConnectionError
import sys
import os


def index_page(page, judge):
    """
    爬取索引页
    :param page:页码
    :param judge: 用于判断上次爬取位置
    """
    if page == 0:
        url = 'http://www.cwca.org.cn/news/tidings/index.html'
    elif page < 5:
        url = 'http://www.cwca.org.cn/news/tidings/index_' + str(page) + '.html'
    else:
        url = 'http://www.cwca.org.cn/column.column.do?m=index&columnId=402883ef405147ed014051759803002a&page=' + str(page)
    print('正在爬取第' + str(page+1) + '页索引页')
    # print(url)
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
    index_source = index_html.xpath('//div[@class="listR"]//li/a')

    # 写入当前爬取到的第一个文章url:'/news/tidings/ff80808161da671a0163d9a89daa03b7.html'
    if page == 0:
        next_judge = index_source[0].xpath('@href')[0]
        with open(sys.path[0] + '/judge.txt', 'w', encoding = 'utf-8') as f:
            print("next_judge:\t" + next_judge)
            f.write(next_judge)

    for item in index_source:
        # 获取索引页内所有文章的标题
        # index_title = item.text
        # 获取索引页内所有文章的url:'/news/tidings/ff80808161da671a0163d9a89daa03b7.html'
        index_url = item.xpath('@href')[0]
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
    # 组合url:'http://www.cwca.org.cn/news/tidings/ff80808161da671a0163d9a89daa03b7.html'
    full_url = 'http://www.cwca.org.cn' + url
    # print(full_url)
    # 获取文章内容
    headers = {'user-agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)'}

    article_response = requests.get(full_url, headers = headers)
    # print( article_response.encoding, article_response.apparent_encoding)
    article_response.encoding = 'GB2312'
    time.sleep(1)

    # 通过正则表达式获取文章中需要的内容
    article_pattern = re.compile(r'<div class="listR">.*<div class="clear">', re.S)

    article_result = article_pattern.search(article_response.text)
    if article_result:
        article_source = article_result.group()

        # 提取url中的ff80808161da671a0163d9a89daa03b7.html作为文件名保存:'/news/tidings/ff80808161da671a0163d9a89daa03b7.html'
        filename_pattren = re.compile(r'/tidings/(.*).html')
        filename = filename_pattren.search(url)
        filename = filename.group(1) + '.xml'
        # print(filename)

        # 完整图片url:'http://www.cwca.org.cn/ckeditor/userfiles/images/20180608-2.jpg'
        # img_name_pattern = re.compile(r'(.*?)')
        # img_url = img_url_pattern.search(url)

        # 获取文章中所有的图片url链接: http://www.bio360.net/storage/image/2018/08/FG3XNGQGmD2HxBMqFgNNmiuLNXjTWHU9cnblI8TV.png
        pattern_img = re.compile(r'<img(.*?)\ssrc="(.*?)"', re.I)
        findall_img = pattern_img.findall(article_source)
        for kw in findall_img:
            # 判断图片URL是否需要组合
            pattern_judge_img = re.compile(r'http', re.I)
            judge_img = pattern_judge_img.search(kw[1])
            if judge_img:
                url_full_img = kw[1]
            else:
                url_full_img =  'http://www.cwca.org.cn' + kw[1]

            # 图片保存名：dwNNY7cwzRcOcsjRwMFcceLF9qTvhyDP8HiHTgQc.png
            pattern_name_save_img = re.compile(r'.*\/(.*\.[jpbg][pmin]\w+)', re.I)
            try:
                name_save_img = pattern_name_save_img.search(kw[1]).group(1)
                # 获取图片
                response_img = requests.get(url_full_img, headers = headers).content

                # 保存图片
                save_img(response_img, name_save_img)

            except:
                print('图片网址有误:' + url_full_img)


        # 解析文章，提取有用的内容，剔除不需要的，返回内容列表
        list_article = parse_page(article_source)
        # 保存文章内容 
        save_page(list_article, filename)
    else:
        print('正则匹配错误error:' + full_url)

def parse_page(source_local):
    """
    提取文章内容
    :param source_local: 文章内容
    """
    # 需要的内容保存到列表里，写入为.xml文件
    list_article = []
    list_article.append('<Document>')

    # 利用etree.HTML，将字符串解析为HTML文档
    html_source_local = etree.HTML(source_local) 
    # print(type(html_source_local),html_source_local)

    # title_article: 第四届发育和疾病的表观遗传学上海国际研讨会在沪隆重开幕
    title_article = html_source_local.xpath('//div[@class = "center_title"]')[0].text
    title_article = '<title>' + title_article + '</title>\n'
    list_article.append(title_article)
    # print(type(title_article),title_article)

    # source_article：来源： 中科普瑞 / 作者：  2018-09-11
    source_article_1 = html_source_local.xpath('//div[@class = "nr"]/span[1]')[0].text
    source_article_2 = html_source_local.xpath('//div[@class = "nr"]/span[2]')[0].text
    source_article_3 = html_source_local.xpath('//div[@class = "nr"]/span[3]')[0].text
    source_article = '<source>' + source_article_1 + source_article_2 + source_article_3 + '</source>\n'
    list_article.append(source_article)
    # print(type(source_article),source_article)

    # 通过正则表达式获取文章中需要的内容，即正文部分
    pattren_article_content = re.compile(r'<body>(.*)</body>', re.I|re.S)
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
            kw_img_name = pattern_kw_name_save_img.search(match.group(1)).group(1)
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
    source_local = source_local.replace('&nbsp;','').strip().replace('&','&amp;').replace('&amp;ldquo;','').replace('&amp;rdquo;','')

    # 清洗后的正文
    # print(source_local)
    source_local = '<content>\n' + source_local + '</content>\n'
    list_article.append(source_local)
    list_article.append('</Document>')

    return list_article

def save_img(result, filename):
    """
    保存文章中的图片
    :param result: 图片文件
    :param filename: 保存的图片名
    """
    img_save_full_name = sys.path[0] + '/cwca_org_spider_result/img/'
    if not os.path.exists(img_save_full_name):
        os.makedirs(img_save_full_name)
    try:
        with open(img_save_full_name + filename, 'wb') as f:
            f.write(result)  
    except:
        print('图片保存错误：' + filename)

def save_page(list_article,filename):
    """
    保存到文件
    :param list_article: 结果
    """
    dir_save_page = sys.path[0] + '/cwca_org_spider_result/'
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
    # 读取上次爬取时保存的用于判断爬取位置的字符串
    judge_name = 'judge.txt'    
    dir_judge = sys.path[0] + '/' + judge_name
    if not os.path.exists(dir_judge):
        with open(dir_judge, 'w', encoding = 'utf-8'):
            print('创建文件：' + dir_judge)
    # with open(dir_judge, 'r', encoding = 'utf-8') as f:
        # judge = f.read()
    judge = 2
    for i in range(7):
        params = index_page(i, judge)
        print('保存第', str(i+1), '页索引页所有文章成功')  
        if params == 1:
            break

    print("爬取完毕，脚本退出！")

if __name__ == '__main__':
    main()
