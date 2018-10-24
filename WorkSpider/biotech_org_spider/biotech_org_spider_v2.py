# -*- encoding:utf-8 -*-

import re
import time
import requests
from lxml import etree
from requests import ConnectionError
import sys
import os


def index_page(page, judge, judge_name, url):
    """
    爬取索引页
    :param page:页码
    :param judge: 用于判断上次爬取位置
    :param judge_name: 判断爬取位置的数据保存名
    :param url: 爬取相关分类下的索引url
    """

    print('正在爬取第' + str(page) + '页索引页————>\t' + judge_name)
    full_url = url + str(page)
    # 获取索引页
    headers = {'user-agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; Zune 4.0; InfoPath.3; MS-RTC LM 8; .NET4.0C; .NET4.0E)'}
    try:
        response = requests.get(full_url, headers = headers)
        response.encoding = 'utf-8'
        time.sleep(2)
    except ConnectionError:
        print('index_page_ConnectionError:' + url)

    # 通过xpath获取索引页内的文章列表
    index_html = etree.HTML(response.text)
    index_source = index_html.xpath('//div[@id="zuob"]//li//a/@href')

    # 写入当前爬取到的第一个文章url
    if page == 1:
        next_judge = index_source[0]
        
        with open(sys.path[0] + '/' + judge_name, 'w', encoding = 'utf-8') as f:
            print(judge_name + "\t<————next_judge————>\t" + next_judge)
            f.write(next_judge)

    for item in index_source:
        # item:/information/155535
        # 判断是否爬取到上次爬取位置，是的话返回1
        if item == judge:
            print("已爬取到上次爬取位置！————>\t" + judge_name)
            return 1
            break

        get_page(item)

def get_page(url):
    """
    提取文章内容
    :param url:文章链接
    """
    # 组合url
    full_url = 'http://www.biotech.org.cn' + url
    # 获取文章内容
    headers = {'user-agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)'}

    article_response = requests.get(full_url, headers = headers)
    article_response.encoding = 'utf-8'
    time.sleep(1)

    # 通过正则表达式获取文章中需要的内容
    article_pattern = re.compile(r'<div id="zuob">.*.lightBox().*?</script>', re.S)

    article_result = article_pattern.search(article_response.text)
    if article_result:
        article_source = article_result.group()
        # 获取文章中所有的图片url链接:'http://159.226.80.12:80/imnews/NewsDataAction?Index=showImg&file=20180808141922.jpg'
        pattern_img = re.compile(r'<img(.*?)\ssrc="(.*?)"', re.I)
        findall_img = pattern_img.findall(article_source)
        # judge_img_get:判断能否获取图片
        judge_img_get = True
        for kw in findall_img:
            # kw[1]: http://www.bio360.net/storage/image/2018/08/FG3XNGQGmD2HxBMqFgNNmiuLNXjTWHU9cnblI8TV.png
            # 判断图片URL是否需要组合
            pattern_judge_img = re.compile(r'http', re.I)
            judge_img = pattern_judge_img.search(kw[1])
            if judge_img:
                url_full_img = kw[1]
            else:
                url_full_img =  'http://www.biotech.org.cn' + kw[1]

            # 图片保存名：dwNNY7cwzRcOcsjRwMFcceLF9qTvhyDP8HiHTgQc.png
            pattern_name_save_img = re.compile(r'.*\/(.*\.[jpbg][pmin]\w+)', re.I)
            try:
                name_save_img = pattern_name_save_img.search(kw[1]).group(1).replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','')
                # 获取图片
                response_img = requests.get(url_full_img, headers = headers).content

                # 保存图片
                save_img(response_img, name_save_img)

            except:
                print('图片网址有误:' + '\n' + url_full_img)
                # 如果图片获取不到，则赋值为false
                judge_img_get = False
                break

        # 如果获取得到图片，再进行下一步
        if judge_img_get:
            # 提取url中的数字作为文件名保存:'/information/155535'|155535
            filename_pattren = re.compile(r'\d+')
            filename = filename_pattren.search(url).group() + '.xml'
            filename = filename.replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','')
            # print(filename)     

            # 解析文章，提取有用的内容，剔除不需要的，返回内容列表
            list_article = parse_page(article_source)
            # 保存文章内容 
            save_page(list_article, filename)
        else:
            print('获取不到图片：' + url_page)

    else:
        print('get_page_error:' + full_url)

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
    title_article = html_source_local.xpath('//div[@id = "caption"]')[0].text
    title_article = '<title>' + title_article + '</title>\n'
    list_article.append(title_article)
    # print(type(title_article),title_article)

    # source_article：来源： 中科普瑞 / 作者：  2018-09-11
    source_article = html_source_local.xpath('//div[@id = "date"]')[0].text
    pattern_search_source = re.compile(r'来源：(.*?)发布者：', re.I|re.S)
    result_source = pattern_search_source.search(source_article).group(1).strip()
    pattern_search_time = re.compile(r'日期：(\d\d\d\d-\d\d-\d\d)', re.I|re.S)
    result_time = pattern_search_time.search(source_article).group(1).strip()
    pattern_search_user_ = re.compile(r'发布者：(.*?)日期：', re.I|re.S)
    result_user = pattern_search_user_.search(source_article).group(1).strip()
    source_article = '<source>' + '<source>' + result_source + '</source>' + '<user>' + result_user + '</user>' + '<time>' + result_time + '</time>' + '</source>\n'
    list_article.append(source_article)
    # print(type(source_article),source_article)

    # 通过正则表达式获取文章中需要的内容，即正文部分
    pattren_article_content = re.compile(r'<div id="nr">(.*)<script type="text/javascript">', re.I|re.S)
    source_article = pattren_article_content.search(source_local)
    # print('source_article.group():', type(source_article.group()), source_article.group())
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
            # print('match.group()', match.group())

            if img_real_name and match.group(1):
                pattern_kw_name_save_img = re.compile(r'.*\/(.*\.[jpbg][pmin]\w+)', re.I)
                kw_img_name = pattern_kw_name_save_img.search(match.group(1)).group(1).replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','')
                img_name = '<img src="./img/' + kw_img_name + '" />'
                # print('img_name:', type(img_name), img_name)
                return img_name

        # 匹配文章内容中的图片url，替换为本地图片url
        pattren_img_local = re.compile(r'<img.*?\ssrc="(.*?)".*?>{1}', re.I|re.S)
        source_local = pattren_img_local.sub(img_url_name, source_article)

            # 剔除不需要的内容
        def article_change(match):
            """
            匹配文章内容中的标签（a、img）除外，剔除其中的样式
            """
            # <p src="./img/13SsuHuXECVJ<p style="text-align: center;"> p
            # print(match.group(),match.group(1))
            name_tag = ''
            return name_tag

        pattren_article_change = re.compile(r'<([^/aip]\w*)\s*.*?>{1}')
        source_local = pattren_article_change.sub(article_change, source_local)

        pattren_article_change_1 = re.compile(r'</[^pa].*?>{1}')
        source_local = pattren_article_change_1.sub('', source_local)

        pattren_article_change_2 = re.compile(r'<p.*?>{1}')
        source_local = pattren_article_change_2.sub('<p>', source_local)

        # source_local = source_local.replace('</blockquote>','').replace('<blockquote>','').replace('style="background-color: rgb(255, 255, 255);"','').replace('align="center" style="text-align: center;"','').replace('<div>','').replace('</div>','').replace('<div class="article-content">','').replace('<div class="statement"','').replace('<div style="text-align: center;">','').strip().replace('&','&amp;').replace('style="text-align: center; "','').replace('style="font-size: 14px;"','').replace('style="text-align: left;"','')
        source_local = source_local.replace('&nbsp;','').strip().replace('&','&amp;')
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
    dir_save_img= sys.path[0] + '/biotech_org_spider_result/img/'
    if not os.path.exists(dir_save_img):
        os.makedirs(dir_save_img)
    try:
        # 保存图片
        with open(dir_save_img + filename, 'wb') as f:
            f.write(source)  
    except OSError as e:
        print('图片保存失败：' +  filename +'\n{e}'.format(e = e))
        
