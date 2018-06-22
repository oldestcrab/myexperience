# -*- coding:utf-8 -*-

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from lxml import etree
import json
import time
import requests
#import os

browser = webdriver.PhantomJS(executable_path=r'C:/Users/CRAB/Desktop/mybooks/execute/phantomjs-2.1.1-windows/bin/phantomjs.exe')


wait = WebDriverWait(browser, 10)


def index_page(page):
    """
    抓取索引页
    :param page: 页码
    """
    print('正在爬取第', page, '页索引页')
    try:
        url = 'http://paper.sciencenet.cn/paper/fieldlist.aspx?id=2'
        browser.get(url)
        if page > 1:
            #print('test')
            input = wait.until(
                EC.presence_of_element_located((By.NAME, 'AspNetPager1_input')))
            #print(input)
            submit = wait.until(
                EC.element_to_be_clickable((By.NAME, 'AspNetPager1')))
            #print(submit)
            input.clear()
            input.send_keys(page)
            submit.click()
            #time.sleep(1)
        wait.until(EC.text_to_be_present_in_element_value((By.NAME, 'AspNetPager1_input'), str(page)))
        get_products()
    except TimeoutException:
        print('爬取第', page, '页索引页time out,尝试重新爬取!')
        index_page(page)
        


def get_products():
    """
    提取文章内容
    """
    html = browser.page_source
    #with open('./html.html', 'a', encoding = 'utf-8') as f:
    #    f.write(html)
    result = etree.HTML(html)
    items = result.xpath('//*[@id="DataGrid1"]/tbody//tbody')
    #print(items)
    #print(type(items))
    for item in items:
        #print(type(item))
        #title = item.xpath('./tr[2]/td[1]/a')[0].text
        #print(title,type(title))
        #content = {
        #    'title': item.xpath('.//td[@width = "70%"]/a')[0].text.replace('\n','').replace(' ',''),
        #    'url': item.xpath('.//td[@width = "70%"]/a/@href')[0],
        #    'from': item.xpath('.//td[@width = "20%"]')[0].text.replace('\n','').replace(' ',''),
        #    'date': item.xpath('.//td[@width = "10%"]')[0].text.replace('\n','').replace(' ','')
        #}
        #print(content)
        kw = item.xpath('.//td[@width = "70%"]/a/@href')[0]
        #print(type(kw))
        url = 'http://paper.sciencenet.cn' + kw
        #print(url)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
        }
        response = requests.get(url, headers = headers)
        response.encoding = 'utf-8'
        time.sleep(2)
        #print(detail_html.encoding,detail_html.apparent_encoding)
        #print(detail_html.text)
        #detail_html = etree.HTML(response.text)
        save_to_json(response)


def save_to_json(result):
    """
    保存到文件
    :param result: 结果
    """
    #with open('./result.json', 'a', encoding = 'utf-8') as f:
    #    f.write(json.dumps(result, indent = 2, ensure_ascii = False))
    detail_html = etree.HTML(result.text)
    detail_content = detail_html.xpath('//*[@id = "content"]')
    print(type(detail_content))
    print(detail_content)
    #detail_result = etree.tostring(detail_content)
    #with open('./test.html', 'w', encoding = 'utf-8') as f:
    #    f.write(deatil_result.decode('utf-8'))
    #print('done')    

def main():
    """
    遍历每一页索引页
    """
    for i in range(1, 2):
        #print(i)
        index_page(i)
        
    browser.close()


if __name__ == '__main__':
    main()













