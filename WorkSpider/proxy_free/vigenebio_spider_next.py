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
    从表_cs_bmnars_vigenebio_keyword中获取查询关键字并且更新数据
    :param kw: 队列或者更新的where条件
    :judge: 0：查询关键字，1：更新数据
    """
    # 数据库连接
    db = pymysql.connect(host='localhost', user='bmnars', password='vi93nwYV', port=3306, db='bmnars')
    cursor = db.cursor()
    # 更新时间
    update_time = time.strftime('%Y-%m-%d',time.localtime())
    # print('judge:\t', type(judge), judge)

    # 查询状态未更新的关键字
    if judge == 0:
       
        sql = 'select Catalog_Number, Gene_Symbol from _cs_bmnars_vigenebio_result_unique where Product_names like "%ORF Clone%" and RefSeq_no is null;'
        # print(sql)
        try:
            cursor.execute(sql)
            # 获取一行
            # 返回关键字
            row = cursor.fetchone()
            while row:
                # print(row)
                kw.put(row)
                row = cursor.fetchone()
        except:
            pass
        finally:
            cursor.close()
            db.close()

        
    # 保存爬取到的数据
    if judge == 1:
       
        sql = 'update _cs_bmnars_vigenebio_result_unique set RefSeq_no = %s where Catalog_Number = %s;'
        # print(sql)
        try:
            cursor.execute(sql, (kw[1], kw[0]))
            db.commit()
        except Exception as e:
            print(e.args)
            db.rollback()
        finally:
            cursor.close()
            db.close()



def get_proxy():
    """
    return:返回可用IP(ip:port)
    """
    response = requests.get('http://127.0.0.1:5555/random')
    proxy = response.text

    return proxy

class ThreadCrawl(threading.Thread):
    def __init__(self, name_thread, queue_page, lock):
        """
        初始化
        :param name_thread: 采集线程名字
        :param queue_page: 页码队列
        :param lock: 采集队列
        """
        super(ThreadCrawl, self).__init__()
        self.name_thread = name_thread
        self.queue_page = queue_page
        self.lock = lock

    def run(self):
        print('启动' + self.name_thread)
        # 判断只要队列不为空，就一直循环
        while not self.queue_page.empty():
            try:
                # 从页码队列中获取url关键字，False队列为空抛出一个为空的异常
                kw_tuple = self.queue_page.get(False)
                # print(kw_tuple)
                # print(self.name_thread + ': url:\t' + url)
                # 组合url
                url = 'https://www.vigenebio.com/ORF/human/' + kw_tuple[0] + '/' + kw_tuple[1] + '-cDNA'
                # print(url)

                # 获取当前可用代理
                proxy = get_proxy()
                # print(self.name_thread + ': proxy:\t' + proxy)
                proxies = {
                    'http':'http://' + proxy ,
                    'https':'https://' + proxy
                }
                # print(proxies)

                # 随机获取user-agent
                with open(sys.path[0] + '/user-agents.txt', 'r' , encoding = 'utf-8') as f:
                    list_user_agent = f.readlines()
                user_agent = random.choice(list_user_agent).strip()
                # print(user_agent)
                headers = {'user-agent':user_agent}

                try:
                    # 尝试获取页面资源
                    response = requests.get(url, headers = headers, proxies = proxies, timeout = 4)
                    response.encoding = 'gb2312'
                except:
                    # print(self.name_thread + ': can\'t get source_page!\t' + url)
                    # 获取不到页面，一般是代理有问题，把数据重新放入队列，尝试再次获取页面
                    print('try again! ' + url)
                    self.queue_page.put(kw_tuple)
                    response = ''

                if response:
                    print(self.name_thread + ': get source_page！', url)

                    content = response.text
                    # print(content)
                    source_html = etree.HTML(content)

                    # 获取需要的内容
                    source = source_html.xpath('//td[@width="310"]')
                    try:
                        # 获取所有内容
                        source = source[0].xpath('string(.)').strip()
                        # print(source)
                        # 通过正则剔除无用内容
                        content_pattren = re.compile(r'RefSeq#(.*)Cat', re.I|re.S)
                        content = content_pattren.search(source).group(1).strip()

                        # 通过列表保存数据
                        list_content = []
                        list_content.append(kw_tuple[0])
                        list_content.append(content)

                        self.lock.acquire()
                        # 把获取到的数据存入MySQL
                        get_kw(list_content, 1)
                        self.lock.release()

                    except Exception as e:
                        print(e.args)

            except Exception as e:
                print('ThreadCrawl', e.args)
        print('结束' + self.name_thread)
        # self.queue_page.put('test')



def main():
    """
    遍历每一页索引页
    """
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    start_time = time.time()

    # 页码队列
    queue_page = Queue()

    # 从数据库中查询数据并放入页码队列
    get_kw(queue_page, 0)

    # 锁
    lock = threading.Lock()

    # 4个采集线程的名字
    list_crawl = ["采集线程1号", "采集线程2号", "采集线程3号", "采集线程4号"]
    # list_crawl = ["采集线程1号"]
    # print('list_crawl', list_crawl)

    # 存储4个采集线程的列表集合     
    thread_crawl = []
    for name_thread in list_crawl:
        # 线程定义
        thread = ThreadCrawl(name_thread, queue_page, lock)
        # 启动线程
        thread.start()
        # 添加线程到列表
        thread_crawl.append(thread)
    # print('thread_crawl\t', thread_crawl)

    for thread in thread_crawl:
        # 等待采集线程完成退出，阻塞主线程，其他线程不受影响
        thread.join()
    print('queue_page为空！')

    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    print('用时：\t' , time.time()-start_time)


if __name__ == '__main__':
    main()