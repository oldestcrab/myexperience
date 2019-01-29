# -*- encoding:utf-8 -*-

import re
import sys
import os
import pymysql
import time
import random
import requests
import redis

class RequestsParams():
    def init(self):
        super(RequestsParams, self).__init__()

    def user_agent(self):
        """
        :return: 返回一个随机选择的user-agent
        """
        user_agent_dir = r'C:/Users/CRAB/Desktop/myexperience/WorkSpider/spider/user-agents.txt'
        # user_agent_dir = r'/home/bmnars/spider_porject/spider/user-agents.txt'
        with open(user_agent_dir, 'r', encoding = 'utf-8') as f:
            user_agents_list = f.readlines()
            user_agent = random.choice(user_agents_list).strip()
        return user_agent

    def proxy(self):
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

class ParseArticleSource():

    def sub_img_url(self, article_content, img_change_dir):
        """
        匹配文章内容中的图片url，替换为本地图片url
        :params article_content: 文章正文部分
        :params img_change_dir: 图片替换路径
        :return: 返回替换图片url后的文章正文
        """
        def img_url_change(match):
            """
            匹配文章内容中的图片url，替换为本地url
            :return: 返回替换的文章url
            """
            img_origin_name_pattern = re.compile(r'\.[pjbg][pinm]', re.I)
            img_origin_name = img_origin_name_pattern.search(match.group())
            # print('match.group(1)', match.group(1))
    
            if img_origin_name and match.group(1):
                img_save_part_name_pattern = re.compile(r'.*\/(.*\.[jpbg][pmin]\w+)', re.I)
                img_save_part_name = img_save_part_name_pattern.search(match.group(1)).group(1).replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','')
                img_name = '<img src="' + img_change_dir + img_save_part_name + '" />'
                # print('img_name: ', img_name)
                return img_name
    
        # 匹配文章内容中的图片url，替换为本地图片url
        local_img_pattern = re.compile(r'<img.*?\ssrc="(.*?)".*?>{1}', re.I|re.S)
        article_content = local_img_pattern.sub(img_url_change, article_content)

        return article_content

    def sub_article_content(self, article_content, img_change_dir):
        """
        剔除文章中不需要的内容，并匹配文章内容中的图片url，替换为本地图片url
        :params article_content: 文章正文部分
        :params img_change_dir: 图片替换路径
        :return: 清洗后的正文
        """

        def img_url_change(match):
            """
            匹配文章内容中的图片url，替换为本地url
            :return: 返回替换的文章url
            """
            img_origin_name_pattern = re.compile(r'\.[pjbg][pinm]', re.I)
            img_origin_name = img_origin_name_pattern.search(match.group())
            # print('match.group(1)', match.group(1))
    
            if img_origin_name and match.group(1):
                img_save_part_name_pattern = re.compile(r'.*\/(.*\.[jpbg][pmin]\w+)', re.I)
                img_save_part_name = img_save_part_name_pattern.search(match.group(1)).group(1).replace(r'/','').replace(r'\\','').replace(':','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','').replace('?','').replace('%','').strip()
                img_name = '<img src="' + img_change_dir + img_save_part_name + '" />'
                # print('img_name: ', img_name)
                return img_name
    
        # 匹配文章内容中的图片url，替换为本地图片url
        local_img_pattern = re.compile(r'<img.*?\ssrc="(.*?)".*?>{1}', re.I|re.S)
        article_content = local_img_pattern.sub(img_url_change, article_content)

        # 剔除文章中不需要的内容
        def article_change(match):
            """
            匹配文章内容中的所有标签（a、img、p）除外，剔除掉
            """
            # <p src="./img/13SsuHuXECVJ<p style="text-align: center;"> p
            # print(match.group(),match.group(1))
            tag_name = ''
            return tag_name
    
        article_change_pattern = re.compile(r'<([^/aip]\w*)\s*.*?>{1}', re.I)
        article_content = article_change_pattern.sub(article_change, article_content)
    
        # 剔除所有除</ap>外的</>标签
        article_change_pattern_1 = re.compile(r'</[^pa].*?>{1}', re.I)
        article_content = article_change_pattern_1.sub('', article_content)
    
        # 剔除<P>标签的样式
        article_change_pattern_2 = re.compile(r'<p.*?>{1}', re.I)
        article_content = article_change_pattern_2.sub('<p>', article_content)
    
        # 剔除一些杂乱的样式
        article_content = article_content.replace('<i>','').strip()

        return article_content

    def join_article_content(self, article_content, article_title, article_user, article_update_time, article_origin_website, ):
        """
        组合并且格式化内容
        :params article_content: 文章正文部分
        :params article_title: 文章标题
        :params article_user: 文章作者
        :params article_update_time: 文章更新时间
        :params article_origin_website: 文章来源网站
        :return: 完全清洗后的正文，列表形式写入文件中
        """
        article_list = []
        # html开头
        article_list.append('<!DOCTYPE html>\n' + '<html>\n' + '<head>\n' + '<meta charset="utf-8"/>\n')

        # 标题
        title = '<title>' + article_title + '</title>\n' + '</head>\n'
        article_list.append(title)
        # 来源
        origin = '<body>\n' + '<div class = "source">' + article_origin_website + '</div>\n' + '<div class = "user">' + article_user + '</div>\n' + '<div class = "time">' + article_update_time + '</div>\n' + '<content>\n'
        article_list.append(origin)
        # 正文
        content = article_content + '\n</content>\n' + '</body>\n' + '</html>\n'
        article_list.append(content)

        return article_list

