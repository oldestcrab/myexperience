# -*- coding:utf-8 -*-

import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import requests
import sys


class TestCookies():
    def __init__(self):
        self.url = 'http://www.igenebio.com/oa/?r=user/default/login'
        # 测试是否登陆成功
        self.test_url = 'http://www.igenebio.com/oa/?r=main/default/index'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.email = '邱海伦'
        self.password = '08015417Qiu'

    def __del__(self):
        self.browser.close()

    def open(self):
        """
        打开网页输入用户名密码
        """
        self.browser.get(self.url)
        email = self.wait.until(EC.presence_of_element_located((By.ID, 'account')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'password')))
        # time.sleep(3)
        # 输入账号
        email.send_keys(self.email)
        # time.sleep(4)
        # 输入密码
        password.send_keys(self.password)
        time.sleep(2)
    
    def login(self):
        """
        点击登录
        """
        # 点击登录
        submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@name="loginsubmit"]')))
        submit.click()


    def cookies(self):
        """
        cookies
        """
        cookies = self.browser.get_cookies()
        print(cookies)
        dict = {}
        for cookie in cookies:
           print(cookie['name'])
        for cookie in cookies:
            dict[cookie['name']] = cookie['value']
        print(dict)
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
        }
        rsp1 = requests.get(self.test_url, headers=headers, cookies=dict)
        print(rsp1.url, rsp1.status_code)
        with open(sys.path[0] + '/1.html', 'w', encoding='utf-8') as f:
            f.write(rsp1.text)
        rsp2 = requests.get(self.test_url, headers=headers)
        print(rsp2.url, rsp2.status_code)
        with open(sys.path[0] + '/2.html', 'w', encoding='utf-8') as f:
            f.write(rsp2.text)
        rsp3 = requests.get(self.test_url, headers=headers, allow_redirects=False)
        with open(sys.path[0] + '/3.html', 'w', encoding='utf-8') as f:
            f.write(rsp3.text)
        print(rsp3.url, rsp3.status_code)

    def run(self):
        """
        运行
        """
        # 输入用户名密码
        self.open()
        # 点击登陆
        self.login()
        # 获取cookies
        self.cookies()    

if __name__ == '__main__':
    test = TestCookies()
    test.run()
