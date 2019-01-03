# -*- coding:utf-8 -*-

import sys
import os
import requests
import time
import random
import threading
from lxml import etree
import pymysql
import re
from queue import Queue
import redis


def get_proxy():
    """
    return: proxy
    """
    try:
        response = requests.get('http://127.0.0.1:5555/random')
        return response.text
    except:
        db = redis.StrictRedis(
            host='localhost', port=6379, decode_responses=True)
        result = db.zrangebyscore('proxies', 100, 100)
        if len(result):
            return random.choice(result)
        else:
            result = db.zrangebyscore('proxies', 0, 100)
            if len(result):
                return random.choice(result)


def get_index_page(index_queue, page_queue):
    """
    :param index_queue:索引页码队列
    :param page_queue: 文章url队列
    """
    # 获取队列中的url直到为空
    while not index_queue.empty():
        # 索引页面url
        url = index_queue.get(False)

        # 获取代理
        proxy = get_proxy()
        print('proxy: ', proxy)
        proxies = {'http': 'http://' + proxy.strip(), 'https': 'https://' + proxy.strip()}

        # 获取headers
        with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
            user_agent_list = f.readlines()
        user_agent = random.choice(user_agent_list).strip()
        headers = {'user-agent':user_agent}

        try :
            # 获取index页面
            index_response = requests.get(url, headers = headers, proxies = proxies, timeout = 4)
            index_response.encoding = 'utf-8'
            # print(index_response.text)

        except Exception as e:
            # 打印报错信息
            # print(e.args)
            print('try again: ', url)
            # 把url放入页码队列，直到获取为止
            index_queue.put(url)
            index_response = ''
        
        # 确保能获取到页面再进行下一步
        if index_response:
            try:
                html_response = etree.HTML(index_response.text)
                try:
                    # 获取文章url
                    url_list = html_response.xpath('//ul[@class="data-list"]/li')
                    # print(url_list)
                    for i in url_list:
                        # 获取文章更新时间：2018-1-1
                        update_time = i.xpath('./span')[0].text
                        # print(update_time)
                        # judge_time: 2018
                        judge_time = re.search(r'(\d{4})-', update_time).group(1)
                        # 爬取文章更新时间为2018年之后的
                        if int(judge_time) >= 2018:
                            # 获取文章url
                            # url = i.xpath('./a/@href')[0]
                            page_url = 'http://skmn.fudan.edu.cn' + i.xpath('./a/@href')[0].strip()
                            page_queue.put(page_url)
                except:
                    print('获取文章url出错')
            except:
                print('页面解析出错')


