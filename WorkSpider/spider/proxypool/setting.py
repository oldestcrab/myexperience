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
PROXIES_THRESHOLD = 500

# 测试代理是否有效的网址
TEST_URL = 'http://httpbin.org/get'

# 测试步长
BATCH_SIZE = 30

# 获取器开关
GETTER_ENABLED = True

# 测试器开关
TESTER_ENABLED = True

# API开关
API_ENABLED = True

# API 配置
API_HOST = '0.0.0.0'
API_PORT = '5555'

# 代理池获取周期
GETTER_CYCLE = 3600

# 代理池测试周期
TESTER_CYCLE = 60