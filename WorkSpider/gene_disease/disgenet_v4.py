# -*- coding:utf-8 -*-

import time
import csv
import pymysql

def parse_dsv(infile):
    """
    解析dsv数据
    :params infile: dsv文件路径
    """
    with open(infile, encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if not row[0] == 'geneId':
                # geneSymbol row[1]
                # 储存基因信息
                gene_list = [row[0],row[1]]
                # print(gene_list)
                save_mysql(gene_list, 'gene_primary', 'curated_disgenet')
                # diseaseName row[5]
                # 储存疾病信息
                disease_list = [row[4],row[5]]
                # print(disease_list)
                save_mysql(disease_list, 'disease', 'curated_disgenet')
                # 储存疾病、基因相关信息
                gd_list = [row[4], row[0]]
                # print(gd_list)
                save_mysql(gd_list, 'gd', 'curated_disgenet')

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
    infile = r'./curated_gene_disease_associations.tsv'

    # 解析数据
    parse_dsv(infile)
     
    print('stop', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    print('all', time.time()-start)
