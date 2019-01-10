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
        with open(sys.path[0] + '/user-agents.txt', 'r', encoding = 'utf-8') as f:
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

    def save_article_page(self, article_real_content, filename):
        """
        保存文章
        :param article_real_content: 文章清洗过后的正文
        :param filename: 文章存储名
        """
        if not os.path.exists(self.page_save_dir):
            os.makedirs(self.page_save_dir)
        try:
            with open(self.page_save_dir + filename , 'w', encoding = 'utf-8') as f:
                for i in article_real_content:
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

    help(SaveArticleSource)
    help(RequestsParams)
    # a = RequestsParams()
    # print(a.proxy())

    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    print('共用时：', time.time()-start_time)


if __name__ == '__main__':
    main()