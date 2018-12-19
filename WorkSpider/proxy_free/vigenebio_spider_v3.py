# -*- encoding:utf-8 -*-

import re
import time
import requests
from lxml import etree
from requests import ConnectionError
import sys
import os
import random
from random import shuffle
import pymysql
import json
import threading
from queue import Queue 

    
def get_kw(kw, judge):
    """
    从表_cs_bmnars_vigenebio_keyword中获取查询关键字
    """
    # 数据库连接
    db = pymysql.connect(host='localhost', user='bmnars', password='vi93nwYV', port=3306, db='bmnars')
    cursor = db.cursor()
    # 更新时间
    update_time = time.strftime('%Y-%m-%d',time.localtime())
    # print('judge:\t', type(judge), judge)

    if judge == 0:
        # 查询状态未更新的关键字，爬取之后状态改为 y
        sql = 'select kw from _cs_bmnars_vigenebio_kw where status = 0 and isrun = 0 and id = %s;'
        # print(sql)
        try:
            cursor.execute(sql, (kw))
            # 获取一行
            row = cursor.fetchone()
            cursor.close()
            db.close()
            return row[0]
        except:
            print('get kw error!')
    
    elif judge == 1:
        sql = 'update _cs_bmnars_vigenebio_kw set update_time=%s, status= 1, isrun = 1 where kw =%s;'
        try:
            cursor.execute(sql, (update_time, kw))
            db.commit()
            print('update keyword success!')

        except:
            print('update error')
            db.rollback()
    elif judge == 2:
        
        sql = 'update _cs_bmnars_vigenebio_kw set update_time=%s, isrun = 1 where kw =%s;'
        try:
            cursor.execute(sql, (update_time, kw))
            db.commit()
            print('update keyword success!')

        except:
            print('update error')
            db.rollback()
    cursor.close()
    db.close()



class Proxy():
    def __init__(self):
        super(Proxy).__init__()
        self.url = 'http://httpbin.org/get'
        self.list_ip = sys.path[0] + '/ip_response.txt'
        self.list_user_agent = sys.path[0] + '/user-agents.txt'

    def test_proxy(self):
        """
        测试代理IP是否可用，返回可用IP
        """
        # 随机获取代理IP
        with open(self.list_ip, 'r', encoding = 'utf-8') as f:
            list_proxy = f.readlines()
            shuffle(list_proxy)

        for proxy in list_proxy:
            proxy = proxy.strip()
            # print(proxy)
            # 获取IP不要端口，判断与httpbin返回的IP是否相等
            judge_proxy_pattern = re.compile('(.*):')
            judge_proxy = judge_proxy_pattern.search(proxy).group(1)
            # print(judge_proxy)

            # 随机获取user-agent
            with open(self.list_user_agent, 'r' , encoding = 'utf-8') as f:
                list_user_agent = f.readlines()
            user_agent = random.choice(list_user_agent).strip()
            # print(user_agent)
            headers = {'user-agent':user_agent}

            proxies = {
                'http':'http://' + proxy ,
                'https':'https://' + proxy 
            }
            # print(proxies)

            try:
                response = requests.get(self.url, headers = headers, proxies = proxies, timeout = 4)
            except:
                response = ''
                # list_proxy.remove(proxy)
            if response:
                try:
                    # 获取httpbin上的IP
                    # print(response.text)
                    dict_response = json.loads(response.text)
                    ip_response = dict_response['origin']
                    # print(ip_response)

                except:
                    ip_response = ''
                # 判断返回的IP是否和本地的相等
                if ip_response == judge_proxy:
                    return proxy

def save_mysql(product_no, gene_no, detail, price, supply_time, kw):
    """
    把获取到的表格数据保存到mysql中
    """
    db = pymysql.connect(host='localhost', user='bmnars', password='vi93nwYV', port=3306, db='bmnars')
    cursor = db.cursor()
    update_time = time.strftime('%Y-%m-%d',time.localtime())
    data = {
        'product_no':product_no,
        'gene_no':gene_no,
        'detail':detail,
	    'update_time':update_time,
        'keyword':kw,
        'supply_time':supply_time,
        'price':price
    }
    table = '_cs_bmnars_vigenebio_rs'
    keys = ','.join(data.keys())
    values = ','.join(['%s']*len(data))
    sql = 'INSERT INTO {table}({keys}) VALUES ({values}) on duplicate key update '.format(table=table, keys=keys, values=values)
    update = ', '.join(['{key} = %s'.format(key=key) for key in data]) + ';'
    sql += update
    # print(sql)
    try:
        if cursor.execute(sql,tuple(data.values())*2):
            db.commit()
            print('saving success!')
    except:
        print("save_mysql_failed:")
        db.rollback()
    
    finally:
        cursor.close()      
        db.close()

