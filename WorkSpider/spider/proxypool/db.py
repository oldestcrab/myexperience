# -*- coding:utf-8 -*-

import redis
from setting import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_KEY
from setting import MAX_SCORE, MIN_SCORE, INITIAL_SCORE, PROXIES_THRESHOLD
from random import choice
import re

class ReadisClient():
    def __init__(self, host = REDIS_HOST, port = REDIS_PORT, password = REDIS_PASSWORD):
        """
        初始化
        :params host: redis地址
        :params port: redis端口
        :params password: redis密码
        """
        super(ReadisClient, self).__init__()
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)

    def exists(self, proxy):
        """
        查询代理是否存在
        :params proxy: 代理
        :return: 判断结果
        """
        return not self.score(proxy) == None

    def score(self, proxy):
        """
        查询代理分数
        :params proxy: 代理
        :return: 代理分数
        """
        return self.db.zscore(REDIS_KEY, proxy)

    def add(self, proxy, score=INITIAL_SCORE):
        """
        添加一个代理到数据库
        :params proxy: 代理
        :params score: 代理分数
        """
        if re.match(r'\d+\.\d+\.\d+\.\d+\:\d+', proxy):
            if self.db.zcard(REDIS_KEY) > PROXIES_THRESHOLD:
                self.db.zadd(REDIS_KEY, {proxy:score})
        else:
            print(proxy, '代理不符合规则，丢弃！')

    def max(self, proxy):
        """
        代理分数更改为50
        :params proxy: 代理
        """
        if self.score(proxy):
            self.db.zadd(REDIS_KEY, {proxy:MAX_SCORE})

    def decrease(self, proxy):
        """
        代理分数-1,如果代理分数为0，则删除代理
        :params proxy: 代理
        """
        if self.score(proxy):
            self.db.zincrby(REDIS_KEY, -1, proxy)
            print(proxy, '不可用，分数-1，当前分数为: ', self.score(proxy))
        else:
            print(proxy, '分数为0，删除')
            self.db.zrem(REDIS_KEY, proxy)

    def all(self):
        """
        :return: 返回当前代理池所有代理
        """
        return self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)

    def count(self):
        """
        :return: 返回当前代理池代理总数
        """
        return self.db.zcard(REDIS_KEY)

    def random(self):
        """
        :return: 随机返回一个当前分数为50的代理
        """
        proxy_list = self.db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        return choice(proxy_list)

def main():

    a = ReadisClient()
    # print(a.exists('222.222.222.222:22222'))
    a.decrease('222.222.222.222:22222')
    # b = a.all()
    # b = a.score('1')
    # print(b)

if __name__ == '__main__':
    main()