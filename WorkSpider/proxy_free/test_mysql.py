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



def save_mysql(product_no, gene_no, descibe, price, supply_time, kw):
    """
    把获取到的表格数据保存到mysql中
    """
    db = pymysql.connect(host='localhost', user='bmnars', password='vi93nwYV', port=3306, db='bmnars')
    cursor = db.cursor()
    update_time = time.strftime('%Y-%m-%d',time.localtime())
    data = {
        'product_no':product_no,
        'gene_no':gene_no,
        'descibe':descibe,
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
    # try:
    if cursor.execute(sql,tuple(data.values())*2):
        db.commit()
    # except:
    #     print("save_mysql_failed:")
    #     db.rollback()
    
    # finally:
    #     cursor.close()      
    #     db.close()


save_mysql(1,1,1,1,1,1)