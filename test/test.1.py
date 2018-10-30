from lxml import etree
import requests
try:
    # 获取索引页
    headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

    response_index = requests.get('http://www.genetics.ac.cn/xwzx/kyjz/201806/t20180613_5025584.html', headers = headers)
    response_index.encoding = 'utf-8'
    # time.sleep(2)
    # print(response_index.url)
except ConnectionError:
    print('index_page_ConnectionError:' )
html_source_local = etree.HTML(response_index.text) 


# print(type(html_source_local),html_source_local)
# title_article: 第四届发育和疾病的表观遗传学上海国际研讨会在沪隆重开幕
title_article = ''.join(html_source_local.xpath('//td[@class="detail_title"]/text()'))
print(title_article)