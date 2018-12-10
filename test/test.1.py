import requests
import json
import sys
import random
import time

print('程序开始！  ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
url = 'http://httpbin.org/get'
with open(sys.path[0] + '/user-agents.txt', 'r' , encoding = 'utf-8') as f:
    list_user_agent = f.readlines()
user_agent = random.choice(list_user_agent).strip()
# print(user_agent)
headers = {'user-agent':user_agent}
# print(headers)
# proxy = '125.46.0.62:53281'
ip_proxy = '	219.246.90.204	'
port_proxy = '	3128'
proxy = ip_proxy.strip() + ':' + port_proxy.strip()
# print(proxy)
proxies = {
    'http':'http://' + proxy ,
    'https':'https://' + proxy 
}
try:
    response = requests.get(url, headers = headers, proxies = proxies)
    response_test_code = response_test.status_code
    # response = requests.get(url, headers = headers)
except:
    print('err')
    response = ''
    response_test_code = ''
if response and response_test_code == 200:
    try:
        dict_response = json.loads(response.content)
        ip_response = dict_response['origin']
    except:
        ip_response = ''
    # print(type(ip_response))
    if ip_response == ip_proxy:
        with open(sys.path[0] + '/ip_response.txt', 'a', encoding = 'utf-8') as f:
            f.write(proxy + '\n')
            # print(dict_response['headers']['User-Agent'])
print('程序结束！  ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
