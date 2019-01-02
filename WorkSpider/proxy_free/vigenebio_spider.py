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
    从表_cs_bmnars_vigenebio_keyword中获取查询关键字并且判断更新数据
    :param kw: 查询或者更新的where条件
    :judge: 0：查询未跑过的关键字，1：status= 1， 2：isrun = 1， 3；status= 0
    return: kw
    """
    # 数据库连接
    db = pymysql.connect(host='localhost', user='bmnars', password='vi93nwYV', port=3306, db='bmnars')
    cursor = db.cursor()
    # 更新时间
    update_time = time.strftime('%Y-%m-%d',time.localtime())
    # print('judge:\t', type(judge), judge)

    # 查询状态未更新的关键字
    if judge == 0:
       
        sql = 'select kw from _cs_bmnars_vigenebio_keyword where status = 0 and isrun = 0 and id = %s;'
        # print(sql)
        try:
            cursor.execute(sql, (kw))
            # 获取一行
            row = cursor.fetchone()
            # 返回关键字
            return row[0]
        except:
            pass
        finally:
            cursor.close()
            db.close()

        
    # 更新status= 1，表示爬取到数据
    elif judge == 1:
        sql = 'update _cs_bmnars_vigenebio_keyword set update_time=%s, status= 1, isrun = 1 where kw =%s;'
        try:
            cursor.execute(sql, (update_time, kw))
            db.commit()

        except:
            print('update status= 1 from keyword error')
            db.rollback()
        finally:
            cursor.close()
            db.close()

    # 更新isrun = 1，表示关键字已跑
    elif judge == 2:
        sql = 'update _cs_bmnars_vigenebio_keyword set update_time=%s, isrun = 1 where kw =%s;'
        try:
            cursor.execute(sql, (update_time, kw))
            db.commit()
            # print('update isrun = 1 from keyword success!')
        except:
            print('update isrun = 1  error')
            db.rollback()
        finally:
            cursor.close()
            db.close()

    # 更新status= 2，表示关键字已跑，并且没有获取到数据
    elif judge == 3:
        sql = 'update _cs_bmnars_vigenebio_keyword set update_time=%s, status= 2 where kw =%s;'
        try:
            cursor.execute(sql, (update_time, kw))
            db.commit()
            # print('update status= 2  from keyword success!')
        except:
            print('update status= 2  error')
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


def save_mysql(Catalog_Number, Gene_Symbol, Species, Product_names, Description, Price, Delivery, keyword):
    """
    把获取到的表格数据保存到mysql中
    """
    db = pymysql.connect(host='localhost', user='bmnars', password='vi93nwYV', port=3306, db='bmnars')
    cursor = db.cursor()
    update_time = time.strftime('%Y-%m-%d',time.localtime())
    data = {
        'Catalog_Number':Catalog_Number,
        'Gene_Symbol':Gene_Symbol,
        'Species':Species,
        'Product_names':Product_names,
        'Description':Description,
        'Price':Price,
        'Delivery':Delivery,
        'update_time':update_time,
        'keyword':keyword

    }
    table = '_cs_bmnars_vigenebio_result'
    keys = ','.join(data.keys())
    values = ','.join(['%s']*len(data))
    sql = 'INSERT INTO {table}({keys}) VALUES ({values}) on duplicate key update '.format(table=table, keys=keys, values=values)
    update = ', '.join(['{key} = %s'.format(key=key) for key in data]) + ';'
    sql += update
    # print(sql)
    try:
        if cursor.execute(sql,tuple(data.values())*2):
            db.commit()
            # print('saving success!')
    except:
        print("save_mysql_failed:")
        db.rollback()
    
    finally:
        cursor.close()      
        db.close()

class ThreadCrawl(threading.Thread):
    def __init__(self, name_thread, queue_page, queue_data):
        """
        初始化
        :param name_thread: 采集线程名字
        :param queue_page: 页码队列
        :param queue_data: 采集队列
        """
        super(ThreadCrawl, self).__init__()
        self.name_thread = name_thread
        self.queue_page = queue_page
        self.queue_data = queue_data

    def run(self):
        print('启动' + self.name_thread)
        # 判断只要队列不为空，就一直循环
        while not self.queue_page.empty():
            try:
                # 从页码队列中获取url，False队列为空抛出一个为空的异常
                url = self.queue_page.get(False)
                # print(self.name_thread + ': url:\t' + url)

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
                    # 获取不到页面，一般是代理有问题，把url重新放入队列，尝试再次获取页面
                    self.queue_page.put(url)
                    response = ''

                # 通过正则从url中获取关键字kw
                kw_re = re.search(r'keyword=(.*)&to', url)
                if not kw_re:
                    kw = re.search(r'keyword=(.*)', url).group(1)
                else:
                    kw = kw_re.group(1)

                # 更新isrun = 1，表示关键字已跑    
                get_kw(kw, 2)

                if response:
                    print(self.name_thread + ': get source_page！', url)

                    content = response.text
                    # print(content)
                    source_html = etree.HTML(content)

                    # 判断该关键字查询是否还有下一页的数据
                    source = source_html.xpath('//div[@class="pagelistbox"]//a[@class="nextPage"]/@href')
                    if source:
                        next_url = 'https://www.vigenebio.com' + source[0]
                        print('next_url: ', next_url)
                        # 如果还有下一页，则把下一页的url放入页码队列里面
                        self.queue_page.put(next_url)
                    
                    # 把关键字，获取到的网页源码放入解析队列
                    list_source = [kw, content]
                    # print('content:\t' + content)
                    self.queue_data.put(list_source)
                    
            except Exception as e:
                print('ThreadCrawl', e.args)
        print('结束' + self.name_thread)
        # self.queue_page.put('test')

class ThreadParse(threading.Thread):
    def __init__(self, name_thread, queue_data, lock):
        """
        初始化
        :param name_thread: 采集线程名字
        :param queue_data: 采集队列
        :param lock: 线程锁
        """
        super(ThreadParse, self).__init__()
        self.name_thread = name_thread
        self.lock = lock
        self.queue_data = queue_data

    def run(self):
        print('启动' + self.name_thread)
        # 判断只要队列不为空，就一直循环
        while not PARSE_EXIT:
            try:
                # 从页码队列中获取数据，False队列为空抛出一个为空的异常
                list_source = self.queue_data.get(False)
                # 解析数据
                self.parse(list_source)
            except Exception as e:
                pass
                # print('ThreadParse', e.args)
        print('结束' + self.name_thread)

    def parse(self, list_source):
        """
        :param list_source: 从解析队列取出的数据
        """
        # 获取关键字
        kw = list_source[0]
        # 获取传过来的网页源码
        content = list_source[1]
        # print(content)
        source_html = etree.HTML(content)
        # print(source_html)
        # 获取表格的每一行
        source = source_html.xpath('//table[@width="980"]/tr')
        if source:
            # 删除表格字段名
            del source[0]
            # print(source)
            if source:
                try:
                    # 获取每一列中的值，存入数据库
                    for i in source:
                        Catalog_Number = i.xpath('./td[1]')[0].text
                        Gene_Symbol = i.xpath('./td[2]')[0].text
                        Species = i.xpath('./td[3]')[0].text
                        Product_names = i.xpath('./td[4]/a')[0].text
                        Description = i.xpath('./td[5]')[0].text
                        Price = i.xpath('./td[6]')[0].text
                        Delivery = i.xpath('./td[7]')[0].text
                        # print(Catalog_Number + '\t')
                        # print(Gene_Symbol + '\t')
                        # print(Species + '\t')
                        # print(Product_names + '\t')
                        # print(Description + '\t')
                        # print(Price + '\t')
                        # print(Delivery + '\t')
                        # 保存到mysql中
                        # print(self.name_thread, 'saving mysql......', kw)
                        # lock.acquire()
                        self.lock.acquire()
                        save_mysql(Catalog_Number, Gene_Symbol, Species, Product_names, Description, Price, Delivery, kw)
                        # print('update keyword......', kw)
                        self.lock.release()
                    print(self.name_thread, 'update status= 1 from keyword', kw)

                    # 更新status= 1，表示爬取到数据
                    get_kw(kw, 1)
                except Exception as e:
                    pass
            else:
                # 更新status= 2，表示关键字已跑，并且没有获取到数据
                get_kw(kw, 3)
                print(self.name_thread,'update status= 2 from keyword', kw)
            # print('success！')


# 通过这种判断，有个问题： 队列放入少量数据，因为线程与主线程同步运行，类里面添加的Url,还没放入队列就判断队列为空退出线程了。
# 判断爬取线程是否跑完
# CRAWL_EXIT = False
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

    # 表里面一共有61091个关键字
    for i in range(1, 61091):
        # 获取关键字，judge=0判断选择查询语句
        kw = get_kw(i, 0)
        # print(kw)
        if kw:
            # 组合url
            url = 'https://www.vigenebio.com/search/search.php?keyword=' + kw
            # 把组合后的url放入页码队列
            queue_page.put(url)
    
    # 采集结果队列
    queue_data = Queue()

    # 锁
    lock = threading.Lock()

    # 三个采集线程的名字
    list_crawl = ["采集线程1号", "采集线程2号", "采集线程3号", "采集线程4号"]
    # list_crawl = ["采集线程1号"]
    # print('list_crawl', list_crawl)

    # 存储三个采集线程的列表集合     
    thread_crawl = []
    for name_thread in list_crawl:
        # 线程定义
        thread = ThreadCrawl(name_thread, queue_page, queue_data)
        # 启动线程
        thread.start()
        # 添加线程到列表
        thread_crawl.append(thread)
    # print('thread_crawl\t', thread_crawl)

    # 三个解析线程的名字
    list_parse = ["解析线程1号", "解析线程2号", "解析线程3号", "解析线程4号"]
    # list_parse = ["解析线程1号"]
    # print('list_parse', list_parse)
    
    # 存储三个解析线程的列表集合     
    thread_parse = []
    for name_thread in list_parse:
        # 线程定义
        thread = ThreadParse(name_thread, queue_data, lock)
        # 启动线程
        thread.start()
        # 添加线程到列表
        thread_parse.append(thread)
    
    # 等待queue_page队列为空
    # a = queue_page.qsize()
    # print('a',a)
    #while  a:
    #    pass
    #    # print('**********')
    # 如果queue_page队列为空,采集线程退出循环
    #global CRAWL_EXIT
    #CRAWL_EXIT = True
    # print('queue_page为空！')

    for thread in thread_crawl:
        # 等待采集线程完成退出，阻塞主线程，其他线程不受影响
        thread.join()
    print('queue_page为空！')

    # 等待queue_data队列为空
    while not queue_data.empty():
        pass 
    # 如果queue_data队列为空,采集线程退出循环
    global PARSE_EXIT
    PARSE_EXIT = True
    print('queue_data为空！')

    for thread in thread_parse:
        # 等待解析线程完成退出，阻塞主线程，其他线程不受影响
        thread.join()
    # print('queue_data为空！')

    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    print('用时：\t' , time.time()-start_time)


if __name__ == '__main__':
    main()