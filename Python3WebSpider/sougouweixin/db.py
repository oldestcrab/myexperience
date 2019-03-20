# -*- coding:utf-8 -*-

from redis import StrictRedis
from settings import *
from request import WeixinRequest
from pickle import dumps, loads

class RedisQueue():
    def __init__(self):
        """
        初始化redis
        """
        self.db = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, )

    def add(self, request):
        """
        向队列添加序列化后的Request
        :param reqeust: 请求对象
        :return: 添加结果
        """
        if isinstance(request, WeixinRequest):
            return self.db.rpush(REDIS_KEY, dumps(request))
        return False

    def pop(self):
        """
        取出下一个request并反序列化
        :return: request or None
        """
        if self.db.llen(REDIS_KEY):
            return loads(self.db.lpop(REDIS_KEY))
        else:
            return False

    def clear(self):
        """
        删除redis key
        """
        self.db.delete(REDIS_KEY)

    def empty(self):
        """
        判断队列是否为空
        """
        return self.db.llen(REDIS_KEY) == 0

if __name__ == '__main__':
    db = RedisQueue()
    url = 'http://www.baidu.com'
    request = WeixinRequest(url=url, callback='hello', need_proxy=True)
    print(request)
    print(type(request))
    db.add(request)
    a = db.pop()
    print(a)
    print(a.callback, a.need_proxy)
    
    