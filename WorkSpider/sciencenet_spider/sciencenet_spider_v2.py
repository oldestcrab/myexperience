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
import sys
import os
import random

# 构造一个 WebDriver 对象，调用phantomjs
browser = webdriver.PhantomJS(executable_path=r'C:/Users/CRAB/Desktop/mybooks/execute/phantomjs-2.1.1-windows/bin/phantomjs.exe')

# 设置等待时长
wait = WebDriverWait(browser, 10)


def index_page(page, judge, judge_name, url, judge_width):
    """
    抓取索引页
    :param page: 页码
    :param judge: 用于判断上次爬取位置
    :param judge_name: 判断爬取位置的数据保存名
    :param url: 爬取相关分类下的索引url
    """
    print('正在爬取第', page, '页索引页————>\t' + judge_name)
    try:
        #url_list = ['http://paper.sciencenet.cn/paper/fieldlist.aspx?id=2','http://news.sciencenet.cn/fieldlist.aspx?id=3']
        #for url in url_list:
        # 论文链接
        #url = 'http://paper.sciencenet.cn/paper/fieldlist.aspx?id=2'
        # 领域新闻链接
        # url = 'http://news.sciencenet.cn/fieldlist.aspx?id=3'
        # config.url为url链接
        browser.get(url)

        # 判断页码
        if page > 1:
            input = wait.until(
                # 定位页码输入位置
                EC.presence_of_element_located((By.NAME, 'AspNetPager1_input')))
            submit = wait.until(
                # 定位页码跳转框
                EC.element_to_be_clickable((By.NAME, 'AspNetPager1')))
            # 清楚页码输入框数据
            input.clear()
            # 填入page参数
            input.send_keys(page)
            # 点击跳转
            submit.click()
        # 判断当前高亮页是否为传递过去的参数page
        wait.until(EC.text_to_be_present_in_element_value((By.NAME, 'AspNetPager1_input'), str(page)))
        # 判断是否爬取到上次爬取位置，是的话返回1
        return get_pages(page, judge, judge_name, judge_width)
    except TimeoutException:
        print('爬取第', page, '页索引页time out,尝试重新爬取!————> \t ' + judge_name)
        # 如果timeout，尝试重新获取页面
        index_page(page, judge, judge_name, url, judge_width)
        