class ThreadCrawl(threading.Thread):
    def __init__(self, name_thread, queue_page, queue_data):
        super(ThreadCrawl, self).__init__()
        self.name_thread = name_thread
        self.queue_page = queue_page
        self.queue_data = queue_data

    def run(self):
        print('启动' + self.name_thread)
        while not CRAWL_EXIT:
            try:
                kw = self.queue_page.get(False)
                print(self.name_thread + ': kw:\t' + kw)
                url = 'http://www.vigenebio.cn/index.php?catid=111&c=content&a=search&more=1&Submit1.x=18&Submit1.y=13&kw=' + kw
                print(self.name_thread + ': url:\t' + url)
                get_proxy = Proxy()
                proxy = get_proxy.test_proxy()
                print(self.name_thread + ': proxy:\t' + proxy)

                # 随机获取user-agent
                with open(sys.path[0] + '/user-agents.txt', 'r' , encoding = 'utf-8') as f:
                    list_user_agent = f.readlines()
                user_agent = random.choice(list_user_agent).strip()
                # print(user_agent)
                headers = {'user-agent':user_agent}
                proxies = {
                    'http':'http://' + proxy ,
                    'https':'https://' + proxy
                }
                # print(proxies)
                try:
                    # 尝试获取页面资源
                    response = requests.get(url, headers = headers, proxies = proxies, timeout = 4)
                    response.encoding = 'utf-8'
                except:
                    print(self.name_thread + ': can\'t get source_page！!\t' + kw)
                    response = ''
                if response:
                    print(self.name_thread + ': get source_page！')
                    content = response.text
                    list_content = [kw, content]
                    # print('content:\t' + content)
                    self.queue_data.put(list_content)
            except:
                pass
        print('结束' + self.name_thread)

class ThreadParse(threading.Thread):
    def __init__(self, name_thread, queue_data, lock):
        super(ThreadParse, self).__init__()
        self.name_thread = name_thread
        self.lock = lock
        self.queue_data = queue_data

    def run(self):
        print('启动' + self.name_thread)
        while not PARSE_EXIT:
            try:
                list_content = self.queue_data.get(False)
                self.parse(list_content)
            except:
                pass
        print('结束' + self.name_thread)

    def parse(self, list_content):
        
        kw = list_content[0]
        # print(kw)
        content = list_content[1]
        # print(content)
        source_html = etree.HTML(content)
        source = source_html.xpath('//div[@class="right"]//tbody/tr')
        print(self.name_thread + ': source:\t' , source)
        if source:
            # 删除表格字段名
            del source[0]
            # print(source)
            for i in source:
                product_no = i.xpath('./td[1]/a')
                gene_no = i.xpath('./td[2]/a')
                detail = i.xpath('./td[3]')
                price = i.xpath('./td[4]')
                supply_time = i.xpath('./td[5]')
                if product_no and gene_no and detail and price and supply_time:
                    product_no = i.xpath('./td[1]/a')[0].text
                    gene_no = i.xpath('./td[2]/a')[0].text
                    detail = i.xpath('./td[3]')[0].text
                    price = i.xpath('./td[4]')[0].text
                    supply_time = i.xpath('./td[5]')[0].text
                    # print(product_no)
                    # print(gene_no)
                    # print(detail)
                    # print(price)
                    # print(supply_time)
                    # 保存到mysql中
                    print('saving mysql......')
                    # lock.acquire()
                    self.lock.acquire()
                    save_mysql(product_no, gene_no, detail, price, supply_time, kw)
                    print('update keyword......')
                    get_kw(kw, 1)
                    self.lock.release()
                else:
                    get_kw(kw, 2)
            # print('success！')

# 判断爬取线程是否跑完
CRAWL_EXIT = False
# 判断解析线程是否跑完
PARSE_EXIT = False

def main():
    """
    遍历每一页索引页
    """
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    start_time = time.time()

    # 页码队列
    queue_page = Queue()
    for i in range(10000, 60000):
        kw = get_kw(i, 0)
        print(kw)
        queue_page.put(kw)
    
    # 采集结果队列
    queue_data = Queue()

    # 锁
    lock = threading.Lock()

    # 三个采集线程的名字
    list_crawl = ["采集线程1号", "采集线程2号", "采集线程3号"]
    # print('list_crawl', list_crawl)
    # 存储三个采集线程的列表集合     
    thread_crawl = []
    for name_thread in list_crawl:
        thread = ThreadCrawl(name_thread, queue_page, queue_data)
        thread.start()
        thread_crawl.append(thread)
    # print('thread_crawl\t', thread_crawl)

    # 三个解析线程的名字
    list_parse = ["解析线程1号", "解析线程2号", "解析线程3号"]
    # print('list_parse', list_parse)
    
    # 存储三个解析线程的列表集合     
    thread_parse = []
    for name_thread in list_parse:
        thread = ThreadParse(name_thread, queue_data, lock)
        thread.start()
        thread_parse.append(thread)
    
    # 等待queue_page队列为空
    while not queue_page.empty():
        pass 
    # 如果queue_page队列为空,采集线程退出循环
    global CRAWL_EXIT
    CRAWL_EXIT = True
    print('queue_page为空！')

    for thread in thread_crawl:
        thread.join()

    # 等待queue_data队列为空
    while not queue_data.empty():
        pass 
    # 如果queue_data队列为空,采集线程退出循环
    global PARSE_EXIT
    PARSE_EXIT = True
    print('queue_data为空！')

    for thread in thread_parse:
        thread.join()


    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    print('用时：\t' , time.time()-start_time)


if __name__ == '__main__':
    main()