class SaveArticleSource():
    def __init__(self, page_save_dir, article_origin_website):
        """
        :param page_save_dir: 文章存储路径
        :param article_origin_website: 文章来源网站
        """
        super(SaveArticleSource, self).__init__()
        self.page_save_dir = page_save_dir
        self.article_origin_website = article_origin_website


    def save_article_img(self, img_source, img_name):
        """
        保存文章中的图片
        :param img_source: 图片二进制文件
        :param img_name: 图片存储名
        """
        img_save_dir = self.page_save_dir + 'img/'
        if not os.path.exists(img_save_dir):
            os.makedirs(img_save_dir)
        try:
            # 保存图片
            with open(img_save_dir + img_name, 'wb') as f:
                f.write(img_source)  
        except Exception as e:
            print('图片保存失败：', e.args)

    def save_article_page(self, article_real_content_list, filename):
        """
        保存文章
        :param article_real_content_list: 文章清洗过后的格式化内容
        :param filename: 文章存储名
        """
        if not os.path.exists(self.page_save_dir):
            os.makedirs(self.page_save_dir)
        try:
            with open(self.page_save_dir + filename , 'w', encoding = 'utf-8') as f:
                for i in article_real_content_list:
                    f.write(i)
        except  Exception as e:
            print('内容保存失败：', e.args)

    def save_mysql(self, source_url, filename):
        """
        保存到mysql
        :param source_url: 文章来源url
        :param filename: 文章存储名
        """
        db = pymysql.connect(host='localhost', user='bmnars', password='vi93nwYV', port=3306, db='bmnars')
        cursor = db.cursor()
        local_url =  self.page_save_dir + filename  
        update_time = time.strftime('%Y-%m-%d',time.localtime())
        data = {
            'source_url':source_url,
            'local_url':local_url,
            'source':self.article_origin_website,
    	    'update_time':update_time
        }
        table = '_cs_bmnars_link_v2'
        keys = ','.join(data.keys())
        values = ','.join(['%s']*len(data))
        sql = 'INSERT INTO {table}({keys}) VALUES ({values}) on duplicate key update '.format(table=table, keys=keys, values=values)
        update = ', '.join(['{key} = %s'.format(key=key) for key in data]) + ';'
        sql += update
        # print(sql)
        try:
            if cursor.execute(sql,tuple(data.values())*2):
                db.commit()
        except:
            print("save_mysql_failed:" + source_url)
            db.rollback()
        finally:
            cursor.close()      
            db.close()


def main():
    """
    遍历每一页索引页
    """
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    start_time = time.time()

    # help(SaveArticleSource)
    # help(RequestsParams)
    help(ParseArticleSource)
    # a = RequestsParams()
    # print(a.proxy())

    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    print('共用时：', time.time()-start_time)


if __name__ == '__main__': 
    main()