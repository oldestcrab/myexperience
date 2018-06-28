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
from requests.exceptions import ConnectionError
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
        url = 'http://paper.sciencenet.cn/paper/fieldlist.aspx?id=2'
        # 领域新闻链接
        #url = 'http://news.sciencenet.cn/fieldlist.aspx?id=3'
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
        #领域新闻为 @width = "60%" ， 论文为 @width = "70%"
        next_judge = items[0].xpath('.//td[@width = "70%"]/a/@href')[0]
        with open('sciencenet_spider/judge.txt', 'w', encoding = 'utf-8') as f:
            print("next_judge:\t" + next_judge)
            f.write(next_judge)
    for item in items:
        #content = {
        #    'title': item.xpath('.//td[@width = "60%"]/a')[0].text.replace('\n','').replace(' ',''),
        #    'url': item.xpath('.//td[@width = "60%"]/a/@href')[0],
        #    'from': item.xpath('.//td[@width = "20%"]')[0].text.replace('\n','').replace(' ',''),
        #    'date': item.xpath('.//td[@width = "10%"]')[0].text.replace('\n','').replace(' ','')
        #}
        kw = item.xpath('.//td[@width = "70%"]/a/@href')[0]
        #title = item.xpath('.//td[@width = "60%"]/a')[0].text.replace('\n','').replace(' ','')
        if kw == judge:
            print("爬取到上次爬取位置，结束爬取！")
            return 1
            break
        url = 'http://paper.sciencenet.cn' + kw
        #/htmlpaper/201861510484322846535.shtm
        filename_pattern = re.compile(r'[a-zA-Z:./-_]')
        filename = filename_pattern.sub('', kw)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
        }
        response = requests.get(url, headers = headers)
        response.encoding = 'utf-8'
        time.sleep(2)
        #print(detail_html.encoding,detail_html.apparent_encoding)
        detail_pattern = re.compile(r'<table id="content".*<!-- JiaThis Button END -->.*?</table>',re.S)
        detail_search = detail_pattern.search(response.text)   
        detail_result = detail_search.group()
        # 匹配url链接
        img_pattern = re.compile(r'<img(.*?)src="(.*?)"', re.S)
        # 获取所有的url链接
        img_findall = img_pattern.findall(detail_result)
        for detail in img_findall:
            try:
                img_sour_pattern = re.compile(r'http')
                img_judge = img_sour_pattern.search(detail[1])
                if img_judge is None:
                    img_url = 'http://news.sciencenet.cn' + detail[1] 
                else:
                    img_url = detail[1] 
                print(img_url)
                img_response = requests.get(img_url, headers = headers).content
                img_save_name = filename_pattern.sub('', detail[1])
                #print('img_save_name:' + img_save_name)
                save_img(img_response, img_save_name)
            except ConnectionError:
                print('图片网址有误:' + url)
        
        def img_url_name(match):
            img_url_pattern = re.compile(r'[a-zA-Z:/.-_]')
            img_url_detail = img_url_pattern.sub('', match.group(2))
            img_url_detail_add = img_url_pattern.search(match.group(1))
            #print("img_url_detail:" + img_url_detail)
            #print('img_url_detail_add: ' + img_url_detail_add.group(), type(img_url_detail_add))
            #if img_url_detail_add is None: 
            img_name = '<img src="./img/' + img_url_detail + '.jpg'
            #else:
            #    img_name = '<img ' + img_url_detail_add.group() + 'src="./img/' + img_url_detail + '.jpg"'
            print("img_name:" + img_name)
            return img_name
        real_result = img_pattern.sub(img_url_name, detail_result)
            
        save_page(real_result, filename)
    print('保存第', page, '页索引页所有文章成功') 
    
    


def save_page(result, filename):
    """
    保存到文件
    :param result: 结果
    :param filename: 保存的文件名
    """
    full_filename = './sciencenet_spider/sciencenet_spider_result/' + filename + '.html'
    with open(full_filename, 'w', encoding = 'utf-8') as f:
        f.write(result)
    #print('文件' + full_filename + '保存成功')    

def save_img(result, filename):
    """
    保存文章中的图片
    :param result: 图片文件
    :param filename: 保存的图片名
    """
    img_save_full_name = './sciencenet_spider/sciencenet_spider_result/img/' + filename + '.jpg'
    with open(img_save_full_name, 'wb') as f:
        f.write(result)       

def main():
    """
    遍历每一页索引页
    """
    with open('sciencenet_spider/judge.txt', 'r', encoding = 'utf-8') as f:
        judge = f.read()
    for i in range(1, 3):
        params = index_page(i, judge)
        if params == 1:
            break
        
        
    browser.close()


if __name__ == '__main__':
    main()













