# -*- coding:utf-8 -*-

# redis地址
REDIS_HOST = 'localhost'
# redis端口
REDIS_PORT = '6379'
# redis密码
REDIS_PASSWORD = ''
# 代理池数据库key
REDIS_KEY = 'proxies'

# 最大分值
MAX_SCORE = 50
# 最小分值
MIN_SCORE = 0
# 初始分值
INITIAL_SCORE = 10

# 代理池数量限制
PROXIES_THRESHOLD = 1000

# 测试代理是否有效的网址
TEST_URL = 'http://httpbin.org/get'

# 测试步长
BATCH_SIZE = 30