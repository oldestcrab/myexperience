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



def get_index_page(index_page, last_judge, last_judge_name, index_url):
    """
    获取索引页
    :param index_page:索引页码
    :param last_judge: 获取上次爬取位置
    :param last_judge_name: 保存爬取位置的文件名
    :param index_url: 爬取index_url
    """
    
    # LAST_THRESHOLD：用于判断是否爬取到上次爬取位置
    LAST_THRESHOLD = True
    
    # 爬取全部索引页
    for index_page in range(1,index_page):    
        
        # 如果LAST_THRESHOLD为False，则退出循环！
        if not LAST_THRESHOLD:
            break
        print('正在爬取第' + str(index_page) + '页！')

        # 拼接url

        # 获取Headers
        with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
            user_agents_list = f.readlines()
            user_agent = random.choice(user_agents_list).strip()
        headers = {'user-agent':user_agent}

        try:
            # 获取索引页
            index_response = requests.get(index_url, headers = headers)
            index_response.encoding = 'utf-8'
            time.sleep(2)
            # print(response_index.url)
        except Exception as e:
            # 打印报错信息
            print(e.args)
            index_response = ''
            print('get index page error: ' + index_url)

        if index_response:
            # 通过xpath获取索引页内的文章列表url
            index_html = etree.HTML(index_response.text)
            index_source_list = index_html.xpath('//ul[@class="data-list"]/li')
            
            # 写入当前爬取到的第一个文章url
            if index_page == 1 and index_source_list:
                next_judge = index_source_list[0].xpath('./a/@href')[0].strip()
                with open(sys.path[0] + '/' + last_judge_name, 'w', encoding = 'utf-8') as f:
                    print("next_judge: " + next_judge)
                    f.write(next_judge)

            for index_source in index_source_list:
                # 获取文章部分url
                url_kw = index_source.xpath('./a/@href')[0].strip()

                # 判断是否爬取到上次爬取位置,是的话LAST_THRESHOLD赋值为False      
                if url_kw == last_judge:
                    print("已爬取到上次爬取位置！")
                    LAST_THRESHOLD = False
                    break

                try:
                    # 仅爬取2018年之后的文章
                    # 获取文章更新时间：2018-1-1
                    update_time = index_source.xpath('./span')[0].text
                    judge_time = re.search(r'(\d{4})-', update_time).group(1)
                except:
                    judge_time = 1997
                # print('judge_time: ', page_url)

                if int(judge_time) >= 2018:
                    page_url = 'http://skmn.fudan.edu.cn' + url_kw
                    # print('page_url: ', page_url)

                    # 获取索引页
                    get_article_page(page_url)
        
def get_article_page(page_url):
    """
    获取文章内容
    :param page_url:文章url
    """

    with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
        user_agents_list = f.readlines()
        user_agent = random.choice(user_agents_list).strip()
    headers = {'user-agent':user_agent}

    # 获取文章
    try:
        article_response = requests.get(page_url, headers = headers)
        article_response.encoding = 'utf-8'
        time.sleep(1)
    except:
        article_response = ''
        print('get article page error: ' + page_url)

    if article_response:
        # 通过正则表达式获取文章中需要的内容
        article_pattren = re.compile(r'<h1 style="color:333;font-size:18px">.*<div class="clearfix">', re.S|re.I)
        article_source = article_pattren.search(article_response.text)
        # print(source_article)

        if article_source:
            article_source = article_source.group()

            # 获取文章中所有的图片url链接
            img_pattern = re.compile(r'<img(.*?)\ssrc="(.*?)"', re.I|re.S)
            img_url_list = img_pattern.findall(article_source)
            # print('findall_img: ', findall_img)

            # IMG_EXISTS:判断能否获取图片
            IMG_EXISTS = True

            for img_part_url in img_url_list:
                # print('img_part_url[1]: ',img_part_url[1])
                
                # 判断图片URL是否需要组合，获取图片url
                img_judge_pattern = re.compile(r'http', re.I)
                img_judge = img_judge_pattern.search(img_part_url[1])
                if img_judge:
                    img_url = img_part_url[1]
                else:
                    img_url = 'http://skmn.fudan.edu.cn' + img_part_url[1]
                # print('img_url: ',img_url)

                img_save_name_pattern = re.compile(r'.*\/(.*\.[jpbg][pmin]\w+)', re.I)
                try:
                    # 图片保存名
                    img_save_name = img_save_name_pattern.search(img_part_url[1]).group(1).replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','')
                    # print('img_save_name: ',  img_save_name)

                    # 获取图片
                    response_img = requests.get(img_url, headers = headers).content


                    # 保存图片
                    save_article_img(response_img, img_save_name, IMG_SAVE_DIR)

                except:
                    print('图片网址有误: ' + img_url)
                    # 如果图片获取不到，则赋值为false
                    IMG_EXISTS = False
                    break

            # 如果获取得到图片，再进行下一步
            if IMG_EXISTS:

                # 提取文件名
                filename_pattern = re.compile(r'.*\/(.*)?', re.I)
                filename = filename_pattern.search(page_url).group(1) + '.html'
                filename = filename.replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','')
                # print('filename: ',  filename)

                # 解析文章，提取有用的内容，剔除不需要的，返回内容列表
                article_real_content = parse_article_page(article_source)

                # 保存文章内容 
                save_article_page(article_real_content, filename, PAGE_SAVE_DIR)

                # 存入mysql
                save_mysql(page_url, filename, PAGE_SAVE_DIR, ARTICLE_ORIGIN_WEBSITE)
            else:
                print('获取不到图片：' + page_url)
        else:
            print('get_page content error:' + page_url)

