# -*- encoding:utf-8 -*-

import re
import time
import requests
from lxml import etree
from requests import ConnectionError
import sys
import os
import random
import pymysql


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
        with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
            list_user_agents = f.readlines()
            user_agent = random.choice(list_user_agents).strip()
        headers = {'user-agent':user_agent}
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
        source_index = html_index.xpath('//td[@id = "cn5right03"]//td[@class="black_14"]/a/@href')

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

            # item: ./zxdt/201808/t20180828_5059967.html
            # print('item:', item, type(item))
            get_page(item, url_kw)
        
def get_page(url, url_kw):
    """
    提取文章内容
    :param url:文章假链接、提供真链接需要的参数
    :param url_kw: 不同分类下的url
    """
    # url:./zxdt/201808/t20180828_5059967.html
    # url_full：http://www.ibp.cas.cn/kyjz/zxdt/201808/t20180828_5059967.html
    url_full = url_kw + url.replace('./','')
    # print(url_full)
    # 随机选择user-agent
    with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
        list_user_agents = f.readlines()
        user_agent = random.choice(list_user_agents).strip()
    headers = {'user-agent':user_agent}

    # 获取文章
    response_article = requests.get(url_full, headers = headers)
    response_article.encoding = 'utf-8'
    time.sleep(1)

    # 通过正则表达式获取文章中需要的内容
    pattren_article = re.compile(r'<td align="center" valign="top" background.*td align="center" style=', re.S)
    source_article = pattren_article.search(response_article.text)

    if source_article:
        source_article = source_article.group()
        # print('1')
        pattren_url_img = re.compile(r'(.*?)/t')
        url_img = pattren_url_img.search(url_full)
        # 获取文章中所有的图片url链接: http://www.bio360.net/storage/image/2018/08/FG3XNGQGmD2HxBMqFgNNmiuLNXjTWHU9cnblI8TV.png
        pattern_img = re.compile(r'<img(.*?)\ssrc="(.*?)"', re.I)
        findall_img = pattern_img.findall(source_article)
        # print('findall_img:', type(findall_img), findall_img
        # judge_img_get:判断能否获取图片
        judge_img_get = True
        for kw in findall_img:
            # kw[1]: http://www.bio360.net/storage/image/2018/08/FG3XNGQGmD2HxBMqFgNNmiuLNXjTWHU9cnblI8TV.png
            # 判断图片URL是否需要组合
            # 判断图片URL是否需要组合
            pattern_judge_img = re.compile(r'http')
            judge_img = pattern_judge_img.search(kw[1])
            # url_full_img:http://www.ibp.cas.cn/kyjz/zxdt/201808/W020180828369497938690.jpg
            if judge_img :
                url_full_img = kw[1]
                pattern_name_save_img = re.compile(r'.*?(\w+.[jpbg][pmin]\w+)')
                name_save_img = pattern_name_save_img.search(kw[1]).group(1)
            else:
                # 图片网址：url_full_img
                url_full_img =  url_img.group(1) + kw[1].replace('./','/')
                # 图片保存名：name_save_img: W020180828369497938690.jpg
                name_save_img = kw[1].replace('./','')

            try:
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
            # 提取url中的154727作为文件名保存: http://www.bio360.net/article/154727
            pattren_filename = re.compile(r'.*\/(.*).html?', re.I)
            filename = pattren_filename.search(url_full).group(1) + '.html'
            filename = filename.replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','')
            # print('filename.group(1):', type(filename.group(1)), filename.group(1)
            # 解析文章，提取有用的内容，剔除不需要的，返回内容列表
            list_article = parse_page(source_article)
            # 保存文章内容 
            save_page(list_article, filename)
            save_mysql(url_full, filename)
        else:
            print('获取不到图片：' + url_full)
    else:
        print('get_page_error:' + url_full)


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
    title_article = html_source_local.xpath('//td[@class="black_20_600"]')[0].text
    title_article = '<title>' + title_article + '</title>\n' + '</head>\n'
    list_article.append(title_article)
    # print(type(title_article),title_article)

    # source_article：来源： 中科普瑞 / 作者：  2018-09-11
    # source_article = html_source_local.xpath('//div[@class="item-time col-sm-8"]')[0].text
    # pattern_search_source = re.compile(r'来源：(.*?)/{1}', re.I|re.S)
    # result_source = pattern_search_source.search(source_article).group(1).strip()
    result_time = html_source_local.xpath('//td[@class="font03"]/text()')[0].replace('|','').replace('【','').strip()
    # print(result_time)
    # pattern_search_user_ = re.compile(r'作者：(.*?)\d\d\d\d-\d\d-\d\d', re.I|re.S)
    # result_user = pattern_search_user_.search(source_article).group(1).replace('/','').replace('时间：','').strip()
    source_article = '<body>\n' + '<div class = "source">'  + '</div>\n' + '<div class = "user">'  + '</div>\n' + '<div class = "time">' + result_time + '</div>\n' + '<content>\n'
    list_article.append(source_article)
    # print(type(source_article),source_article)

    # 通过正则表达式获取文章中需要的内容，即正文部分
    pattren_article_content = re.compile(r'class="font04"(.*)<td align="center" style=', re.I|re.S)
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
                img_name = '<img src="/home/bmnars/data/ibp_cas_spider_result_v2/img/' + kw_img_name + '" />'
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
    dir_save_img = '/home/bmnars/data/ibp_cas_spider_result_v2/img/'
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
    dir_save_page = '/home/bmnars/data/ibp_cas_spider_result_v2/'
    if not os.path.exists(dir_save_page):
        os.makedirs(dir_save_page)
    try:
        with open(dir_save_page + filename , 'w', encoding = 'utf-8') as f:
            for i in list_article:
                f.write(i)
    except  OSError as e:
        print('内容保存失败：' + filename + '\n{e}'.format(e = e))




