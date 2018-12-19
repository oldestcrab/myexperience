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


def get_kw():
    """
    从表_cs_bmnars_vigenebio_keyword中获取查询关键字
    """
    # 数据库连接
    db = pymysql.connect(host='localhost', user='bmnars', password='vi93nwYV', port=3306, db='bmnars')
    cursor = db.cursor()
    cursor_update = db.cursor()
    # 更新时间
    update_time = time.strftime('%Y-%m-%d',time.localtime())
    # 查询状态未更新的关键字，爬取之后状态改为 y
    sql = 'select kw from _cs_bmnars_vigenebio_keyword where status = 0 and isrun = 0;'
    # print(sql)
    try:
        cursor.execute(sql)
        print('keyword_count:\t' , cursor.rowcount)
        # 获取一行
        row = cursor.fetchone()
        while row:
            # row[0] ：A1BG
            print('keyword:\t' + row[0])
            judge_update = parse_page(row[0])
            if judge_update == 1:
                sql_update = 'update _cs_bmnars_vigenebio_keyword set update_time=%s, status= 1, isrun = 1 where kw =%s;'
                try:
                    cursor_update.execute(sql_update, (update_time, row[0]))
                    db.commit()
                except:
                    print('update error')
                    db.rollback()
            else:
                sql_update = 'update _cs_bmnars_vigenebio_keyword set update_time=%s, isrun = 1  where kw =%s;'
                try:
                    cursor_update.execute(sql_update, (update_time, row[0]))
                    db.commit()
                except:
                    print('update error')
                    db.rollback()
            row = cursor.fetchone()
            print('\n==================next==================\n')
            # 传递关键字过去解析页面
    except:
        print('someting wrong!')
        cursor_update.close()
        cursor.close()
        db.close()

def parse_page(kw):

    url = 'http://www.vigenebio.cn/index.php?catid=111&c=content&a=search&more=1&Submit1.x=18&Submit1.y=13&kw=' + kw
    print('url:\t' + url)


    proxy = test_proxy()
    print('proxy:\t' + proxy)

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
        response = requests.get(url, headers = headers, proxies = proxies, timeout = 7)
        response.encoding = 'utf-8'
    except:
        print('can\'t get source_page！!')
        response = ''
    if response:
        print('get source_page！')
        source_html = etree.HTML(response.text)
        source = source_html.xpath('//div[@class="right"]//tbody/tr')
        print('source:\t' , source)

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
                    save_mysql(product_no, gene_no, detail, price, supply_time, kw)
            return 1

def test_proxy():
    """
    测试代理IP是否可用，返回可用IP
    """
    # 随机获取代理IP
    with open(sys.path[0] + '/ip_response.txt', 'r', encoding = 'utf-8') as f:
        list_proxy = f.readlines()
        shuffle(list_proxy)
    
    for proxy in list_proxy:
        proxy = proxy.strip()
        # 获取IP不要端口，判断与httpbin返回的IP是否相等
        judge_proxy_pattern = re.compile('(.*):')
        judge_proxy = judge_proxy_pattern.search(proxy).group(1)
        # print(judge_proxy)
        url = 'http://httpbin.org/get'

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
            response = requests.get(url, headers = headers, proxies = proxies, timeout = 4)
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
            print('saving success!')
    except:
        print("save_mysql_failed:")
        db.rollback()
    
    finally:
        cursor.close()      
        db.close()

def main():
    """
    遍历每一页索引页
    """
    print("vigenebio_spider爬取开始！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))



    # 从数据库中获取关键字
    get_kw()

    print("vigenebio_spider爬取完毕，脚本退出！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))


if __name__ == '__main__':
    main()