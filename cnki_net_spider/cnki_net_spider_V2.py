# -*- encoding:utf-8 -*-

import re
import time
import requests
from lxml import etree
from requests import ConnectionError
import random


def index_page(page, judge):
    """
    爬取索引页
    :param page:页码
    :param judge: 用于判断上次爬取页数
    """
    # 通过用session保持链接
    search_session = requests.Session()
    # 要想获取搜索结果的索引页，必须先访问search_url，不然服务器比对cookie错误会返回:对不起，服务器上不存在此用户！可能已经被剔除或参数错误
    search_url = r'http://kns.cnki.net/kns/request/SearchHandler.ashx?action=&NaviCode=*&ua=1.11&PageName=ASP.brief_default_result_aspx&DbPrefix=SCDB&DbCatalog=%E4%B8%AD%E5%9B%BD%E5%AD%A6%E6%9C%AF%E6%96%87%E7%8C%AE%E7%BD%91%E7%BB%9C%E5%87%BA%E7%89%88%E6%80%BB%E5%BA%93&ConfigFile=SCDBINDEX.xml&db_opt=CJFQ%2CCDFD%2CCMFD%2CCPFD%2CIPFD%2CCCND%2CCCJD&txt_1_sel=SU%24%25%3D|&txt_1_special1=%25&his=0&parentdb=SCDB&__=Thu%20Aug%2009%202018%2015%3A36%3A52%20GMT%2B0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)'
    # 索引页url
    index_url = 'http://kns.cnki.net/kns/brief/brief.aspx'
    # headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
    # kw_search为search_url的参数，kw_index为index_url的参数，注意：修改kw_search中txt_1_value1的值才会真正返回修改后的搜索结果，kw_index中的keyValue修改与否没有影响。
    # 例如：'txt_1_value1':'生物'，'keyValue':'化学'  ，真正的搜素结果为生物
    kw_search = {
        'txt_1_value1':'细胞',
    }

    # judge_last_spider：用于判断是否爬取到上次爬取位置
    judge_last_spider = True
    # judge_times： 判断是否需要使用session保持链接
    judge_times = True
    # 当judge_none为1时存入当前页数，也就是第一次访问不到资源的页数
    judge_none = 0
    # 如果judge_page.txt里面不为空，则把读取的数字化为整形，不然开始页数为1
    if judge:
        page_start = int(judge)
    else:
        page_start = 1

    for i in range(page_start,page):
        print('开始爬取第' + str(i) + '页！')    
        # 如果judge_last_spider为假，则退出整个循环，爬取结束
        if judge_none > 4:
            break

        # 在爬取15页索引页之后需要输入验证码，每爬15页暂停5分钟再开始爬取
        # 一开始爬取需要使用session保持链接
        if i == page_start:
            judge_times = False
        # elif i%20==0:
        #    print('=====sleepings=====')
        #    time.sleep(120)
        #    judge_times = False

        # 如果judge_times为假，则建立一个session会话
        if not judge_times or i%5==0:
            # 先访问search_url与服务器建立一个session会话，保持同一个cookie

            # 若非开始爬取页数，则是获取不到资源，等待3分钟之后再尝试建立一个session会话
            if i != page_start:
                print('\n============sleeping 300s============\n')
                time.sleep(300)
            
            # 随机选择一个user-agent
            with open('cnki_net_spider/user-agents.txt', 'r', encoding = 'utf-8') as f:
                list_user_agents = f.readlines()
                user_agent = random.choice(list_user_agents).strip()
            headers = {'user-agent':user_agent}
            print(headers)

            # 建立一个session会话
            search_session.get(search_url, params = kw_search, headers = headers)
            print('search_session_get')



        # curpage 当前页
        curpage =  i
        # lastpage 上一页
        lastpage = i*10-10
        # kw_index index_url的参数
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
            # 获取索引页
            response_index = search_session.get(index_url, params = kw_index, headers = headers)
        except ConnectionError:
            print('index_page_ConnectionError，sleeping 10s and try again!:' + index_url)
            # 30S后尝试再访问一次
            time.sleep(10)
            response_index = search_session.get(index_url, params = kw_index, headers = headers)
        response_index.encoding = 'utf-8'
        time.sleep(1)
        print(response_index.url)

        # 通过xpath获取索引页内的文章列表url
        index_html = etree.HTML(response_index.text)
        index_source = index_html.xpath('//a[@class = "fz14"]/@href')

        # 写入当前爬取到的第一个文章url
        # if i == 1:
            # next_judge = index_source[0]
            # with open('cnki_net_spider/judge.txt', 'w', encoding = 'utf-8') as f:
                # print("next_judge:\t" + next_judge)
                # f.write(next_judge)

        # 先判断是否能获取文章列表url
        if index_source:
            # 如果能获取文章列表url，则可以尝试爬取下一页，不用再次建立一个session会话
            judge_times = True
            for item in index_source:  
                # if item == judge:
                    # print("已爬取到上次爬取位置！")
                    # judge_last_spider = False
                    # break

                # item: /kns/detail/detail.aspx?QueryID=0&CurRec=50&recid=&FileName=ZGPX2017062104E&DbName=CAPJLAST&DbCode=CJFQ&yx=Y&pr=&URLID=11.2905.G4.20170621.2131.094
                # print('item:', item, type(item))
                get_page(item)
        else:
            # 如果不能获取文章列表url，则judge_none + 1，同时judge_times为False，重新建立一个session会话
            print('url get noting:\t' + str(i))
            judge_none += 1
            print(judge_none)
            judge_times = False
            # judge_last_spider = False
            # print(judge_times)

            # 当judge_none为1时存入当前页数，即第一次获取不到资源，下次从这里开始爬取！
            if judge_none == 1:
                with open('cnki_net_spider/judge_page.txt', 'w', encoding = 'utf-8') as f:
                    print("next_page:\t" + str(i))
                    f.write(str(i))
        