def get_pages(page, judge, judge_name, judge_width):
    """
    提取文章内容
    :param page: 页码
    :param judge: 用于判断上次爬取位置
    """
    html = browser.page_source
    result = etree.HTML(html)
    # 获取索引页文章列表内容
    items = result.xpath('//*[@id="DataGrid1"]/tbody//tbody')

    # 写入当前爬取到的第一个文章url：/htmlpaper/2018625148872046611.shtm
    if page == 1:
        # 领域新闻为 @width = "60%" ，
        # next_judge = items[0].xpath('.//td[@width = "60%"]/a/@href')[0]
        # 论文为 @width = "70%"
        # config.judge_width为不同宽度，即： @width = "60%" | @width = "70%"
        next_judge = items[0].xpath('.//td[' + judge_width + ']/a/@href')[0]
        with open(judge_name, 'w', encoding = 'utf-8') as f:
            print(judge_name + "\t<————next_judge————>\t" + next_judge)
            f.write(next_judge)

    # 提取每一个文章的url
    for item in items:
        '''
        content = {
            'title': item.xpath('.//td[@width = "60%"]/a')[0].text.replace('\n','').replace(' ',''),
            'url': item.xpath('.//td[@width = "60%"]/a/@href')[0],
            'from': item.xpath('.//td[@width = "20%"]')[0].text.replace('\n','').replace(' ',''),
            'date': item.xpath('.//td[@width = "10%"]')[0].text.replace('\n','').replace(' ','')
        }
        '''
        # 领域新闻为 @width = "60%" ，
        # kw = item.xpath('.//td[@width = "60%"]/a/@href')[0]
        # 论文为 @width = "70%"
        kw = item.xpath('.//td[' + judge_width + ']/a/@href')[0]
        #title = item.xpath('.//td[@width = "60%"]/a')[0].text.replace('\n','').replace(' ','')

        # 判断是否爬取到上次爬取位置，是的话返回1
        if kw == judge:
            print("已爬取到上次爬取位置！————>\t" + judge_name)
            return 1
            break

        # 组合url
        #url = 'http://paper.sciencenet.cn' + kw
        #print(url)
        #/htmlpaper/201861510484322846535.shtm
        # 提取url中的数字作为文件名保存
        filename_pattern = re.compile(r'[a-zA-Z:\.\/\-\_]')
        filename = filename_pattern.sub('', kw)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
        }
        try:
            url_pattern = re.compile(r'http')
            url_judge = url_pattern.search(kw)
            if url_judge is None:
                url = 'http://news.sciencenet.cn' + kw 
            else:
                url = kw 
            # print(url)
            response = requests.get(url, headers = headers)
            response.encoding = 'utf-8'
            time.sleep(2)
        except ConnectionError:
            print('文章网址有误:' + url)

        # 提取文章中的内容
        detail_pattern = re.compile(r'<table id="content".*<!-- JiaThis Button END -->.*?</table>',re.S)
        source_article = detail_pattern.search(response.text)   
        if source_article:
            source_article = source_article.group()
            # print(source_article)
            # 获取文章中所有的图片url链接: http://www.bio360.net/storage/image/2018/08/FG3XNGQGmD2HxBMqFgNNmiuLNXjTWHU9cnblI8TV.png
            pattern_img = re.compile(r'<img(.*?)\ssrc="(.*?)"', re.I)
            findall_img = pattern_img.findall(source_article)
            # print('findall_img:', type(findall_img), findall_img)
            # judge_img_get:判断能否获取图片
            judge_img_get = True
            for kw in findall_img:
                # kw[1]: http://www.bio360.net/storage/image/2018/08/FG3XNGQGmD2HxBMqFgNNmiuLNXjTWHU9cnblI8TV.png
                # 判断图片URL是否需要组合
                # print('kw[1]',kw[1])
                pattern_judge_img = re.compile(r'http', re.I)
                judge_img = pattern_judge_img.search(kw[1])
                if judge_img:
                    url_full_img = kw[1]
                else:
                    # 图片网址:url_full_img: http://www.bio360.net/storage/image/2018/08/FG3XNGQGmD2HxBMqFgNNmiuLNXjTWHU9cnblI8TV.png
                    url_full_img =  'http://paper.sciencenet.cn' + kw[1]
                    # 图片保存名：dwNNY7cwzRcOcsjRwMFcceLF9qTvhyDP8HiHTgQc.png
                # print('url_full_img:', type(url_full_img), url_full_img)
                pattern_name_save_img = re.compile(r'.*\/(.*\.[jpbg][pmin]\w+)', re.I)
                try:
                    name_save_img = pattern_name_save_img.search(kw[1]).group(1).replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','')
                    # print('name_save_img:', type(name_save_img), name_save_img)
                    # 获取图片
                    response_img = requests.get(url_full_img, headers = headers).content
                    # 保存图片
                    save_img(response_img, name_save_img)
                except:
                    print('图片网址有误:' + '\n' + url_full_img)
                    # 如果图片获取不到，则赋值为false
                    judge_img_get = False
                    break
            # 如果获取得到图片，再进行下一步
            if judge_img_get:
                # 提取url中的154727作为文件名保存: http://www.bio360.net/article/154727
                pattren_filename = re.compile(r'.*\/(.*)?.shtm', re.I)
                filename = pattren_filename.search(url).group(1) + '.html'
                filename = filename.replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','')
                # print(filename)
                # 解析文章，提取有用的内容，剔除不需要的，返回内容列表
                list_article = parse_page(source_article)
                # 保存文章内容 
                save_page(list_article, filename)
            else:
                print('获取不到图片：' + url)
        else:
            print('get_page_error:' + url)

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
    title_article = html_source_local.xpath('//td[@class="style1"]')[1].text.strip()
    title_article = '<title>' + title_article + '</title>\n' + '</head>\n'
    list_article.append(title_article)
    # print(type(title_article),title_article)

    # source_article：来源： 中科普瑞 / 作者：  2018-09-11
    source_article = html_source_local.xpath('//td[@align="left"]/div[1]')[0].text
    # print(source_article)
    pattern_search_source = re.compile(r'来源：(.*?)发布时间', re.I|re.S)
    try:
        result_source = pattern_search_source.search(source_article).group(1).strip()
    except:
        result_source = ''
    pattern_search_time = re.compile(r'\d\d\d\d/\d+/\d+', re.I|re.S)
    try:
        result_time = pattern_search_time.search(source_article).group().strip()
    except:
        result_time = ''
    pattern_search_user_ = re.compile(r'作者：(.*?)来源', re.I|re.S)
    try:
        result_user = pattern_search_user_.search(source_article).group(1).replace('/','').replace('时间：','').strip()
    except:
        result_user = ''
    source_article = '<body>\n' + '<div class = "source">' + result_source + '</div>\n' + '<div class = "user">' + result_user + '</div>\n' + '<div class = "time">' + result_time + '</div>\n' + '<content>\n'
    list_article.append(source_article)
    # print(type(source_article),source_article)

    # 通过正则表达式获取文章中需要的内容，即正文部分
    pattren_article_content = re.compile(r'font-family: 宋体; line-height: 20px;">(.*)<div style="border-bottom:', re.I|re.S)
    source_article = pattren_article_content.search(source_local)

    if source_article:
        source_article = source_article.group(1)

        def img_url_name(match):
            """
            匹配文章内容中的图片url，替换为本地url
            """
            # http://www.bio360.net/storage/image/2018/08/FG3XNGQGmD2HxBMqFgNNmiuLNXjTWHU9cnblI8TV.png
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
        source_local = source_local.replace('&middot;','·').replace('&lsquo;','‘').replace('&rsquo;','’').replace('&mdash;','-').replace('&ldquo;','“').replace('&rdquo;','”').replace('&nbsp;','').replace('&','&amp;').strip()
        pattren_article_change_3 = re.compile(r'(特别声明.*?请与我们接洽。)')
        source_local = pattren_article_change_3.sub('', source_local)
        # 清洗后的正文
        # print(source_local)
        source_local = source_local + '\n</content>\n' + '</body>\n' + '</html>\n'
        list_article.append(source_local)
    
    return list_article

