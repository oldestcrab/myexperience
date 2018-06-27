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
import re
#import os

browser = webdriver.PhantomJS(executable_path=r'C:/Users/CRAB/Desktop/mybooks/execute/phantomjs-2.1.1-windows/bin/phantomjs.exe')


wait = WebDriverWait(browser, 10)


def index_page(page, judge):
    """
    抓取索引页
    :param page: 页码
    :param judge: 用于判断上次爬取位置
    """
    print('正在爬取第', page, '页索引页')
    try:
        #url_list = ['http://paper.sciencenet.cn/paper/fieldlist.aspx?id=2','http://news.sciencenet.cn/fieldlist.aspx?id=3']
        #for url in url_list:
        # 论文链接
        #url = 'http://paper.sciencenet.cn/paper/fieldlist.aspx?id=2'
        # 领域新闻链接
        url = 'http://news.sciencenet.cn/fieldlist.aspx?id=3'
        browser.get(url)
        if page > 1:
            input = wait.until(
                EC.presence_of_element_located((By.NAME, 'AspNetPager1_input')))
            submit = wait.until(
                EC.element_to_be_clickable((By.NAME, 'AspNetPager1')))
            input.clear()
            input.send_keys(page)
            submit.click()
        wait.until(EC.text_to_be_present_in_element_value((By.NAME, 'AspNetPager1_input'), str(page)))
        return get_pages(page, judge)
    except TimeoutException:
        print('爬取第', page, '页索引页time out,尝试重新爬取!')
        index_page(page, judge)
        


def get_pages(page, judge):
    """
    提取文章内容
    :param page: 页码
    :param judge: 用于判断上次爬取位置
    """
    html = browser.page_source
    result = etree.HTML(html)
    items = result.xpath('//*[@id="DataGrid1"]/tbody//tbody')
    if page == 1:
        #领域新闻为 @width = "60%" ， 论文为 @width = "60%"
        next_judge = items[0].xpath('.//td[@width = "60%"]/a/@href')[0]
        with open('sciencenet_spider/judge.text', 'w', encoding = 'utf-8') as f:
            print(next_judge)
            f.write(next_judge)
    for item in items:
        #print(type(item))
        #content = {
        #    'title': item.xpath('.//td[@width = "60%"]/a')[0].text.replace('\n','').replace(' ',''),
        #    'url': item.xpath('.//td[@width = "60%"]/a/@href')[0],
        #    'from': item.xpath('.//td[@width = "20%"]')[0].text.replace('\n','').replace(' ',''),
        #    'date': item.xpath('.//td[@width = "10%"]')[0].text.replace('\n','').replace(' ','')
        #}
        #print(content)
        kw = item.xpath('.//td[@width = "60%"]/a/@href')[0]
        #title = item.xpath('.//td[@width = "60%"]/a')[0].text.replace('\n','').replace(' ','')
        if kw == judge:
            print("爬取到上次爬取位置，结束爬取！")
            return 1
            break
        url = 'http://paper.sciencenet.cn' + kw
        #/htmlpaper/201861510484322846535.shtm
        filename_pattern = re.compile('[a-zA-Z./]')
        filename = filename_pattern.sub('', kw)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
        }
        response = requests.get(url, headers = headers)
        response.encoding = 'utf-8'
        time.sleep(2)
        #print(detail_html.encoding,detail_html.apparent_encoding)
        #detail_html = etree.HTML(response.text)
        save_page(response.text, filename)
        print('保存第', page, '页索引页所有文章成功') 
    
    


def save_page(result, filename):
    """
    保存到文件
    :param result: 结果
    """
    #with open('./result.json', 'a', encoding = 'utf-8') as f:
    #    f.write(json.dumps(result, indent = 2, ensure_ascii = False))
    #print(result)
    detail_pattern = re.compile(r'<table id="content".*<!-- JiaThis Button END -->.*?</table>',re.S)
    detail_result = detail_pattern.search(result)
    #print(type(detail_html))
    #detail_content = etree.tostring(detail_html)
    #detail_result = detail_html.xpath('//table[@id="content"]')
    #print(type(detail_result))
    #print(detail_result.group())
    full_filename = './sciencenet_spider/sciencenet_spider_result/' + filename + '.html'
    with open(full_filename, 'w', encoding = 'utf-8') as f:
        f.write(detail_result.group())
    #print('文件' + full_filename + '保存成功')    

def main():
    """
    遍历每一页索引页
    """
    with open('sciencenet_spider/judge.text', 'r', encoding = 'utf-8') as f:
        judge = f.read()
    for i in range(1, 4):
        #print(i)
        params = index_page(i, judge)
        if params == 1:
            break
        
        
    browser.close()


if __name__ == '__main__':
    main()













