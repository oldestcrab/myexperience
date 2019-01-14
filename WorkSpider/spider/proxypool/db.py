# -*- coding:utf-8 -*-

import redis
from setting import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_KEY
from setting import MAX_SCORE, MIN_SCORE, INITIAL_SCORE, PROXIES_THRESHOLD
from random import choice
import re
from error import PoolEmptyError

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
        添加一个代理到数据库，默认初始分值10分
        :params proxy: 代理
        :params score: 代理分数
        """
        if re.match(r'\d+\.\d+\.\d+\.\d+\:\d+', proxy):
            if self.db.zcard(REDIS_KEY) < PROXIES_THRESHOLD:
                if not self.score(proxy):
                    self.db.zadd(REDIS_KEY, {proxy:score})
            else:
                print('代理池代理数量已满'+str(PROXIES_THRESHOLD)+'，不再添加代理！')
        else:
            print(proxy, '代理不符合规则，丢弃！')

    def max(self, proxy):
        """
        代理分数更改最高值
        :params proxy: 代理
        """
        self.db.zadd(REDIS_KEY, {proxy:MAX_SCORE})
        print(proxy, '可用，分数设置为最高值，当前分数为: ', self.score(proxy))

    def decrease(self, proxy):
        """
        代理分数-1,如果代理分数为0，则删除代理
        :params proxy: 代理
        """
        if self.score(proxy) and self.score(proxy) > MIN_SCORE:
            self.db.zincrby(REDIS_KEY, -1, proxy)
            print(proxy, '不可用，分数-1，当前分数为: ', self.score(proxy))
        else:
            print(proxy, '分数为0，删除')
            self.db.zrem(REDIS_KEY, proxy)

    def all(self):
        """
        返回当前代理池所有代理
        :return: 返回当前代理池所有代理
        """
        return self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)

    def count(self):
        """
        返回当前代理池代理总数
        :return: 返回当前代理池代理总数
        """
        return self.db.zcard(REDIS_KEY)

    def random(self):
        """
        随机返回一个当前分值最高的代理,首先尝试获取分值最高的代理，如果不存在，则按照排名获取，负责抛出异常
        :return: 随机代理
        """
        proxy_list = self.db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(proxy_list):
            return choice(proxy_list)
        else:
            proxy_list = self.db.zrevrange(REDIS_KEY, 0, 100)
            if len(proxy_list):
                return choice(proxy_list)
            else:
                raise PoolEmptyError

    def batch(self, start, stop):
        """
        批量获取代理
        :return: 代理列表
        """
        return self.db.zrevrange(REDIS_KEY, start, stop)

def main():
    a = ReadisClient()
    # print(a.exists('222.222.222.222:22222'))
    # a.decrease('222.222.222.222:22222')
    # # b = a.all()
    # b = a.batch()
    # print(b)
    print(a.batch(1, 5))

if __name__ == '__main__':
    main()