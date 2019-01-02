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

url = 'http://www.vigenebio.cn/index.php?catid=111&c=content&a=search&more=1&Submit1.x=18&Submit1.y=13&kw=A1BG'
# 随机获取user-agent
with open(sys.path[0] + '/user-agents.txt', 'r' , encoding = 'utf-8') as f:
    list_user_agent = f.readlines()
user_agent = random.choice(list_user_agent).strip()
# print(user_agent)
headers = {'user-agent':user_agent}
proxies = {
    'http':'http://' + '117.191.11.107:8080' ,
    'https':'https://' + '117.191.11.107:8080' 
}
response = requests.get(url, headers = headers, proxies = proxies, timeout = 7)
response.encoding = 'utf-8'
source_html = etree.HTML(response.text)
source = source_html.xpath('//table[@width="980"]/tbody/tr')
print(type(source),source)
del source[0]
print(source)
for kw in source:
    product_no = kw.xpath('./td[1]/a')[0].text
    gene_no = kw.xpath('./td[2]/a')[0].text
    descibe = kw.xpath('./td[3]')[0].text
    price = kw.xpath('./td[4]')[0].text
    supply_time = kw.xpath('./td[5]')[0].text
    print(product_no)
    print(gene_no)
    print(descibe)
    print(price)
    print(supply_time)