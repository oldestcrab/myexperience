# -*- coding:utf-8 -*-

import time
import requests
import re
import sys
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CrackHuxiu():
    def __init__(self):
        super(CrackHuxiu, self).__init__()
        self.user = '18827923473'
        self.browser = webdriver.Chrome()
        # 如果不设置按照默认的大小无法模拟点击登陆，登陆按钮不在视野内无法获取
        self.browser.set_window_size(1440, 900)
        self.url = 'https://www.huxiu.com'
        self.wait = WebDriverWait(self.browser, 20)

    def __del__(self):
        """
        关闭浏览器
        """
        self.browser.close()

    def open(self):
        """
        打开网页输入账号
        """
        # 打开网页
        self.browser.get(self.url)
        # 点击登陆按钮
        # login = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@class="js-login"]')))
        login = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'js-login')))
        login.click()
        # 获取账号输入框位置
        user = self.wait.until(EC.presence_of_element_located((By.ID, 'sms_username')))
        user.send_keys(self.user)

    def get_img_info(self, xpath):
        """
        获取验证码图片url，位置信息
        :params xpath: xpath选择器规则
        :return :验证码图片url，位置信息
        """
        time.sleep(2)
        # 定义获取验证码图片url，位置信息的正则
        img_info_pattern = re.compile(r'background-image: url\("(.*?)"\); background-position: (.*?)px (.*?)px;')
        # 定位验证码标签
        elements = self.browser.find_elements(By.XPATH, xpath)
        # print(elements)
        # 存储所有验证码图片坐标位置信息
        location = list()
        for element in elements:
            # 匹配正则
            img_info = img_info_pattern.search(element.get_attribute('style'))
            # 获取url
            url = img_info.group(1)
            # 获取x轴位置
            x_pos = img_info.group(2)
            # 获取y轴位置
            y_pos = img_info.group(3)
            # 添加到列表
            location.append((int(x_pos),int(y_pos)))
        
        return url, location

    def mosaic_img(self, img_url, img_location):
        """
        拼接图片
        :params img_url:图片url
        :params img_location:图片坐标信息
        :return :完整的图片
        """
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
        }
        # 获取图片
        rsp = requests.get(img_url, headers=headers)
        # 读取图片
        file = BytesIO(rsp.content)
        # 调用Image拼接图片
        img = Image.open(file)
        # img.show()
        # 图片上半部分
        img_upper_list = []
        # 图片上半部分
        img_down_list = []
        for pos in img_location:
            if pos[1] == 0:
                # y值为0的图片属于上半部分，高度58
                img_down_list.append(img.crop((abs(pos[0]), 0, abs(pos[0])+10, 58)))
            else:
                # y值为58的图片属于下半部分，高度为图片高度
                img_upper_list.append(img.crop((abs(pos[0]), 58, abs(pos[0])+10, img.height)))

        # 初始化偏移量为0
        x_offset = 0
        # 新建一个图片
        new_img = Image.new('RGB', (260, img.height))

        # 拼接上部分：
        for img in img_upper_list:
            # past()方法进行粘贴，第一个参数是被粘对象，第二个是粘贴位置
            new_img.paste(img, (x_offset, 0))
            # 偏移量对应增加移动到下一个图片位置,img.width表示图片宽度
            x_offset += img.width

        x_offset = 0
        # 拼接下部分：
        for img in img_down_list:
            new_img.paste(img, (x_offset, 58))
            x_offset += img.width

        return new_img

    def get_distance(self, cut_img, full_img):
        """
        获取缺口偏移量
        :params cut_img: 带缺口验证码图片
        :params full_img: 完整验证码图片
        :return :缺口偏移量
        """
        # print(cut_img.width, cut_img.height)
        # 滑块的初始位置
        left = 53
        # 遍历像素点横坐标坐标
        for x in range(left, cut_img.width):
            # 遍历像素点纵坐标坐标
            for y in range(cut_img.height):
                # 如果不是相同的像素，返回此时的横轴坐标，即滑块需要移动的距离
                if not self.is_pixel_equal(cut_img, full_img, x, y):
                    left = x
                    return left
        return left

    def is_pixel_equal(self, cut_img, full_img, x, y):
        """
        判断同一个坐标点像素是否相同
        :params cut_img: 带缺口验证码图片
        :params full_img: 完整验证码图片
        :params x: x轴坐标
        :params y: y轴坐标
        :return :判断结果
        """
        # 获取带缺口图片的像素点（按照RGB格式）
        cut_pixel = cut_img.load()[x,y]
        # print(cut_pixel)
        # 获取w完整图片的像素点（按照RGB格式）
        full_pixel = full_img.load()[x,y]
        # 设置一个判定值，像素值之差大于该值则判定像素不相同
        threshold =  60
        # 判断像素的各个颜色之差
        # print(abs(cut_pixel[1] - full_pixel[1]))
        if abs(cut_pixel[1] - full_pixel[1]) < threshold and  abs(cut_pixel[0] - full_pixel[0]) < threshold and  abs(cut_pixel[2] - full_pixel[2]) < threshold:
            # 如果插值在判断值之内，判定返回的是相同像素
            return True
        else:
            return False 

    def get_track(self, distance):
        """
        获取移动轨迹
        :params distance: 位移距离
        :return :移动轨迹
        """
        # 存储移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0
        # 当还没有移动到终点的时候
        while current < distance:
            # 如果处于加速阶段：
            if current < mid:
                # 加速度为3
                a = 3
            else:
                # 减速阶段，加速度为-2
                a = -2
            # 初速度为0
            v0 = v
            # 当前速度 v = v0 + a*t
            v = v0 + a*t
            # 移动距离 x = v0t + 1/2*a*t*t
            move = v0*t + 1/2*a*t*t
            current += move
            track.append(round(move))
        # print(track)
        return track

    def get_slider(self):
        """
        获取滑块
        :return 滑块
        """
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'gt_slider_knob')))
        return slider

    def move_to_gap(self, slider, track):
        """
        拖动滑块
        :params slider: 滑块
        :parasm track: 移动轨迹
        """
        # 悬停在滑块上
        ActionChains(self.browser).click_and_hold(slider).perform()
        for x in track:
            # 拖动滑块
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        # 模拟人类对准时间
        time.sleep(0.5)
        # 释放滑块
        ActionChains(self.browser).release().perform()


    def crack(self):
        """
        验证验证码
        :return :判断结果
        """
        # 获取带缺口验证码图片url，位置信息
        cut_img_url, cut_img_location = self.get_img_info('//div[@class="gt_cut_bg_slice"]')
        # print(cut_img_location)

        # 获取完整验证码图片url，位置信息
        full_img_url, full_img_location = self.get_img_info('//div[@class="gt_cut_fullbg_slice"]')
        # print(cut_img_url, full_img_url)

        # 拼接缺口验证码图片
        cut_img = self.mosaic_img(cut_img_url, cut_img_location)
        full_img = self.mosaic_img(full_img_url, full_img_location)
        # full_img.show()

        # 保存图片
        cut_img.save(sys.path[0] + '/cut_img.jpg')
        full_img.save(sys.path[0] + '/full_img.jpg')

        # 获取缺口位置
        gap = self.get_distance(cut_img, full_img)
        print('缺口位置', gap)
        # 减去缺口位移
        gap -= 8

        # 获取移动轨迹
        track = self.get_track(gap)
        print('移动轨迹', track)

        # 获取滑块
        slider = self.get_slider()
        # print(slider)

        # 拖动滑块
        self.move_to_gap(slider, track)

        try:
            # 判断是否验证通过
            success = self.wait.until(
                EC.text_to_be_present_in_element((By.XPATH, '//span[@class="gt_info_type"]'), '验证通过:'))
            print('验证通过')
        except:
            print('验证不通过')
            success = False

        return success
    def run(self):
        """
        运行
        """
        # 输入账号
        self.open()

        # 验证码验证,不通过尝试刷新直至通过为止
        while not self.crack():
            # self.refresh()
            pass
        

if __name__ == '__main__':
    mycrack = CrackHuxiu()
    mycrack.run()