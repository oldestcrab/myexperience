# -*- encoding:utf-8 -*-

import requests
from lxml import etree
import time
import re
from requests import ConnectionError

def index_page(page):
    """
    爬取索引页
    :param page:页码
    """
    if page == 0:
        url = 'http://www.ioz.ac.cn/xwzx/kyjz/index.html'
    else:
        url = 'http://www.ioz.ac.cn/xwzx/kyjz/index_' + str(i) + '.html'
    print('正在爬取第' + str(page+1) + '页索引页')

    # 获取索引页
    headers = {'user-agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; Zune 4.0; InfoPath.3; MS-RTC LM 8; .NET4.0C; .NET4.0E)'}
    try:
        response = requests.get(url, headers = headers)
        response.encoding = 'utf-8'
        time.sleep(1)
    except ConnectionError:
        print('ConnectionError:' + url)

    # 通过xpath获取索引页内的文章列表
    index_html = etree.HTML(response.text)
    index_source = index_html.xpath('//table[@class = "hui12_sj2"]//a')
    for item in index_source:
        # 获取索引页内所有文章的标题
        index_title = item.text
        # 获取索引页内所有文章的url
        index_url = item.xpath('@href')[0].replace('./','/',)
        # print(index_url,type(index_url))

        get_page(index_url)

def get_page(url):
    """
    提取文章内容
    :param url:文章链接
    """
    # 组合url
    full_url = 'http://www.ioz.ac.cn/xwzx/kyjz' + url
    # 获取文章内容
    headers = {'user-agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)'}
    article_response = requests.get(full_url, headers = headers)
    article_response.encoding = 'utf-8'
    time.sleep(1)

    # 通过正则表达式获取文章中需要的内容
    article_pattern = re.compile(r'<table width="650" border="0" align="center" cellpadding="0" cellspacing="0">.*?<td class="bk_d1"></td>', re.S)
    article_source = article_pattern.search(article_response.text)
    #print(article_source.group())
    save_page(article_source.group())

def save_page(html):
    """
    保存到文件
    :param html: 结果
    """
    with open('./ioz_ac_spider/result.html', 'w', encoding = 'utf-8') as f:
        f.write(html)
    print('sldjgss')
def main():
    """
    遍历每一页索引页
    """
    for i in range(1):
        index_page(i) 

if __name__ == '__main__':
    main()