# -*- coding:utf-8 -*-

from requests import Session
from settings import *
from request import WeixinRequest
import requests
from db import RedisQueue
from pyquery import PyQuery as pq
from mysql import MySQL

class Spider():
    queue = RedisQueue()
    keyword = 'NBA'
    url = 'https://weixin.sogou.com/weixin?type=2&s_from=input&query=' + keyword
    headers ={
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2,mt;q=0.2',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': 'IPLOC=CN4401; SUID=28CB5E7D3020910A000000005C6225BE; SUV=1549936064592885; pgv_pvi=8287179776; ABTEST=0|1552986153|v1; weixinIndexVisited=1; sct=45; SNUID=D4E773512C28A8D914386FB32D1B245E',
    'Host': 'weixin.sogou.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    
    }
    session = Session()
    mysql = MySQL()
        

    def get_proxy(self):
        """
        从代理池获取代理
        :return: proxy or None
        """
        try:
            response = requests.get(PROXY_POOL_URL)
            if response.status_code == 200:
                print('Get Proxy', response.text)
                return response.text
            return None
        except Exception as e:
            print('get proxy error', e.args)
            return None
    
    def start(self):
        """
        初始化工作
        """
        # 全局更新Headers
        self.session.headers.update(self.headers)
        weixin_request = WeixinRequest(url=self.url, callback=self.parse_index, need_proxy=True)
        # 调度第一个请求
        self.queue.add(weixin_request)

    def parse_index(self, response):
        """
        解析索引页
        :params response: 响应
        :return: 新的响应
        """
        doc = pq(response.text)
        items = doc('.news-box .news-list li .txt-box h3 a').items()
        for item in items:
            url = item.attr('href')
            weixin_request = WeixinRequest(url=url, callback=self.parse_detail)
            yield weixin_request
        next = doc('#sogou_next').attr('href')
        if next:
            url = 'https://weixin.sogou.com/weixin' + str(next)
            weixin_request = WeixinRequest(url=url, callback=self.parse_index, need_proxy=True)
            yield weixin_request
            
    def parse_detail(self, response):
        """
        解析详情页
        :param response: 响应
        :return: 微信公众号文章
        """
        doc = pq(response.text)
        data = {
            'title':doc('#activity-name').text(),
            'content':doc('.rich_media_content').text(),
            'date':doc('#js_modify_tim').text(),
            'nickname':doc('#js_name').text(),
            'wechat':doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()
        }
        yield data

    def reuqest(self, weixin_request):
        """
        执行请求
        :param weixin_request: 请求
        :return : 响应
        """
        try:
            if weixin_request.need_proxy:
                proxy = self.get_proxy()
                if proxy:
                    proxies = {
                        'http':'http://' + proxy,
                        'https':'https://' + proxy
                    }
                    return self.session.send(weixin_request.prepare(), timeout=weixin_request.timeout, allow_redirects=False, proxies=proxies)
            return self.session.send(weixin_request.prepare(), timeout=weixin_request.timeout, allow_redirects=False)
        except Exception as e:
            print(e.args)     
            return False
    
    def error(self, weixin_request):
        """
        错误处理
        :param weixin_request: 请求
        :return :
        """
        weixin_request.fail_time = weixin_request.fail_time + 1
        print('Request Failed', weixin_request.fail_time, 'Times', weixin_request.url)
        if weixin_request.fail_time < MAX_FAILED_TIME:
            self.queue.add(weixin_request)
    
    def schedule(self):
        """
        调度请求
        :return :
        """
        while not self.queue.empty():
            weixin_request = self.queue.pop()
            callback = weixin_request.callback
            print('Schedule', weixin_request.url)
            response = self.reuqest(weixin_request)
            print(response.text)
            if response and response.status_code in VALID_STATUSES:
                results = list(callback(response))
                if results:
                    for result in results:
                        print('New Result', type(result))
                        if isinstance(result, WeixinRequest):
                            self.queue.add(result)
                        if isinstance(result, dict):
                            self.mysql.insert('articles', result)
                else:
                    self.error(weixin_request)
            else:
                self.error(weixin_request)

    def run(self):
        """
        运行入口
        """
        self.start()
        self.schedule()





if __name__ == '__main__':
    spider = Spider()
    spider.run()