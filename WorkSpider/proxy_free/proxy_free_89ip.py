import requests
import json
import sys
import random
from lxml import etree
import time

def get_proxy(url_kw, num):
    for i in range(1,num):
        print('正在爬取第' + str(i) + '页高匿代理!')
        url_full = url_kw + str(i) + '.html'
        # print(url_full)
        with open(sys.path[0] + '/user-agents.txt', 'r' , encoding = 'utf-8') as f:
            list_user_agent = f.readlines()
        user_agent = random.choice(list_user_agent).strip()
        # print(user_agent)
        headers = {'user-agent':user_agent}
        try:
            response = requests.get(url_full, headers = headers)
            response.encoding = 'utf-8'
            time.sleep(1)
            # response = requests.get(url, headers = headers)
        except:
            response = ''
        # print(response.url)
        if response:
            # print(response.text)
            html_proxy = etree.HTML(response.text)
            source_proxy = html_proxy.xpath('//table[@class="layui-table"]//tr')
            # print(source_proxy)
            for proxy in source_proxy:
                list_ip_proxy = proxy.xpath('./td[1]')
                list_port_proxy = proxy.xpath('./td[2]')
                if list_ip_proxy and list_ip_proxy :
                    ip_proxy = list_ip_proxy[0].text
                    port_proxy = list_port_proxy[0].text
                    # print(ip_proxy, port_proxy)
                    test_proxy(ip_proxy, port_proxy)

def test_proxy(ip_proxy, port_proxy):
    url = 'http://httpbin.org/get'
    with open(sys.path[0] + '/user-agents.txt', 'r' , encoding = 'utf-8') as f:
        list_user_agent = f.readlines()
    user_agent = random.choice(list_user_agent).strip()
    # print(user_agent)
    headers = {'user-agent':user_agent}
    # print(headers)
    # proxy = '125.46.0.62:53281'
    # ip_proxy = '61.183.233.6'
    # port_proxy = '54896'
    proxy = ip_proxy.strip() + ':' + port_proxy.strip()
    # print(proxy)
    proxies = {
        'http':'http://' + proxy ,
        'https':'https://' + proxy 
    }
    try:
        response = requests.get(url, headers = headers, proxies = proxies, timeout = 4)
        # response = requests.get(url, headers = headers)
    except:
        response = ''
    if response:
        try:
            dict_response = json.loads(response.content)
            ip_response = dict_response['origin']
        except:
            ip_response = ''
        # print(type(ip_response))
        if ip_response == ip_proxy:
            print('get:  ' + proxy)
            with open(sys.path[0] + '/ip_response.txt', 'a', encoding = 'utf-8') as f:
                f.write(proxy + '\n')
            # print(dict_response['headers']['User-Agent'])

def main():
    print('程序开始！  ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    url_get_proxy = 'http://www.89ip.cn/index_'
    num = 100
    get_proxy(url_get_proxy, num)
    print('程序结束！  ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

if __name__ == "__main__":
    main()