def parse_article_page(article_source):
    """
    提取文章内容
    :param article_source: 未筛选的文章内容
    :return: 筛选过后的文章内容
    """
    # 需要的内容保存到列表里，写入为.xml文件
    article_list = []
    article_list.append('<!DOCTYPE html>\n' + '<html>\n' + '<head>\n' + '<meta charset="utf-8"/>\n')

    # 利用etree.HTML，将字符串解析为HTML文档
    article_source_html = etree.HTML(article_source) 

    # 获取文章标题
    article_title = article_source_html.xpath('//h1')[0].text
    # print('title_article: ',  article_title)
    article_title = '<title>' + article_title + '</title>\n' + '</head>\n'
    article_list.append(article_title)

    # 获取文章来源
    article_origin = article_source_html.xpath('//div[@class="view-info"]/span')[0].text

    # 获取文章更新时间
    try:
        article_update_time_pattern = re.compile(r'\d{4}-\d{2}-\d{2}', re.I|re.S)
        article_update_time = article_update_time_pattern.search(article_origin).group().strip()
    except:
        article_update_time = ''
    # print('article_update_time: ',  article_update_time)

    # 获取文章作者
    article_user = ''

    # 获取文章来源网站
    article_origin_website = ''

    article_origin = '<body>\n' + '<div class = "source">' + article_origin_website + '</div>\n' + '<div class = "user">' + article_user + '</div>\n' + '<div class = "time">' + article_update_time + '</div>\n' + '<content>\n'
    # print('article_origin: ',  article_origin)
    article_list.append(article_origin)
    
    # 通过正则表达式获取文章中需要的内容，即正文部分
    article_content_pattern = re.compile(r'<div class="view-cnt">(.*)<div class="clearfix">', re.I|re.S)
    article_content = article_content_pattern.search(article_source)

    if article_content:
        article_content = article_content.group(1)

        def img_url_change(match):
            """
            匹配文章内容中的图片url，替换为本地url
            :return: 返回替换的文章url
            """
            img_origin_name_pattern = re.compile(r'\.[pjbg][pinm]', re.I)
            img_origin_name = img_origin_name_pattern.search(match.group())
            # print('match.group(1)', match.group(1))
    
            if img_origin_name and match.group(1):
                img_save_part_name_pattern = re.compile(r'.*\/(.*\.[jpbg][pmin]\w+)', re.I)
                img_save_part_name = img_save_part_name_pattern.search(match.group(1)).group(1).replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','')
                img_name = '<img src="' + IMG_CHANGE_DIR + img_save_part_name + '" />'
                # print('img_name: ', img_name)
                return img_name
    
        # 匹配文章内容中的图片url，替换为本地图片url
        local_img_pattern = re.compile(r'<img.*?\ssrc="(.*?)".*?>{1}', re.I|re.S)
        article_content = local_img_pattern.sub(img_url_change, article_content)
    
        # 剔除文章中不需要的内容
        def article_change(match):
            """
            匹配文章内容中的所有标签（a、img、p）除外，剔除掉
            """
            # <p src="./img/13SsuHuXECVJ<p style="text-align: center;"> p
            # print(match.group(),match.group(1))
            tag_name = ''
            return tag_name
    
        article_change_pattern = re.compile(r'<([^/aip]\w*)\s*.*?>{1}', re.I)
        article_content = article_change_pattern.sub(article_change, article_content)
    
        # 剔除所有除</ap>外的</>标签
        article_change_pattern_1 = re.compile(r'</[^pa].*?>{1}', re.I)
        article_content = article_change_pattern_1.sub('', article_content)
    
        # 剔除<P>标签的样式
        article_change_pattern_2 = re.compile(r'<p.*?>{1}', re.I)
        article_content = article_change_pattern_2.sub('<p>', article_content)
    
        # 剔除一些杂乱的样式
        article_content = article_content.replace('<i>','').strip()
    
        # 清洗后的正文
        article_real_content = article_content + '\n</content>\n' + '</body>\n' + '</html>\n'
        article_list.append(article_real_content)
    
    return article_list

