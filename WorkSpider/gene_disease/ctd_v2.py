# -*- coding:utf-8 -*-

import time
import csv
import re
import pymysql

def parse_csv(infile):
    """
    解析csv数据
    :params infile: csv文件路径
    """
    # 读取csv文件
    with open(infile, encoding='utf-8', newline='') as f:
        # 获取句柄
        reader = csv.reader(f, delimiter='\t')
        # 逐行读取
        for row in reader:
            # print(len(row))
            # 过滤注释信息
            if not row[0].startswith('#'):
                # print(row)
                # 内容为 , 分隔，再读取一遍
                reader_row = csv.reader(row, delimiter=',')
                # print(reader_row)
                # 获取数据
                for line in reader_row:
                    # print('gene_name', line[0])
                    # print('gene_id', line[1])
                    # print('DiseaseName', line[2])
                    # print('DiseaseID', line[3])
                    # 疾病列表
                    disease_list = [line[3],line[2]]
                    # 储存疾病信息
                    save_mysql(disease_list, 'disease', 'ctd')
                    # 基因列表
                    gene_list = [line[1],line[0]]
                    # 储存基因信息
                    save_mysql(gene_list, 'gene_primary', 'ctd')
                    # 疾病和基因关系列表
                    gd_list = [line[3],line[1]]
                    # 储存疾病和基因关系信息
                    save_mysql(gd_list, 'gd', 'ctd')

def save_mysql(source, flag, table_name):
    """
    保存到mysql
    :param source: 数据
    :param flag: 标识,告知source数据读取方式以及存入哪张表
    :param table_name: 表名
    """
    # 连接数据库
    db = pymysql.connect(host='localhost', user='bmnars', password='vi93nwYV', port=3306, db='gene_disease')
    # 获得句柄
    cursor = db.cursor()
    # 时间
    update_time = time.strftime('%Y-%m-%d',time.localtime())
    try:
        # 如果标识为disease，且存在内容，则为基因信息存入表disease中，
        if flag == 'disease' and source:
            # print(source)
            data = {
                'id':source[0],
                'name':source[1],
                'update_time':update_time
            }
            table = 'disease_'+table_name
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
                    # print(1)
            except Exception as e:
                print("save mysql disease failed", e.args)
                # 错误则回滚
                db.rollback()

        # 如果标识为gene_primary，且存在内容，则为基因信息存入表gene_primary中，
        if flag == 'gene_primary' and source:
            data = {
                'id':source[0],
                'name':source[1],
                'update_time':update_time
            }
            table = 'gene_primary_'+table_name
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
            except Exception as e:
                print("save mysql gene_primary failed", e.args)
                # 错误则回滚
                db.rollback()

        # 如果标识为gd，且存在内容，则为基因与疾病关系存入表gd中，
        if flag == 'gd' and source:
            data = {
                'disease_id':source[0],
                'gene_id':source[1],
                'update_time':update_time
            }
            table = 'gd_' + table_name
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
                # print('save mysql gd success')
            except:
                print("save mysql gd failed")
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
    print('start', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    start = time.time()

    # 文件路径
    infile = r'./CTD_genes_diseases.csv'
    # 解析数据
    parse_csv(infile)
     
    print('stop', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    print('all', time.time()-start)
