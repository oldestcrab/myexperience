# -*- coding:utf-8 -*-
from db import ReadisClient
import re


def scan():
    """
    导入代理
    """
    proxies_dir = input('请输入要导入的代理的绝对地址: ')

    # 连接redis
    db = ReadisClient()
    print(db.exists('1.1.1.1:1'))
    print(db.exists('2.2.2.2:2'))
    print(db.exists('3.3.3.3:3'))
    # 获取要导入的代理
    try:
        with open(proxies_dir, 'r', encoding = 'utf-8') as f:
            proxies_list = f.readlines()
    except:
        print('文件不存在！')

    # 导入代理
    try:
        print('开始导入代理！')
        for proxy in proxies_list:
            try:
                db.add(proxy.strip())
                print(proxy.strip(),'导入成功!' )
            except:
                print(proxy.strip(),'导入失败！')
    except:
        pass

    print('当前代理池总代理数量为：', db.count())

def main():
    scan()

if __name__ == '__main__':
    main()