def get_page(url):
    """
    提取文章内容
    :param url:文章假链接、提供真链接需要的参数
    """
    # item: /kns/detail/detail.aspx?QueryID=0&CurRec=50&recid=&FileName=ZGPX2017062104E&DbName=CAPJLAST&DbCode=CJFQ&yx=Y&pr=&URLID=11.2905.G4.20170621.2131.094
    # 需要获取的数据：FileName=ZGPX2017062104E&DbName=CAPJLAST&DbCode=CJFQ
    # 组合后的url可以才可以访问：http://kns.cnki.net/KCMS/detail/detail.aspx?FileName=NFNY2016120700B&DbName=CAPJLAST&DbCode=CJFQ
    FileName_pattern = re.compile(r'FileName=(.*?)&', re.I)
    DbName_pattern = re.compile(r'DbName=(.*?)&', re.I)
    DbCode_pattern = re.compile(r'DbCode=(.*?)&', re.I)
    url_filename = FileName_pattern.search(url).group(1)
    url_dbname = DbName_pattern.search(url).group(1)
    url_dbcode = DbCode_pattern.search(url).group(1)
    # print(url_filename,url_dbname,url_dbcode)

    kw = {
        'FileName':url_filename,
        'DbName':url_dbname,
        'DbCode':url_dbcode
    }
    url_article = 'http://kns.cnki.net/KCMS/detail/detail.aspx?'
    # 随机选择一个user-agent    
    with open('cnki_net_spider/user-agents.txt', 'r', encoding = 'utf-8') as f:
        list_user_agents = f.readlines()
        user_agent = random.choice(list_user_agents).strip()
    headers = {'user-agent':user_agent}
    # 获取文章
    try:
        article_response = requests.get(url_article, params = kw, headers = headers)
    except ConnectionError:
        # 如果链接错误，则放弃爬取此文章页面，获取百度页面，xpath匹配不到，不写入。脚本继续爬取，避免因此中断
        print('ConnectionError article_response，get baidu!')
        article_response = requests.get('https://www.baidu.com')
    article_response.encoding = 'utf-8'
    # print(article_response.url)
    time.sleep(2)

    # 通过xpath获取文章中的关键字|有序介孔生物玻璃; 掺杂离子; 生物性能;
    html_article = etree.HTML(article_response.text)
    kw_article = html_article.xpath('//label[@id="catalog_KEYWORD"]/../a')
    
    # 有的文章没有关键字，先确认有没有
    if kw_article:
        for kw in kw_article:
            try:
                # 替换关键字中的无关字符
                kw_real = re.sub('\s|;','',kw.text)
            except TypeError:
                kw_real = None
            # 保存文章内容 
            if kw_real:
                save_page(kw_real)

    else:
        # print('get_page_error:\t' + article_response.url)
        pass

def save_page(kw):
    """
    保存文章内容
    :param kw:提取出来的关键字
    """
    with open('cnki_net_spider/kw_xibao.txt', 'a', encoding = 'utf-8') as f:
        f.write(kw + '\n')

def main():
    """
    遍历每一页索引页
    """
    print("cnki_net_spider爬取开始！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

    # 读取上次爬取时最后的爬取页数，此次爬取从此页数开始
    with open('cnki_net_spider/judge_page.txt', 'r', encoding = 'utf-8') as f:
            judge = f.read()
    index_page(120, judge)

    print("cnki_net_spider爬取完毕，脚本退出！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))


if __name__ == '__main__':
    main()
