# -*- encoding:utf-8 -*-

import re
import time
import requests
from lxml import etree
from requests import ConnectionError
import sys
import os
import random




def index_page(page, judge, dir_judge, url):

    # judge_last_spider：用于判断是否爬取到上次爬取位置
    judge_last_spider = True
    
    for i in range(1,page):    
        # 如果judge_last_spider为False，则退出循环！
        if not judge_last_spider:
            break
        print('正在爬取第' + str(i) + '页！\t' )

        url_full = url + str(i)
        # print('url_full',url_full)
        with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
            list_user_agents = f.readlines()
            user_agent = random.choice(list_user_agents).strip()
        headers = {'user-agent':user_agent}
        try:
            # 获取索引页
            response_index = requests.get(url_full, headers = headers)
            response_index.encoding = 'utf-8'
            time.sleep(2)
            # print(response_index.url)
        except ConnectionError:
            print('index_page_ConnectionError:' + url)

        if response_index:
            # 通过xpath获取索引页内的文章列表url
            # print(response_index.text)
            html_index = etree.HTML(response_index.text)
            # source_index = html_index.xpath('//table[@summary="forum_103"]/tbody//th[@class="common"]')
            source_index = html_index.xpath('//a[@class="s xst"]')

            # 写入当前爬取到的第一个文章url
            if i == 1 and source_index:
                judge_next = html_index.xpath('//a[@class="s xst"]/@href')[0]
                # print(judge_next)
                with open(dir_judge, 'w', encoding = 'utf-8') as f:
                    print("judge_next:\t" + judge_next)
                    f.write(judge_next)

            for item in source_index:
                # 判断是否爬取到上次爬取位置,是的话judge_last_spider赋值为False      
                if judge_next == judge:
                    print("已爬取到上次爬取位置！")
                    judge_last_spider = False
                    break

                url_index = item.xpath('@href')[0]  
                # print('url_index',url_index)
                title_index = item.text 
                # print('title_index',title_index)    

                # item: ./201810/t20181029_5151255.html
                # print(item)
                get_page(url_index, title_index)
        
def get_page(url_index, title_index):

    url_full = 'http://7sht.me/' + url_index
    # print(url_full)
    with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
        list_user_agents = f.readlines()
        user_agent = random.choice(list_user_agents).strip()
    headers = {'user-agent':user_agent}
    # 获取文章
    try:
        response_article = requests.get(url_full, headers = headers)
        response_article.encoding = 'utf-8'
        time.sleep(1)
    except:
        print('get_page error' + url_full)

    if response_article:
        # 通过正则表达式获取文章中需要的内容
        pattren_article = re.compile(r'【出演女优】：(.*?)<br{1}', re.S|re.I)
        source_article = pattren_article.search(response_article.text)
        # print(source_article)
        if source_article:
            source_article = source_article.group(1).strip()
            title_index = title_index.replace('[高清中文字幕]','')
            dir_save_page = sys.path[0] + '/source/'
            if not os.path.exists(dir_save_page):
                os.makedirs(dir_save_page)
            # content = '[' + source_article + ' | ' + title_index + '](' + url_full + ')'
            content = '<a href ="' + url_full + '">' + source_article + ' | ' + title_index + '</a><br/>' 
            # print(content)
            # with open(dir_save_page + source_article + '.md', 'a', encoding = 'utf-8') as f:
            with open(dir_save_page + 'source_article' + '.html', 'a', encoding = 'utf-8') as f:
                f.write(content + '\n')

def main():
    """
    遍历每一页索引页
    """
    print("爬取开始！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

    # 用for循环遍历爬取不同分类下的文章
    for wd in range(1):

        if wd == 0:
            judge_name = 'judge_chinese.txt'
            url_kw = 'http://7sht.me/forum.php?mod=forumdisplay&fid=103&orderby=dateline&filter=author&page='
            num = 9
        dir_judge = sys.path[0] + '/' + judge_name
        if not os.path.exists(dir_judge):
            with open(dir_judge, 'w', encoding = 'utf-8'):
                print('创建文件：' + dir_judge) 
        # 读取上次爬取时保存的用于判断爬取位置的字符串
        # with open(dir_judge, 'r', encoding = 'utf-8') as f:
                # judge = f.read()
        judge = 1
        index_page(num, judge, dir_judge, url_kw)

    print("爬取完毕，脚本退出！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))


if __name__ == '__main__':
    main()