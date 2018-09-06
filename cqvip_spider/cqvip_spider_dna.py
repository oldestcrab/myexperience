# -*- encoding:utf-8 -*-

import re
import time
import requests
from lxml import etree
from requests import ConnectionError
import random


def index_page(page, judge_page):
    """
    爬取索引页
    :param page:页码
    :param judge: 用于判断上次爬取位置
    """
    # 通过用session保持链接
    # search_session = requests.Session()
    # 要想获取搜索结果的索引页，必须先访问search_url，不然服务器比对cookie错误会返回:对不起，服务器上不存在此用户！可能已经被剔除或参数错误
    # search_url = r'http://kns.cnki.net/kns/request/SearchHandler.ashx?action=&NaviCode=*&ua=1.11&PageName=ASP.brief_default_result_aspx&DbPrefix=SCDB&DbCatalog=%E4%B8%AD%E5%9B%BD%E5%AD%A6%E6%9C%AF%E6%96%87%E7%8C%AE%E7%BD%91%E7%BB%9C%E5%87%BA%E7%89%88%E6%80%BB%E5%BA%93&ConfigFile=SCDBINDEX.xml&db_opt=CJFQ%2CCDFD%2CCMFD%2CCPFD%2CIPFD%2CCCND%2CCCJD&txt_1_sel=SU%24%25%3D|&txt_1_special1=%25&his=0&parentdb=SCDB&__=Thu%20Aug%2009%202018%2015%3A36%3A52%20GMT%2B0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)'
    # 索引页url
    # url_index: http://cqvip.com/data/main/search.aspx?action=so&tid=0&w=&o=&mn=&issn=&cnno=&rid=0&c=&gch=&cnt=&perpage=0&ids=&valicode=&_=1535962010014&k=%E7%94%9F%E7%89%A9&curpage=1
    url_index = 'http://cqvip.com/data/main/search.aspx?action=so&tid=0&w=&o=&mn=&issn=&cnno=&rid=0&c=&gch=&cnt=&perpage=0&ids=&valicode=&_=1535962010014'
    # headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
    # kw_search为search_url的参数，kw_index为index_url的参数，注意：修改kw_search中txt_1_value1的值才会真正返回修改后的搜索结果，kw_index中的keyValue修改与否没有影响。
    # 例如：'txt_1_value1':'生物'，'keyValue':'化学'  ，真正的搜素结果为生物
    if judge_page:
        page_start = int(judge_page)
    else:
        page_start = 1
    for i in range(page_start,page):
        print('开始爬取第' + str(i) + '页！')    
        if i ==page_start or i%5 == 0:
            if i != page_start:
                print('\n============sleeping600s============\n')
                time.sleep(600)
            with open('./user-agents.txt', 'r', encoding = 'utf-8') as f:
                list_user_agents = f.readlines()
                user_agent = random.choice(list_user_agents).strip()
            headers = {'user-agent':user_agent}
            print(headers)
        # elif i%10 == 0:
            # print('\n============sleeping60s============\n')
            # time.sleep(60)
        kw_index = {
            'k':'dna',
            'curpage':i
        }
        try:
            # 获取索引页
            response_index = requests.get(url_index, params = kw_index, headers = headers)
        except ConnectionError:
            print('index_page_ConnectionError and try again!:' + url_index)
            with open('./judge_page_dna.txt', 'w', encoding = 'utf-8') as f:
                print("next_page:\t" + str(i))
                f.write(str(i))
            response_index = requests.get(url_index, params = kw_index, headers = headers)
        response_index.encoding = 'utf-8'
        time.sleep(4)
        print(response_index.url)
        # 通过xpath获取索引页内的文章列表url
        html_index = etree.HTML(response_index.text)
        source_index = html_index.xpath('//ul//th/a/@href')

        # 写入当前爬取到的第一个文章url
        # if i == 1:
            # next_judge = index_source[0]
            # with open('./judge.txt', 'w', encoding = 'utf-8') as f:
                # print("next_judge:\t" + next_judge)
                # f.write(next_judge)
        if source_index:
            # print(i)
            for item in source_index:
                # 判断是否爬取到上次爬取位置,是的话judge_last_spider赋值为False      
                # if item == judge:
                    # print("已爬取到上次爬取位置！")
                    # judge_last_spider = False
                    # break

                # item: \"/QK/70597X/201834/epub1000001383928.html\"
                pattern_item = re.compile(r'http')
                judge_item = pattern_item.search(item)
                if not judge_item:
                    # print('item:', item, type(item))
                    get_page(item)
        else:
            print('source_index get noting:\t' + str(i))
            # judge_times = False
            # print(judge_times)
        

def get_page(url):
    """
    提取文章内容
    :param url:文章假链接、提供真链接需要的参数
    """
    # item: \"/QK/70597X/201834/epub1000001383928.html\"
    # 需要获取的数据：/QK/70597X/201834/epub1000001383928.html
    # 组合后的url可以才可以访问：http://cqvip.com/QK/72177X/201806/epub1000001390926.html
    url_article = 'http://cqvip.com' + url.replace(r'\"','')
    # print(url_article)
    # headers = {'user-agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)'}
    with open('./user-agents.txt', 'r', encoding = 'utf-8') as f:
        list_user_agents = f.readlines()
        user_agent = random.choice(list_user_agents).strip()
    headers = {'user-agent':user_agent}
    # 获取文章
    try:
        response_article = requests.get(url_article,  headers = headers)
    except:
        print('ConnectionError article_response:')
        response_article = requests.get('https://www.baidu.com')
    response_article.encoding = 'utf-8'
    source_article = response_article.text
    time.sleep(4)
    # except ConnectionError:
        # print('response_article error:' + url_article)
        # response_article = ''
    # 通过xpath获取文章中的关键字|有序介孔生物玻璃; 掺杂离子; 生物性能;
    html_article = etree.HTML(source_article)
    kw_article = html_article.xpath('//table[2]//tr[2]//td[2]/a')
    
    # 有的文章没有关键字，先确认有没有
    if kw_article:
        for kw in kw_article:
            save_page(kw.text)

    else:
        # print('get_page_error:\t' + article_response.url)
        pass

def save_page(kw):
    """
    保存文章内容
    :param kw:提取出来的关键字
    """
    if kw:
        with open('./kw_dna.txt', 'a', encoding = 'utf-8') as f:
            f.write(str(kw) + '\n')

def main():
    """
    遍历每一页索引页
    """
    print("cqvip_spider爬取开始！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

    # 读取上次爬取时保存的用于判断爬取位置的字符串
    with open('./judge_page_dna.txt', 'r', encoding = 'utf-8') as f:
            judge_page = f.read()
    # judge = 2
    index_page(200, judge_page)

    print("cqvip_spider爬取完毕，脚本退出！")
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))


if __name__ == '__main__':
    main()


# http://cqvip.com/data/main/search.aspx?action=so&tid=0&k=%E7%94%9F%E7%89%A9&w=&o=&mn=&issn=&cnno=&rid=0&c=&gch=&cnt=&curpage=2&perpage=0&ids=&valicode=&_=1535962010014


