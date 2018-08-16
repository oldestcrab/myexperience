# -*- encoding:utf-8 -*-

import re
import time
import requests
from lxml import etree
from requests import ConnectionError


def index_page(page, judge):
    """
    爬取索引页
    :param page:页码
    :param judge: 用于判断上次爬取位置
    """
    # 通过用session保持链接
    search_session = requests.Session()
    # 要想获取搜索结果的索引页，必须先访问search_url，不然服务器比对cookie错误会返回:对不起，服务器上不存在此用户！可能已经被剔除或参数错误
    search_url = r'http://kns.cnki.net/kns/request/SearchHandler.ashx?action=&NaviCode=*&ua=1.11&PageName=ASP.brief_default_result_aspx&DbPrefix=SCDB&DbCatalog=%E4%B8%AD%E5%9B%BD%E5%AD%A6%E6%9C%AF%E6%96%87%E7%8C%AE%E7%BD%91%E7%BB%9C%E5%87%BA%E7%89%88%E6%80%BB%E5%BA%93&ConfigFile=SCDBINDEX.xml&db_opt=CJFQ%2CCDFD%2CCMFD%2CCPFD%2CIPFD%2CCCND%2CCCJD&txt_1_sel=SU%24%25%3D|&txt_1_special1=%25&his=0&parentdb=SCDB&__=Thu%20Aug%2009%202018%2015%3A36%3A52%20GMT%2B0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)'
    # 索引页url
    index_url = 'http://kns.cnki.net/kns/brief/brief.aspx'
    headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
    # kw_search为search_url的参数，kw_index为index_url的参数，注意：修改kw_search中txt_1_value1的值才会真正返回修改后的搜索结果，kw_index中的keyValue修改与否没有影响。
    # 例如：'txt_1_value1':'生物'，'keyValue':'化学'  ，真正的搜素结果为生物
    kw_search = {
        'txt_1_value1':'生物',
    }
    for i in range(1,page):
        judge_times = True
        if i == 1:
            judge_times = False
        elif i%15==0:
            print('=====sleeping300s=====')
            time.sleep(300)
            judge_times = False
        if not judge_times:
            # 先访问search_url与服务器建立一个session会话，保持同一个cookie
            search_session.get(search_url, params = kw_search, headers = headers)
        curpage =  i
        lastpage = i*10-10
        kw_index = {
            'curpage':curpage,
            'RecordsPerPage':'50',
            'QueryID':'0',
            'ID':'',
            'turnpage':'1',
            'tpagemode':'L',
            'dbPrefix':'SCDB',
            'Fields':'',
            'DisplayMode':'listmode',
            'pagename':'ASP.brief_default_result_aspx'  
        }   
        try:
            response_index = search_session.get(index_url, params = kw_index, headers = headers)
            response_index.encoding = 'utf-8'
            time.sleep(3)
            print(response_index.url)
        except ConnectionError:
            print('index_page_ConnectionError:' + index_url)
        with open('./cnki_net_spider/test' + str(i) + '.html', 'w', encoding = 'utf-8') as f:
            f.write(response_index.text)
        # 通过xpath获取索引页内的文章列表

# 索引页的文章列表，10个a标签
# //a[@class = "fz14"]
# 11.2184.Q.20180813.1709.003
# 获取的文章通过最后的这个ID进行索引
# http://kns.cnki.net/KCMS/detail/11.2184.Q.20180813.1709.003.html

def main():
    """
    遍历每一页索引页
    """
    # 读取上次爬取时保存的用于判断爬取位置的字符串
    with open('./kepu_net_spider/judge.txt', 'r', encoding = 'utf-8') as f:
            judge = f.read()
    # judge = 2

    # for i in range(6):
    # params = index_page(56, judge)
    index_page(20, judge)
    # if params == 1:
        # break
    # print('保存第', str(i+1), '页索引页所有文章成功')  
    print("爬取完毕，脚本退出！")

if __name__ == '__main__':
    main()