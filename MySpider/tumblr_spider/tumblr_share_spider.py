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
        input_username.send_keys('18819425701@163.com')
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
        input_password.send_keys('08015417Qiu')
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

    # 返回喜欢页源码
    return browser.page_source

def get_index_page(page_end, browser_next):
    """
    爬取页面
    :param page_end:页码数
    """
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


    # config.tumblr_likes_username : 爬取用户名
    for i in range(page_start, page_end):
        # 保存当前爬取页数
        print('当前爬取页码数：' + str(i))
        with open(dir_judge_start_page, 'w', encoding = 'utf-8') as f:
            f.write(str(i))


        response_index = browser_page_likes(i, browser_next)
        # print(type(response_index))
        # with open(sys.path[0] + '/1.html', 'w', encoding = 'utf-8') as f:
        #     f.write(response_index)
        html_iframe = etree.HTML(response_index)

        try:
            # list_video_source_1 = html_iframe.xpath('//div[@class="post_media"]//video/source')
            # 获取用户自己发布的视频
            list_video_source_1 = html_iframe.xpath('//div[@class="post_content_inner clearfix"]')
            
        except:
            print('get list_video_source_1 error!')
            list_video_source_1 = []

        # try:
            # list_video_source_2 = html_iframe.xpath('//div[@class="reblog-list"]')
            # list_video_source_2 = html_iframe.xpath('//div[@class="reblog-list"]')
            # 
        # except:
            # print('get list_video_source_2 error!')
            # list_video_source_2 = []
        # print( list_video_source_1)
        if list_video_source_1:
            for i in list_video_source_1:
                get_page_video_post(i)
        # print(list_video_source_2)
        # if list_video_source_2:
            # for i in list_video_source_2:
                # get_page_video_reblog(i)
# 
def get_page_video_post(content_lxml):
    """
    爬取用户自己发布的视频页面
    :param content_lxml:通过xpath获取的内容
    """
    # 获取框架页面链接列表
    # url_iframe : https://everythingfox.tumblr.com/video_file/t:TQ_U5i4OlLu9TxRYtxAdzg/179493447941/tumblr_ph9x0xr04g1vmobp0/480
    list_url_iframe = content_lxml.xpath('./div[@class="post_media"]//video/source/@src')
    
    # 视频保存名字
    list_name_1 = content_lxml.xpath('./div[@class="post_body"]//p/text()')
    list_name_2 = content_lxml.xpath('./div[@class = "reblog-list-item contributed-content"]//p/text()')

    # 先确认是否能获取框架页面链接列表，能则继续下一步
    if list_url_iframe:
        # 获取框架页面链接
        url_iframe = list_url_iframe[0]
        # print('url_iframe：' + url_iframe)

        # 访问该链接，返回的url即为视频真正链接
        with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
            list_user_agents = f.readlines()
            user_agent = random.choice(list_user_agents).strip()
        headers = {'user-agent':user_agent}
        try:
            response_video_page = requests.get(url_iframe, headers = headers)
        except:
            print('get video page error:' + url_iframe)
            response_video_page = ''
        
        # 确认是否访问成功
        if response_video_page:
            # 获取视频真正url
            # url_video : https://vf.media.tumblr.com/tumblr_ph9x0xr04g1vmobp0_480.mp4
            url_video = response_video_page.url
            print('url_video:' + url_video)

            # 确认视频保存名字：原用户发布内容下文字|转载用户转载内文字|视频链接取最后
            if list_name_1 and len(list_name_1)<3:
                name_video = ''.join(list_name_1) + '.mp4'
            elif list_name_2 and len(list_name_2)<3:
                name_video = ''.join(list_name_2) + '.mp4'
            else:
                pattren_name_video = re.compile(r'.*\/(.*)?', re.I)
                name_video = pattren_name_video.search(url_video).group(1) 
            print(name_video)
            
            # 获取视频内容
            try:
                response_video = requests.get(url_video, headers = headers)
                response_video.encoding = 'utf-8'
                # time.sleep(1)
            except:
                print('get video page error:' + url_video)
                response_video = ''

            # 如果能够获取视频内容，则保存内容
            if response_video:
                save_content_video(name_video, response_video.content)

def get_page_video_reblog(content_lxml):
    """
    爬取视频页面
    :param content_lxml:通过xpath获取的内容
    """
    # url_iframe : https://everythingfox.tumblr.com/video_file/t:TQ_U5i4OlLu9TxRYtxAdzg/179493447941/tumblr_ph9x0xr04g1vmobp0/480
    list_url_video = content_lxml.xpath('./div[@class = "post-reblog-trail-item original-reblog-content"]/div[@class="post-reblog-content"]//source/@src')
    # name_video = ''.join(content_lxml.xpath('./div[@class="post-reblog-content"]//p/text()')) 
    list_name_1 = content_lxml.xpath('./div[@class = "post-reblog-trail-item original-reblog-content"]/div[@class="post-reblog-content"]//p/text()')
    list_name_2 = content_lxml.xpath('./div[@class = "post-reblog-trail-item"]//p/text()')
    if list_url_video:
        url_video = list_url_video[0]
        if list_name_1 and len(list_name_1)<3:
            name_video = ''.join(list_name_1) + '.mp4'
        elif list_name_2 and len(list_name_2)<3:
            name_video = ''.join(list_name_2) + '.mp4'
        else:
            pattren_name_video = re.compile(r'.*\/(.*)?', re.I)
            name_video = pattren_name_video.search(url_video).group(1) 

        print(name_video)
        print(url_video)
        print(type(name_video))
        with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
            list_user_agents = f.readlines()
            user_agent = random.choice(list_user_agents).strip()
        headers = {'user-agent':user_agent}

        try:
            response_video = requests.get(url_video, headers = headers)
            response_video.encoding = 'utf-8'
            time.sleep(1)
        except:
            print('get video page error:' + url_video)
            response_video = requests.get('https://www.baidu.com', headers = headers)

        save_content_video(name_video, response_video.content)

def save_content_video(name_video, content_video):
    """
    保存视频
    :param name_video:视频保存名字
    :param content_video:视频链接
    """   
    dir_save_vedio = sys.path[0] + '/'  + config.tumblr_likes_username + '_likes_result/'
    if not os.path.exists(dir_save_vedio):
        os.makedirs(dir_save_vedio)
    try:
        # 保存视频
        with open(dir_save_vedio + name_video, 'wb') as f:
            f.write(content_video)  
    except OSError as e:
        print('图片保存失败：' + name_video +'\n{e}'.format(e = e))


def main():
    print('tumblr_likes_spider爬取开始！')
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

    # 构造一个 WebDriver 对象，调用phantomjs
    browser = webdriver.Chrome()
    browser_next = browser_page_login(browser)
    # config.tumblr_likes_page : 爬取总页数    
    get_index_page(config.tumblr_share_page, browser_next)

    browser.close()
    print('tumblr_likes_spider爬取结束！')
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

if __name__ == '__main__':
    main()