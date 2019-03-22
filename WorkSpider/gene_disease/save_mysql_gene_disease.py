# -*- coding:utf-8 -*-

import pymysql
import time

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
        # 如果标识为disease_parent，则为疾病父类信息存入表disease_parent_*中，
        if flag == 'disease_parent' and source:
            data = {
                'name':source[1],
                'parent_name':source[0],
                'update_time':update_time
            }
            table = 'disease_parent_'+table_name
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
                print("save mysql disease_parent failed", e.args)
                # 错误则回滚
                db.rollback()

        # 如果标识为disease，且存在内容，则为基因信息存入表disease中，
        if flag == 'disease' and source:
            if len(source) ==3:
                data = {
                    'name':source[1],
                    'acronym':source[2],
                    'parent_name':source[0],
                    'update_time':update_time
                }
            else:
                data = {
                    'name':source[1],
                    'parent_name':source[0],
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
            except Exception as e:
                print("save mysql disease failed", e.args)
                # 错误则回滚
                db.rollback()

        # 如果标识为gene_primary，且存在内容，则为基因信息存入表gene_primary中，
        if flag == 'gene_primary' and source:
            data = {
                'name':source,
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
            # 通过disease_name查询disease_id
            try:
                sql_disease_id = 'select id from disease_{table_name} where name = "{disease_name}";'.format(disease_name=source[0], table_name=table_name)
                cursor.execute(sql_disease_id)
                disease_id = cursor.fetchone()[0]
                # print(disease_id)
            except Exception as e:
                print('get disease id error', e.args)
            # 通过gene_name查询gene_id
            try:
                sql_gene_id = 'select id from gene_primary_{table_name} where name = "{gene_name}";'.format(gene_name=source[1], table_name=table_name)
                # print(sql_gene_id)
                cursor.execute(sql_gene_id)
                gene_id = cursor.fetchone()[0]
                # print(gene_id)
            except:
                print('get gene id error')
            data = {
                'disease_id':disease_id,
                'gene_id':gene_id,
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

