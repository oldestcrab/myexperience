# -*- coding:utf-8 -*-
import config
import time
import os
import sys
import random
import requests
from lxml import etree
import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

def browser_page_login(browser):
    """
    用于网站登录
    :param browser:浏览器对象
    """


    # 设置等待时长
    wait = WebDriverWait(browser, 10)
    url_login = 'https://www.tumblr.com/login'
    try:
        browser.get(url_login)
        # 等待获取下一步按钮
        submit_next = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@class="signup_determine_btn active"]')))
        # input_username : 用户名输入框
        input_username = browser.find_element_by_xpath('//input[@name="determine_email"]')
        input_username.clear()
        input_username.send_keys(config.tumblr_user_likes_username)
        # 点击下一步
        submit_next.click()
        # submit_use_password : 使用密码登录按钮|点击使用密码登录
        submit_use_password = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="signup_view magiclink active"]/div[@class="magiclink_password_container chrome"]')))
        submit_use_password.click()
        # submit_login 登录按钮
        submit_login = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@class="signup_login_btn active"]')))
        # 密码输入框
        input_password = browser.find_element_by_xpath('//div[@class="form_row form_row_password"]/input[@type="password"]')
        # input_password.clear()
        input_password.send_keys(config.tumblr_user_likes_password)
        # 点击登录
        submit_login.click()
        # print(browser.page_source)
        
        # 返回浏览器对象
        return browser

    except TimeoutException:
        print('login page loading time out!')
        browser_page_login(browser)

def browser_page_likes(page, browser):
    """
    获取用户喜欢页面
    :param page:当前页数
    :param browser:浏览器对象
    """
    # https://www.tumblr.com/likes/page/1
    url_likes = 'https://www.tumblr.com/likes/page/' + str(page)
    print(url_likes)
    browser.get(url_likes)
    browser.implicitly_wait(5)

    # 返回喜欢页源码
    return browser.page_source

def get_index_page(browser_next):
    """
    爬取页面
    :param browser_next:浏览器对象
    """
    '''
    # dir_judge_start_page : 保存上次最后爬取的页数
    dir_judge_start_page = sys.path[0] + '/judge_share_start_page.txt'
    if not os.path.exists(dir_judge_start_page):
        with open(dir_judge_start_page, 'w', encoding = 'utf-8') as f:
            f.write('1')
        print('创建文件：' + dir_judge_start_page + ',并赋值page_next_start = 1')

    # 如果是新爬取的，True，则起始页为1，否则读取上次爬取时的页数，并作为起始页
    # config.tumblr_share_judge_new : True|False
    if config.tumblr_share_judge_new:
        page_start = 1
    else:
        with open(dir_judge_start_page, 'r', encoding = 'utf-8') as f:
            page_start = int(f.readline())
    '''

    # config.tumblr_likes_username : 爬取用户名
    for i in range(config.tumblr_user_likes_page_start, config.tumblr_user_likes_page_end):
        print('当前爬取页码数：' + str(i))
        # 保存当前爬取页数
        # with open(dir_judge_start_page, 'w', encoding = 'utf-8') as f:
        #     f.write(str(i))

        # 获取浏览器对象返回的网页源码
        response_index = browser_page_likes(i, browser_next)
        html_iframe = etree.HTML(response_index)

        try:
            # 获取视频源码
            list_video_source = html_iframe.xpath('//div[@class="post_content_inner clearfix"]')
            
        except:
            print('get list_video_source error!')
            list_video_source = []
            
        # 确定能够获取
        if list_video_source:
            for i in list_video_source:
                get_page_video(i)

def get_page_video(content_lxml):
    """
    爬取用户自己发布的视频页面
    :param content_lxml:通过xpath获取的内容
    """
    # 获取框架页面链接列表
    list_url_iframe = content_lxml.xpath('.//video/source/@src')

    # 视频保存名字
    list_name_1 = content_lxml.xpath('.//div[@class="post_body"]/p/text()')
    list_name_2 = content_lxml.xpath('.//div[@class="reblog-content"]/p/text()')


    # 先确认是否能获取框架页面链接列表，能则继续下一步
    if list_url_iframe:
        # 获取视频页面链接
        url_iframe = list_url_iframe[0]
        # print('url_iframe：' + url_iframe)

        with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
                list_user_agents = f.readlines()
                user_agent = random.choice(list_user_agents).strip()
        headers = {'user-agent':user_agent}

        # 判断是否还需要访问视频框架页面
        pattren_url_video = re.compile(r'.*(\.mp4)')
        judge_url_video = pattren_url_video.search(url_iframe)

        # 如果匹配不到.mp4,则需要访问框架页面
        if judge_url_video is None:
            # 访问该链接，返回的url即为视频真正链接
            try:
                response_video_page = requests.get(url_iframe, headers = headers)
            except:
                print('load video page error:' + url_iframe)
                response_video_page = requests.get(url_iframe, headers = headers)
        
            # 获取视频真正url
            url_video = response_video_page.url
        else:
            url_video = url_iframe

        # 保存视频url链接
        # with open(sys.path[0] + '/list_url_video.txt', 'a', encoding = 'utf-8') as f:
            # f.write(url_video + '\n')

        # print('url_video:\t' + url_video)

        # 确认视频保存名字：原用户发布内容下文字|转载用户转载内文字|视频链接取最后
        if list_name_1 and len(list_name_1)<3:
            name_video = ''.join(list_name_1) + '.mp4'
        elif list_name_2 and len(list_name_2)<3:
            name_video = ''.join(list_name_2) + '.mp4'
        else:
        #     pattren_name_video = re.compile(r'.*\/(.*)?', re.I)
        #     name_video = pattren_name_video.search(url_video).group(1)
            name_video = ''
        # pattren_name_video = re.compile(r'.*\/(.*)?', re.I)
        # name_video = pattren_name_video.search(url_video).group(1)
        if name_video:
            name_video = name_video.replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','').replace('\\n','').strip()
            print(name_video)

            # 获取视频内容
            try:
                response_video = requests.get(url_video, headers = headers)
                # response_video.encoding = 'utf-8'
                # time.sleep(1)
            except:
                print('get video page error:' + url_video)
                response_video = ''
            # 如果能够获取视频内容，则保存内容
            if response_video:
                save_content_video(name_video, response_video.content)

def save_content_video(name_video, content_video):
    """
    保存视频
    :param name_video:视频保存名字
    :param content_video:视频链接
    """   
    dir_save_vedio = 'd:/tumblr_user_likes_spider_result/' + config.tumblr_user_likes_username_dir + '/'
    if not os.path.exists(dir_save_vedio):
        os.makedirs(dir_save_vedio)
    try:
        # 保存视频
        with open(dir_save_vedio + name_video, 'wb') as f:
            f.write(content_video)  
    except OSError as e:
        print('视频保存失败：' + name_video +'\n{e}'.format(e = e))


def main():
    print('tumblr_likes_spider爬取开始！')
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

    # 构造一个 WebDriver 对象，调用phantomjs
    browser = webdriver.Chrome()
    browser_next = browser_page_login(browser)
    # config.tumblr_likes_page : 爬取总页数    
    get_index_page(browser_next)

    browser.close()
    print('tumblr_likes_spider爬取结束！')
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

if __name__ == '__main__':
    main()