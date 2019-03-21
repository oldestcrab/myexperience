# -*- coding:utf-8 -*-

import json
import jsonpath
import time
import pymysql
import re

def handle_json(name, children):
    """
    处理json数据
    :params name: 疾病名称
    :params children: 疾病children
    """
    # print(last_name)
    # print(name)
    # print(children)

    # 判断是否拥有children,有则继续往下迭代
    if children:
        # 遍历当前children
        for i in children:
            # 获取子疾病或者基因信息
            children_name = i.get('name')
            # 获取子children
            children_children = i.get('children')
            # 如果当前不再拥有children,则为最底部疾病信息。再往下为基因信息
            if children_children:
                # 只储存大类，具体疾病的父类存在疾病表
                if not re.search(r'^H\d+', children_name):
                    # 储存疾病名与children疾病名
                    if name == 'br08402_gene':
                        name = 'Human diseases'
                    name_list = [name, children_name]
                    # print(name_list)
                    # 保存至mysql
                    # save_mysql(name_list, 'disease_parent')
            else:
                # name为疾病信息，children_name为基因信息
                print(name)
                pattern = re.compile(r'H\d+(.*)\s([.*])?')
                b = pattern.search(a).group()
            # 遍历迭代
            handle_json(children_name, children_children)

def save_mysql(source, flag):
        """
        保存到mysql
        :param source: list数据
        :param flag: 标识
        """
        # 连接数据库
        db = pymysql.connect(host='localhost', user='bmnars', password='vi93nwYV', port=3306, db='gene_disease')
        # 获得句柄
        cursor = db.cursor()
        # 时间
        update_time = time.strftime('%Y-%m-%d',time.localtime())
        try:
            # 如果标识为disease_parent，则为疾病父类信息存入表disease_parent_kegg中，
            if flag == 'disease_parent':
                name = source[1]
                parent_name = source[0]
                data = {
                    'name':name,
                    'parent_name':parent_name,
                    'update_time':update_time
                }
                table = 'disease_parent_kegg'
                keys = ','.join(data.keys())
                values = ','.join(['%s']*len(data))
                sql = 'INSERT INTO {table}({keys}) VALUES ({values}) on duplicate key update '.format(table=table, keys=keys, values=values)
                update = ', '.join(['{key} = %s'.format(key=key) for key in data]) + ';'
                sql += update
                # print(sql)
                try:
                    # 执行语句
                    if cursor.execute(sql,tuple(data.values())*2):
                        # 提交
                        db.commit()
                    # print('save mysql gene success')
                except Exception as e:
                    print("save mysql primary gene failed", name, e.args)
                    # 错误则回滚
                    db.rollback()
        except Exception as e:
            print('save_mysql error', e.args)
        finally:
            # 关闭句柄
            cursor.close()      
            # 关闭连接
            db.close()


if __name__ == '__main__':
    # 记录开始时间
    print('start', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    start = time.time()

    # json文件路径
    infile = r'C:/Users/CRAB/Desktop/br08402_gene.json'
    # 读取json文件
    with open(infile, 'r') as f:
        context = json.load(f)
    
    name = context.get('name')
    children = context.get('children')
    # 处理json数据
    handle_json(name, children)

    # 记录结束时间
    print('stop', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    print('all', time.time()-start)