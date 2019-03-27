from settings import *
from requests import Request
from requests import Session

class WeixinRequest(Request):
    def __init__(self, url, callback, method='GET', headers=None, need_proxy=False, fail_time=0, timeout=TIMEOUT):
        super(WeixinRequest, self).__init__(method, url, headers)
        # Request.__init__(self, method, url, headers)
        self.callback = callback
        self.need_proxy = need_proxy
        self.fail_time = fail_time
        self.timeout = timeout
        


if __name__ == '__main__':
    session = Session()
    headers ={
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': 'SUID=28CB5E7D3020910A000000005C6225BE; SUV=1549936064592885; pgv_pvi=8287179776; ABTEST=0|1552986153|v1; weixinIndexVisited=1; JSESSIONID=aaa7g4gaMDO77hr8j15Mw; PHPSESSID=fs9uhr5cbbo8uiid7cioi8g8c1; IPLOC=SG; SNUID=EA5C2AFF5F5BDB57E1A7B4A85FF0A8E3; sct=48',
    'Host': 'weixin.sogou.com',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    
    }
    
    url = 'https://www.baidu.com'
    weixin = WeixinRequest(url=url, callback='halo')
    # print(weixin)
    # print(weixin.headers)
    # print(type(weixin))
    # print(weixin.url)
    print(session.headers)
    session.headers.update(headers)
    print(session.headers)
    a = session.prepare_request(weixin)
    response = session.send(a, timeout=300)
    # print(response.url)
    print(response.request.headers)

