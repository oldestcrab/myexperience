import time
import requests
import sys
import random
from lxml import etree

while True:
    print('================================================\n')
    url = 'http://www.vigenebio.com/search/search.php?keyword=AA2'
    print( ': url:\t' + url)
    # 随机获取user-agent
    with open(sys.path[0] + '/user-agents.txt', 'r' , encoding = 'utf-8') as f:
        list_user_agent = f.readlines()
    user_agent = random.choice(list_user_agent).strip()
    # print(user_agent)
    try:
        aa = requests.get('http://127.0.0.1:5555/random')
        aaa = aa.text
        print(aaa)
    except:
        print('aaaa')
        aaa = ''
    headers = {'user-agent':user_agent}
    proxies = {
        'http':'http://' + aaa ,
        'https':'https://' + aaa
    }
    print(proxies)
    try:
        # 尝试获取页面资源
        response = requests.get(url, headers = headers, proxies = proxies, timeout = 4)
        response.encoding = 'gb2312'
    except:
        print(': can\'t get source_page！!\t' )
        response = ''
    if response:
        print(': get source_page！')
        content = response.text
        # print(content)
        source_html = etree.HTML(content)

        source = source_html.xpath('//table[@width="980"]/tr')
        print(type(source),source)
        if source:
            del source[0]
            print(source)
            for kw in source:
                Catalog_Number = kw.xpath('./td[1]')[0].text
                Gene_Symbol = kw.xpath('./td[2]')[0].text
                Species = kw.xpath('./td[3]')[0].text
                Product_names = kw.xpath('./td[4]/a')[0].text
                Description = kw.xpath('./td[5]')[0].text
                Price = kw.xpath('./td[6]')[0].text
                Delivery = kw.xpath('./td[7]')[0].text
                print(Catalog_Number + '\t')
                print(Gene_Symbol + '\t')
                print(Species + '\t')
                print(Product_names + '\t')
                print(Description + '\t')
                print(Price + '\t')
                print(Delivery + '\t')
            
        
