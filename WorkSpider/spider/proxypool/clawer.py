# -*- coding:utf-8 -*-

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
        attrs['__CrawFunc__'] = []

        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append(k)
                count += 1
        
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)

class Clawer(object, mataclass = ProxyMataclass):
    def get_proxies(self, callback):
        proxies = []
        for proxy in eval('slef.{}()'.format(callback)):
            proxies.append(proxy)
        return proxies


class Getter()
    def __init__(self):
        self.redis = RedisClient()
        self.Crawler = crawler()

    def is_over_threshole(slef):
        if self.redis.count() >= POOL_UPPER_THRESHOLD:
            return True
        else:
            return False
    def run(self):
        print('获取器开始运行！')
        if not self.is_over_threshole():
            for callback_laber in range(self.crawler.['__CrawlFuncCount__']):
                callback = self.crawler.['__CrawlFunc__'][callback_laber]
                proxies = self.crawler.get_proxies(callback)
                sys.stdout.flush()
                for proxy in proxies:
                    self.redis.add(proxy)