def save_page(list_article,filename):
    """
    保存到文件
    :param list_article: 结果
    :param filename: 保存的文件名
    """
    dir_save_page = sys.path[0] + '/biotech_org_spider_result/'
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
    print("biotech_org_spider爬取开始！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    # 用for循环遍历爬取相关分类下的文章
    for wd in range(6):
        # 重点关注
        if wd == 0:
            judge_name = 'judge_6.txt'
            url = 'http://www.biotech.org.cn/about/6/page/'    
        # 医药生物
        if wd == 1:
            judge_name = 'judge_106.txt'
            url = 'http://www.biotech.org.cn/topic/106/page/'
        # 农业生物
        if wd == 2:
            judge_name = 'judge_107.txt'
            url = 'http://www.biotech.org.cn/topic/107/page/'
        # 工业生物
        if wd == 3:
            judge_name = 'judge_108.txt'
            url = 'http://www.biotech.org.cn/topic/108/page/'
        # 基础与前沿
        if wd == 4:
            judge_name = 'judge_109.txt'
            url = 'http://www.biotech.org.cn/topic/109/page/'
            # 文献导读
        if wd == 5:
            judge_name = 'judge_110.txt'
            url = 'http://www.biotech.org.cn/topic/110/page/'
    
        # 读取上次爬取时保存的用于判断爬取位置的字符串
        # with open(sys.path[0] + '/' + judge_name, 'r', encoding = 'utf-8') as f:
                # judge = f.read()
        judge = 1
        for i in range(1,2):
            params = index_page(i, judge, judge_name, url)
            if params == 1:
                break
            print('保存第', str(i), '页索引页所有文章成功————>\t' + judge_name)  

    print("biotech_org_spider爬取完毕，脚本退出！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

if __name__ == '__main__':
    main()