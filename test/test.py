import time
import requests
from lxml import etree
import re
    
url_article = 'http://kns.cnki.net/KCMS/detail/detail.aspx?FileName=WSXB20180621000&DbName=CAPJLAST&DbCode=CJFQ'
headers = {'user-agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)'}
# 获取文章
article_response = requests.get(url_article, headers = headers)
article_response.encoding = 'utf-8'
print(article_response.url)
time.sleep(2)
# 通过xpath获取文章中的关键字|有序介孔生物玻璃; 掺杂离子; 生物性能;
html_article = etree.HTML(article_response.text)
kw_article = html_article.xpath('//label[@id="catalog_KEYWORD"]/../a')
# print(kw_article)
    # 有的文章没有关键字，先确认有没有
if kw_article:
    for kw in kw_article:
        # print(kw.text)
        try:
            kw_real = re.sub('\s|;','',kw.text)
        except:
            kw_real = None
            # print('TypeError, UnboundLocalError')
        # 保存文章内容 
        if kw_real:
            print(kw_real)