# -*- encoding:utf-8 -*-

import json
import re
import requests
from lxml import etree
import random
import sys
import time

class ProxyMataclass(type):
    def __new__(cls, name, bases, attrs):
        count = 0
        attrs['__CrawlFunc__'] = []

        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append(k)
                count +=1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)


class Crawler(object, metaclass = ProxyMataclass):
    def get_proxies(self, callback):
        """
        :return: 返回爬取到的代理
        """
        proxies = []
        for proxy in eval("self.{}()".format(callback)):
            proxies.append(proxy)
        return proxies

    def crawl_xicidaili(self):
        """
        爬取代理：https://www.xicidaili.com/wt/
        :yield: 返回爬取到的代理
        """
        for i in range(1,4):
            url_full = 'https://www.xicidaili.com/wt/' + str(i)
            with open(sys.path[0] + '/proxypool/user-agents.txt', 'r' , encoding = 'utf-8') as f:
                list_user_agent = f.readlines()
            user_agent = random.choice(list_user_agent).strip()
            headers = {'user-agent':user_agent}
            try:
                response = requests.get(url_full, headers = headers)
                response.encoding = 'utf-8'
                time.sleep(1)
            except:
                response = ''
            if response:
                html_proxy = etree.HTML(response.text)
                source_proxy = html_proxy.xpath('//table[@id="ip_list"]/tr')
                for proxy in source_proxy:
                    list_ip_proxy = proxy.xpath('./td[2]')
                    list_port_proxy = proxy.xpath('./td[3]')
                    judge_proxy = proxy.xpath('./td[5]')
                    if list_ip_proxy and list_ip_proxy and judge_proxy:
                        judge_proxy = judge_proxy[0].text
                        if judge_proxy == '高匿':
                            ip_proxy = list_ip_proxy[0].text
                            port_proxy = list_port_proxy[0].text
                            address_port = ip_proxy.strip()+':'+port_proxy.strip()
                            yield address_port
    
    def crawl_kuaidaili(self):
        """
        爬取代理：https://www.kuaidaili.com/free/inha/
        :yield: 返回爬取到的代理
        """
        for i in range(1, 4):
            url_full = 'https://www.kuaidaili.com/free/inha/' + str(i)
            with open(sys.path[0] + '/proxypool/user-agents.txt', 'r' , encoding = 'utf-8') as f:
                list_user_agent = f.readlines()
            user_agent = random.choice(list_user_agent).strip()
            headers = {'user-agent':user_agent}
            try:
                response = requests.get(url_full, headers = headers)
                response.encoding = 'utf-8'
                time.sleep(1)
            except:
                response = ''
            if response:
                html_proxy = etree.HTML(response.text)
                source_proxy = html_proxy.xpath('//table[@class="table table-bordered table-striped"]//tr')
                for proxy in source_proxy:
                    list_ip_proxy = proxy.xpath('./td[@data-title="IP"]')
                    list_port_proxy = proxy.xpath('./td[@data-title="PORT"]')
                    if list_ip_proxy and list_ip_proxy :
                        ip_proxy = list_ip_proxy[0].text
                        port_proxy = list_port_proxy[0].text
                        address_port = ip_proxy.strip()+':'+port_proxy.strip()
                        yield address_port

    def crawl_89ip(self):
        """
        爬取代理：http://www.89ip.cn/index_1.html
        :yield: 返回爬取到的代理
        """
        for i in range(1, 4):
            url_full = 'http://www.89ip.cn/index_' + str(i) + '.html'
            with open(sys.path[0] + '/proxypool/user-agents.txt', 'r' , encoding = 'utf-8') as f:
                list_user_agent = f.readlines()
            user_agent = random.choice(list_user_agent).strip()
            headers = {'user-agent':user_agent}
            try:
                response = requests.get(url_full, headers = headers)
                response.encoding = 'utf-8'
                time.sleep(1)
            except:
                response = ''
            if response:
                html_proxy = etree.HTML(response.text)
                source_proxy = html_proxy.xpath('//table[@class="layui-table"]//tr')
                for proxy in source_proxy:
                    list_ip_proxy = proxy.xpath('./td[1]')
                    list_port_proxy = proxy.xpath('./td[2]')
                    if list_ip_proxy and list_ip_proxy :
                        ip_proxy = list_ip_proxy[0].text
                        port_proxy = list_port_proxy[0].text
                        address_port = ip_proxy.strip()+':'+port_proxy.strip()
                        yield address_port