def save_article_img(img_source, img_name, img_save_dir):
    """
    保存文章中的图片
    :param img_source: 图片二进制文件
    :param img_name: 图片存储名
    :param img_save_dir: 图片存储路径
    """
    if not os.path.exists(img_save_dir):
        os.makedirs(img_save_dir)
    try:
        # 保存图片
        with open(img_save_dir + img_name, 'wb') as f:
            f.write(img_source)  
    except Exception as e:
        print('图片保存失败：', e.args)

def save_article_page(article_real_content, filename, page_save_dir):
    """
    保存到文件
    :param article_real_content: 文章清洗过后的正文
    :param filename: 文件存储名
    :param page_save_dir: 文件存储路径
    """
    if not os.path.exists(page_save_dir):
        os.makedirs(page_save_dir)
    try:
        with open(page_save_dir + filename , 'w', encoding = 'utf-8') as f:
            for i in article_real_content:
                f.write(i)
    except  Exception as e:
        print('内容保存失败：', e.args)

def save_mysql(source_url, filename, local_url_dir, article_origin_website):
    """
    保存到文件
    :param source_url: 文章来源url
    :param filename: 文章本地存储名
    :param local_url_dir: 文章本地url路径
    :param article_origin_website: 文章来源网站
    """
    db = pymysql.connect(host='localhost', user='bmnars', password='vi93nwYV', port=3306, db='bmnars')
    cursor = db.cursor()
    local_url =  local_url_dir + filename  
    update_time = time.strftime('%Y-%m-%d',time.localtime())
    data = {
        'source_url':source_url,
        'local_url':local_url,
        'source':article_origin_website,
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
        print("save_mysql_failed:" + source_url)
        db.rollback()
    finally:
        cursor.close()      
        db.close()


# 图片存储路径
IMG_SAVE_DIR = sys.path[0] + '/skmn_fudan_spider_result/img/'
# IMG_SAVE_DIR = '/home/bmnars/data/skmn_fudan_spider_result/img/'
# 图片替换路径
IMG_CHANGE_DIR = './img/'
# IMG_CHANGE_DIR = '/home/bmnars/data/skmn_fudan_spider_result/img/'
# 文件存储路径
PAGE_SAVE_DIR = sys.path[0] + '/skmn_fudan_spider_result/'
# PAGE_SAVE_DIR = '/home/bmnars/data/skmn_fudan_spider_result/'
# 文章来源网站
ARTICLE_ORIGIN_WEBSITE = 'http://skmn.fudan.edu.cn'


def main():
    """
    遍历每一页索引页
    """
    print("skmn_fudan_spider爬取开始！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    start_time = time.time()

    # 用for循环遍历爬取不同分类下的文章
    for wd in range(1):

        if wd == 0:
            # 保存爬取位置的文件名
            last_judge_name = 'judge.txt'
            # 索引url
            index_url = 'http://skmn.fudan.edu.cn/Data/List/zxdt1'
            # 要爬取的索引总页数
            index_page = 2

        # 读取上次爬取时保存的用于判断爬取位置的字符串,如果不存在则创建
        judge_dir = sys.path[0] + '/' + last_judge_name
        if not os.path.exists(judge_dir):
            with open(judge_dir, 'w', encoding = 'utf-8'):
                print('创建文件：' + judge_dir) 
        # with open(judge_dir, 'r', encoding = 'utf-8') as f:
                # last_judge = f.read()

        last_judge = 1

        # 获取索引页
        get_index_page(index_page, last_judge, last_judge_name, index_url)

    print("skmn_fudan_spider爬取完毕，脚本退出！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    print('共用时：', time.time()-start_time)


if __name__ == '__main__':
    main()