def save_img(source, filename):
    """
    保存文章中的图片
    :param source: 图片文件
    :param filename: 保存的图片名
    """
    dir_save_img = sys.path[0] + '/sciencenet_spider_result/img/'
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
    dir_save_page = sys.path[0] + '/sciencenet_spider_result/'
    if not os.path.exists(dir_save_page):
        os.makedirs(dir_save_page)
    try:
        with open(dir_save_page + filename , 'w', encoding = 'utf-8') as f:
            for i in list_article:
                f.write(i)
    except  OSError as e:
        print('内容保存失败：' + filename + '\n{e}'.format(e = e))

def main():
    """
    遍历每一页索引页
    """
    print("sciencenet_spider爬取开始！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    for wd in range(1):
        # 论文
        if wd == 0:
            # 论文链接
            url = 'http://paper.sciencenet.cn/paper/fieldlist.aspx?id=2'
            # 论文为 @width = "70%"
            judge_width = '@width = "70%"'
            # 论文为总页数为259
            num = 10
            # 领域新闻的判断文件名
            judge_name = sys.path[0] + '/paper_url_judge.txt'
        # if wd == 1:
            # url = 'http://news.sciencenet.cn/fieldlist.aspx?id=3'
            # judge_width = '@width = "60%"'
            # num = 614
            # judge_name = sys.path[0] + '/news_url_judge.txt'

        # 读取上次爬取时保存的用于判断爬取位置的字符串
        # with open(judge_name, 'r', encoding = 'utf-8') as f:
            # judge = f.read()
        judge = 1
        for i in range(1, num):
            params = index_page(i, judge, judge_name, url, judge_width)
            if params == 1:
                break

    browser.close()
    print("sciencenet_spider爬取完毕，脚本退出！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))


if __name__ == '__main__':
    main()













