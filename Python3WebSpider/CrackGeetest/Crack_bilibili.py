# -*- coding:utf-8 -*-

import time
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import requests
import sys


class Crack_bilibili():
    def __init__(self):
        self.url = 'https://passport.bilibili.com/login'
        # 测试是否登陆成功
        self.test_url = 'https://account.bilibili.com/account/home'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.email = '188195701'
        self.password = '08015417Qiu'

    def __del__(self):
        self.browser.close()

    def open(self):
        """
        打开网页输入用户名密码
        """
        self.browser.get(self.url)
        email = self.wait.until(EC.presence_of_element_located((By.ID, 'login-username')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'login-passwd')))
        # time.sleep(3)
        # 输入账号
        email.send_keys(self.email)
        # time.sleep(4)
        # 输入密码
        password.send_keys(self.password)
        time.sleep(2)
    
    def get_image_info(self, xpath):
        """
        获取验证码图片url，位置信息
        :params xpath:xpath选择器规则
        :return: 验证码图片url，位置信息
        """
        # 定义获取验证码图片url，位置信息的正则
        link = re.compile(r'background-image: url\("(.*?)"\); background-position: (.*?)px (.*?)px;')
        # 选中标签
        elements = self.browser.find_elements_by_xpath(xpath)
        # print(elements)
        # 存储位置坐标信息
        location = list()
        for element in elements:
            # 获取标签style属性值
            style = element.get_attribute("style")
            # 匹配正则
            groups = link.search(style)
            # 获取url
            image_url = groups[1]
            # 获取x轴位置
            x_pos = groups[2]
            # 获取y轴位置
            y_pos = groups[3]
            # 添加到列表
            location.append((int(x_pos), int(y_pos)))
            # print(len(location))
        return image_url, location

    def mosaic_image(self, image_url, location):
        """
        拼接图片
        :params: image_url:验证码图片url
        :params: location:验证码图片坐标信息
        :return: 拼接后的图片
        """
        # 获取图片
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
        }
        resq = requests.get(image_url, headers=headers)
        file = BytesIO(resq.content)
        # 调用Image拼接图片
        img = Image.open(file)
        # img.show()
        image_upper_lst = []
        image_down_lst = []
        for pos in location:
            if pos[1] == 0:
                # y值==0的图片属于上半部分，高度58
                image_upper_lst.append(img.crop((abs(pos[0]), 0, abs(pos[0]) + 10, 58)))
            else:
                # y值==58的图片属于下半部分
                image_down_lst.append(img.crop((abs(pos[0]), 58, abs(pos[0]) + 10, img.height)))

        # 初始化偏移量为0
        x_offset = 0
        # 新建一个图片，new()第一个参数是颜色模式，第二个是图片尺寸
        new_img = Image.new("RGB", (260, img.height))

        # 拼接第一行
        for img in image_upper_lst:
            # past()方法进行粘贴，第一个参数是被粘对象，第二个是粘贴位置
            new_img.paste(img, (x_offset, 58))
            # 偏移量对应增加移动到下一个图片位置,img.width表示图片宽度
            x_offset += img.width

        # 拼接第二行
        x_offset = 0
        for img in image_down_lst:
            new_img.paste(img, (x_offset, 0))
            x_offset += img.width

        # new_img.show()
        return new_img
    
    def get_distance(self, cut_image, full_image):
        """
        获取缺口偏移量
        :param cut_image: 带缺口图片
        :param full_image: 完整图片
        :return:缺口偏移量
        """
        # 滑块的初始位置
        left = 60
        # 遍历像素点横坐标
        for i in range(left, full_image.size[0]):
            # 遍历像素点纵坐标
            for j in range(full_image.size[1]):
                # 如果不是相同像素,返回此时横轴坐标,即滑块需要移动的距离
                if not self.is_pixel_equal(cut_image, full_image, i, j):
                    left = i
                    return left
        return left
    
    def is_pixel_equal(self, cut_image, full_image, x, y):
        """
        判断两个像素是否相同
        :param cut_image: 带缺口图片
        :param full_image: 完整图片
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 获取缺口图片的像素点(按照RGB格式)
        pixel1 = cut_image.load()[x, y]
        # 获取完整图片的像素点(按照RGB格式)
        pixel2 = full_image.load()[x, y]
        # 设置一个判定值，像素值之差超过判定值则认为该像素不相同
        threshold = 60
        # 判断像素的各个颜色之差，abs()用于取绝对值
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            # 如果差值在判断值之内，返回是相同像素
            return True
        else:
            # 如果差值在判断值之外，返回不是相同像素
            return False
    
    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 创建存放轨迹信息的列表
        track = []
        distance_half = distance 
        # distance_half = distance * 1/2
        # print(distance_half)
        for i in range(1):
            # 当前位移
            current = 0
            # 减速阈值
            mid = distance_half * 4 / 5
            # 计算间隔
            t = 0.1
            # 初速度
            v = 0
            # 当尚未移动到终点时
            while current < distance_half:
                # 如果处于加速阶段
                if current < mid:
                    # 加速度为正2
                    a = 3
                # 如果处于减速阶段
                else:
                    # 加速度为负2
                    a = -2
                # 初速度v0
                v0 = v
                # 当前速度v = v0 + at
                v = v0 + a * t
                # 移动距离x = v0t + 1/2 * a * t^2
                move = v0 * t + 1 / 2 * a * t * t
                # 当前位移
                current += move
                # print(move)
                # 加入轨迹
                track.append(round(move))
            # print(track)
        return track
    
    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'gt_slider_knob')))
        return slider

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        """
        # 使用click_and_hold()方法悬停在滑块上，perform()方法用于执行
        ActionChains(self.browser).click_and_hold(slider).perform()
        for x in track:
            # 使用move_by_offset()方法拖动滑块，perform()方法用于执行
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        # fake_track = [2,3,3,2,2,3,3,2,2,3,3,2,2,3,3,2]
        # for x in fake_track:
        #     ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        # for x in fake_track:
        #     ActionChains(self.browser).move_by_offset(xoffset=-x, yoffset=0).perform()

        # 模拟人类对准时间
        time.sleep(0.5)
        # 释放滑块
        ActionChains(self.browser).release().perform()
    
    def crack(self):
        """
        验证码验证
        :return :验证结果
        """
        # 获取带缺口的验证码图片
        cut_image_url, cut_image_location = self.get_image_info('//div[@class="gt_cut_bg_slice"]')
        # 获取完整的验证码图片
        full_image_url, full_image_location = self.get_image_info('//div[@class="gt_cut_fullbg_slice"]')
        # print(cut_image_url, full_image_url)

        # 根据坐标拼接图片
        cut_image = self.mosaic_image(cut_image_url, cut_image_location)
        full_image = self.mosaic_image(full_image_url, full_image_location)

        # 保存图片方便查看
        cut_image.save(sys.path[0] + '/cut_img.jpg')
        full_image.save(sys.path[0] + '/full_img.jpg')

        # 获取缺口位置
        gap = self.get_distance(cut_image, full_image)
        print('缺口位置', gap)
        # 减去缺口位移
        gap -= 5

        # 获取移动轨迹
        track = self.get_track(gap)
        # print('滑动轨迹', track)

        # 获取滑块标签
        slider = self.get_slider()
        # print(slider)

        # 拖动滑块
        self.move_to_gap(slider, track)

        try:
            # 判断是否验证通过
            success = self.wait.until(
                EC.text_to_be_present_in_element((By.XPATH, '//span[@class="gt_info_type"]'), '验证通过:'))
        except:
            success = False

        return success

    def refresh(self):
        """
        刷新验证码
        """
        print('刷新验证码')
        slider = self.get_slider()
        ActionChains(self.browser).move_to_element(slider).perform()
        # 获取验证码刷新按钮
        again = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'gt_refresh_button')))
        # 点击刷新
        again.click()

    def login(self):
        """
        点击登录
        """
        submit = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-login')))
        submit.click()
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="nav-name"]')))
            print('登陆成功!')
        except:
            print('用户名或密码错误！')

    def run(self):
        """
        运行
        """
        # 输入用户名密码
        self.open()
        # 验证码验证,不通过尝试刷新直至通过为止
        while not self.crack():
            # self.refresh()
            pass
        # 验证码验证通过，登陆
        self.login()
        
if __name__ == '__main__':
    crack = Crack_bilibili()
    crack.run()