def save_mysql(url_source, url_local):
    """
    保存到文件
    :param url_source: 文章来源url
    :param url_local: 文章本地url
    """
    db = pymysql.connect(host='localhost', user='bmnars', password='vi93nwYV', port=3306, db='bmnars')
    cursor = db.cursor()
    url_local_full = '/home/bmnars/data/ibp_cas_spider_result_v2/' + url_local  
    update_time = time.strftime('%Y-%m-%d',time.localtime())
    data = {
        'source_url':url_source,
        'local_url':url_local_full,
        'source':'www.ibp.cas.cn',
	    'update_time':update_time
    }
    table = '_cs_bmnars_link_v2'
    keys = ','.join(data.keys())
    values = ','.join(['%s']*len(data))
    sql = 'INSERT INTO {table}({keys}) VALUES ({values}) on duplicate key update '.format(table=table, keys=keys, values=values)
    update = ', '.join(['{key} = %s'.format(key=key) for key in data]) + ';'
    sql += update
    # print(sql)
    try:
        if cursor.execute(sql,tuple(data.values())*2):
            db.commit()
    except:
        print("save_mysql_failed:" + url_source)
        db.rollback()
    
    finally:
        cursor.close()      
        db.close()

def main():
    """
    遍历每一页索引页
    """
    print("ibp_cas_spider爬取开始！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

    # 用for循环遍历爬取不同分类下的文章
    judge_name = 'judge_kyjz.txt'
    url_kw = 'http://www.ibp.cas.cn/kyjz/'
    num = 3
    dir_judge = sys.path[0] + '/' + judge_name
    if not os.path.exists(dir_judge):
        with open(dir_judge, 'w', encoding = 'utf-8'):
            print('创建文件：' + dir_judge)    
    with open(dir_judge, 'r', encoding = 'utf-8') as f:
        judge = f.read()
    # judge = 1
    index_page(num, judge, judge_name, url_kw)

    print("ibp_cas_spider爬取完毕，脚本退出！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))


if __name__ == '__main__':
    main()