class ThreadParse(threading.Thread):
    def __init__(self, page_queue, lock):
        """
        初始化
        :param name_thread: 采集线程名字
        :param queue_data: 采集队列
        :param lock: 线程锁
        """
        super(ThreadParse, self).__init__()
        self.page_queue = page_queue
        self.lock = lock

    def run(self):
        # 判断只要队列不为空，就一直循环
        while not PARSE_EXIT:
            try:
                # 从页码队列中获取数据，False队列为空抛出一个为空的异常
                url = self.page_queue.get(False)
                print(url)
                self.get_page(url)
            except:
                pass

    def get_page(self, url):
        """
        :param url:从解析队列中获取到的url
        """
        # 获取代理
        proxy = get_proxy()
        print('proxy: ', proxy)
        proxies = {'http': 'http://' + proxy.strip(), 'https': 'https://' + proxy.strip()}

        # 获取headers
        with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
            user_agent_list = f.readlines()
        user_agent = random.choice(user_agent_list).strip()
        headers = {'user-agent':user_agent}

        try :
            # 获取文章页面
            page_response = requests.get(url, headers = headers, proxies = proxies, timeout = 4)
            page_response.encoding = 'utf-8'
            # print(index_response.text)

        except Exception as e:
            # 打印报错信息
            # print(e.args)
            print('try again: ', url)
            # 把url放入页码队列，直到获取为止
            self.page_queue.put(url)
            page_response = ''

        if page_response:
            # 通过正则表达式获取文章中需要的内容
            pattren_article = re.compile(r'<h1 style="color:333;font-size:18px">.*<div class="clearfix">', re.S|re.I)
            source_article = pattren_article.search(page_response.text)
            # print(source_article)
            if source_article:
                source_article = source_article.group()
                # 获取文章中所有的图片url链接: http://skmn.fudan.edu.cn/Assets/userfiles/sys_eb538c1c-65ff-4e82-8e6a-a1ef01127fed/images/news/67.jpg
                pattern_img = re.compile(r'<img(.*?)\ssrc="(.*?)"', re.I)
                findall_img = pattern_img.findall(source_article)
                # print('findall_img:', type(findall_img), findall_img)
                # judge_img_get:判断能否获取图片
                judge_img_get = True
                for kw in findall_img:
                    # kw[1]: /Assets/userfiles/sys_eb538c1c-65ff-4e82-8e6a-a1ef01127fed/images/news/67.jpg
                    # 判断图片URL是否需要组合
                    # print('kw[1]',kw[1])
                    pattern_judge_img = re.compile(r'http', re.I)
                    judge_img = pattern_judge_img.search(kw[1])
                    if judge_img:
                        url_full_img = kw[1]
                    else:
                        url_full_img =  'http://skmn.fudan.edu.cn' + kw[1]
                        # 图片保存名：dwNNY7cwzRcOcsjRwMFcceLF9qTvhyDP8HiHTgQc.png
                    print('url_full_img: ', url_full_img)
                    pattern_name_save_img = re.compile(r'.*\/(.*\.[jpbg][pmin]\w+)', re.I)
                    try:
                        name_save_img = pattern_name_save_img.search(kw[1]).group(1).replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','')
                        print('name_save_img:', name_save_img)
                        # 获取图片
                        response_img = requests.get(url_full_img, headers = headers).content
                        # 保存图片
                        print(1)
                        self.save_img(response_img, name_save_img)
                    except Exception as e:
                        print(e.args)

                        print('图片网址有误:' + '\n' + url_full_img)
                        # 如果图片获取不到，则赋值为false
                        judge_img_get = False
                        break
                # 如果获取得到图片，再进行下一步
                if judge_img_get:
                    # 提取url中的154727作为文件名保存: http://www.bio360.net/article/154727
                    pattren_filename = re.compile(r'.*\/.*?=(.*)?', re.I)
                    filename = pattren_filename.search(url_full).group(1) + '.html'
                    filename = filename.replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','')
                    # print(filename)
                    # 解析文章，提取有用的内容，剔除不需要的，返回内容列表
                    list_article = parse_page(source_article)
                    # 保存文章内容 
                    save_page(list_article, filename)
                else:
                    print('获取不到图片：' + url_full)
            else:
                print('get_page content error:' + url_full)

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
        title_article = html_source_local.xpath('//div[@class = "center_title"]')[0].text
        title_article = '<title>' + title_article + '</title>\n' + '</head>\n'
        list_article.append(title_article)
        # print(type(title_article),title_article)

        # source_article：来源： 中科普瑞 / 作者：  2018-09-11
        source_article = html_source_local.xpath('//div[@class="item-time col-sm-8"]')[0].text
        pattern_search_source = re.compile(r'来源：(.*?)/{1}', re.I|re.S)
        result_source = pattern_search_source.search(source_article).group(1).strip()
        pattern_search_time = re.compile(r'\d\d\d\d-\d\d-\d\d', re.I|re.S)
        result_time = pattern_search_time.search(source_article).group().strip()
        pattern_search_user_ = re.compile(r'作者：(.*?)\d\d\d\d-\d\d-\d\d', re.I|re.S)
        result_user = pattern_search_user_.search(source_article).group(1).replace('/','').replace('时间：','').strip()
        source_article = '<body>\n' + '<div class = "source">' + result_source + '</div>\n' + '<div class = "user">' + result_user + '</div>\n' + '<div class = "time">' + result_time + '</div>\n' + '<content>\n'
        list_article.append(source_article)
        # print(type(source_article),source_article)

        # 通过正则表达式获取文章中需要的内容，即正文部分
        pattren_article_content = re.compile(r'<div id="nr">(.*)<script type="text/javascript">', re.I|re.S)
        source_article = pattren_article_content.search(source_local)

        if source_article:
            source_article = source_article.group(1)

            def img_url_name(match):
                """
                匹配文章内容中的图片url，替换为本地url
                """
                # http://skmn.fudan.edu.cn/Assets/userfiles/sys_eb538c1c-65ff-4e82-8e6a-a1ef01127fed/images/news/67.jpg
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
            source_local = source_local.replace('&nbsp;','').replace('&','&amp;').strip()

            # 清洗后的正文
            print(source_local)
            source_local = source_local + '\n</content>\n' + '</body>\n' + '</html>\n'
            list_article.append(source_local)

        return list_article

    def save_img(self, source, filename):
        """
        保存文章中的图片
        :param source: 图片文件
        :param filename: 保存的图片名
        """
        dir_save_img = sys.path[0] + '/skmn_fudan_spider_result/img/'
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
        dir_save_page = sys.path[0] + '/skmn_fudan_spider_result/'
        if not os.path.exists(dir_save_page):
            os.makedirs(dir_save_page)
        try:
            with open(dir_save_page + filename , 'w', encoding = 'utf-8') as f:
                for i in list_article:
                    f.write(i)
        except  OSError as e:
            print('内容保存失败：' + filename + '\n{e}'.format(e = e))

        save_mysql(url_page, filename)


    def save_mysql(url_source, url_local):
        """
        保存到文件
        :param url_source: 文章来源url
        :param url_local: 文章本地url
        """
        db = pymysql.connect(host='localhost', user='bmnars', password='vi93nwYV', port=3306, db='bmnars')
        cursor = db.cursor()
        url_local_full = '/home/bmnars/data/skmn_fudan_spider_result_v2/' + url_local  
        update_time = time.strftime('%Y-%m-%d',time.localtime())
        data = {
            'source_url':url_source,
            'local_url':url_local_full,
            'source':'www.bio360.net',
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

PARSE_EXIT = False

def main():
    """
    遍历每一页
    """
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    print('skmn_fudan_spider开始爬取!')
    start_time = time.time()

    # 索引页码队列
    index_queue = Queue()

    # 文章url队列
    page_queue = Queue()

    # 锁
    lock = threading.Lock()

    # 存储4个解析线程的列表集合 
    thread_parse = []
    for i in range(4):
        # 线程定义
        thread = ThreadParse(page_queue, lock)
        # 启动线程
        thread.start()
        # 添加线程到列表
        thread_parse.append(thread)
    
    # 索引页面url
    url = 'http://skmn.fudan.edu.cn/Data/List/zxdt1'
    # 把url放入索引页码队列
    index_queue.put(url)

    get_index_page(index_queue, page_queue)

    # 等待page_queue队列为空
    while not page_queue.empty():
        pass
    # 如果page_queue队列为空,采集线程退出循环
    global PARSE_EXIT
    PARSE_EXIT = True
    print('page_queue为空！')

    for thread in thread_parse:
        # 等待采集线程完成退出，阻塞主线程，其他线程不受影响
        thread.join()

    print('skmn_fudan_spider爬取结束!')
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    print('共用时：', time.time() - start_time)


if __name__ == '__main__':
    main()