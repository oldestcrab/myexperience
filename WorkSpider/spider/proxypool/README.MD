### proxypool 说明文档

#### 说明
代理池共分为4个模块：存储模块、获取模块、检测模块、接口模块

- 存储模块  
    负责存储获取模块爬取下来的代理，使用redis的sorted set进行存储。代理不重复，并通过分数标识数据库中的代理状态。

- 获取模块  
    负责定时从各大代理网站上爬取高匿代理，代理池设置代理总数为500，超过该数量将不会继续获取代理。新获取的代理分数标识为10。

- 检测模块  
    负责定时检测数据库中的代理，通过分数标识数据库中的代理状态。访问[httpbin](http://httpbin.org/get),查看返回的IP是否为该代理。当代理可用时，分数设置为50，当代理不可用时分数减1，如果分数为0，则移除该代理。

- 接口模块  
    负责通过Web API提供对外服务的接口，访问 http://127.0.0.1:5555/random 即可随机获得数据库中所有分数为50的代理中的一个。

#### 使用说明

- 启动代理池  
```python
# 切换python运行环境
source /home/bmnars/spider_porject/bmnars_venv/bin/activate
# 启动代理池
nohup python /home/bmnars/spider_porject/proxypool/run_proxypool.py &
```

- 获取代理  
当代理池启动时，  
访问 http://127.0.0.1:5555/random 即可获得一个当前可用的代理。  
访问 http://127.0.0.1:5555/count 可查看当前代理池的代理总数。  

- 示例  
```python
import requests
import redis

def proxy():
    """
    :return: 返回一个随机选择的proxy
    """
    try:
        response = requests.get('http://127.0.0.1:5555/random')
        return response.text
    except:
        db = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
        result = db.zrangebyscore('proxies', 50, 50)
        if len(result):
            return random.choice(result)
        else:
            result = db.zrangebyscore('proxies', 0, 50)
            if len(result):
                return random.choice(result)

```