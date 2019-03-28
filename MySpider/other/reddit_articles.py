# -*- coding:utf-8 -*-

import time
import sys
import requests
import json

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
    for i in range(21):
        
        url = 'https://gateway.reddit.com/desktopapi/v1/subreddits/gonewildstories?rtj=only&redditWebClient=web2x&app=web2x-client-production&layout=card&sort=hot&allow_over18=1&include=prefsSubreddit&dist=' + str(i) + '&after=' + token
        print(url)

        response = requests.get(url, headers=headers)
        gws_dict = json.loads(response.text)
        token = gws_dict['token']
        print(token)
        # with open(r'C:/Users/CRAB/Desktop/gonewildstories.json', 'r', encoding='utf-8') as f:
        #     gws_dict = json.load(f)
        for i in gws_dict['posts'].keys():
            articles_dict = gws_dict['posts'][i]
            # print(articles_dict['title'])
            article_url = articles_dict['permalink']
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
    
    

if __name__ == '__main__':
    print('start\t', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    start = time.time()
    parse_index()
    print('stop\t', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    print('all\t', time.time()-start)
