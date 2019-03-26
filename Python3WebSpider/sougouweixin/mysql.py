# -*- coding:utf-8 -*-

import pymysql
from settings import *

class MySQL():
    def __init__(self):
        """
        mysql初始化
        """
        try:
            self.db = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, port=MYSQL_PORT,database=MYSQL_DATABASE)
            self.cursor = self.db.cursor()
        except Exception as e:
            print('connect mysql error',e.args)
    
    def __del__(self):
        self.cursor.close()
        self.db.close()
        
    def insert(self, table, data):
        """
        插入数据
        :param table: 表名
        :param data: 数据
        """
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql_query = 'insert into %s (%s) values (%s)' % (table, keys, values)
        try:
            self.cursor.execute(sql_query, tuple(data.values()))
            self.db.commit()
        except pymysql.MySQLError as e:
            print(e.args)
            self.db.rollback()