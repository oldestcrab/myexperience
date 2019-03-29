# -*- coding:utf-8 -*-

import time
import sys
import requests
import json
from lxml import etree

def parse_index():
    """
    解析index
    """
    headers ={
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    
    }
    token = ''
    for i in range(51):
        print('正在爬取第' + str(i) + '页')
        url = 'https://gateway.reddit.com/desktopapi/v1/subreddits/gonewildstories?rtj=only&redditWebClient=web2x&app=web2x-client-production&layout=card&sort=top&t=all&allow_over18=1&include=prefsSubreddit&dist=' + str(i) + '&after=' + token
        # print(url)

        response = requests.get(url, headers=headers)
        gws_dict = json.loads(response.text)
        token = gws_dict['token']
        # print(token)
        # with open(r'C:/Users/CRAB/Desktop/gonewildstories.json', 'r', encoding='utf-8') as f:
        #     gws_dict = json.load(f)
        if i > 41:
            for i in gws_dict['posts'].keys():
                articles_dict = gws_dict['posts'][i]
                # print(articles_dict['title'])
                article_url = articles_dict['permalink']
                # print(article_url)
                parse_article(article_url)

def parse_article(article_url):
    """
    解析文章
    """
    headers ={
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }
    response = requests.get(article_url, headers=headers)
    result = etree.HTML(response.text)
    # 获取标题
    try:
        article_title = result.xpath('//h2[@class="s1okktje-0 eYgaub"]')[0].text
    except Exception as e:
        article_title = ''
        print('get article title error', e.args)
    # print(article_title)
    # 获取正文
    try:
        article_content = ''
        # article_content = result.xpath('string(//div[@data-click-id="text"]/div[@class="fo16tt-0 bJBAtI"])')
        content = result.xpath('//div[@data-click-id="text"]/div[@class="fo16tt-0 bJBAtI"]/p')
        for i in content:
            paragraph = i.xpath('string(.)')
            article_content = article_content + '\t' + paragraph + '\n'
    except Exception as e:
        article_content = ''
        print('get article content error', e.args)
    # print(article_content)
    # 储存文章
    save_article(article_title, article_content)

def save_article(article_title, article_content):
    """
    储存文章
    :params article_title: 文章标题
    :params article_content: 文章正文
    """
    global count
    with open(r'C:/Users/CRAB/Desktop/This Is What It Takes.txt', 'a', encoding='utf-8') as f:
        f.write('\n第00' + str(count) + '章\n\n')
        f.write('\t' + article_title + '\n')
        f.write(article_content + '\n')
    count += 1

count = 1

if __name__ == '__main__':
    print('start\t', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    start = time.time()
    parse_index()
    print('stop\t', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    print('all\t', time.time()-start)
