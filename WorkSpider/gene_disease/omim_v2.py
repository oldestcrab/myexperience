# -*- coding:utf-8 -*-
import time
import csv
import pymysql

def parse_txt(infile):
    """
    解析txt文件
    :params infile: txt文件路径
    """
    # 读取原文件
    with open(infile, 'r', encoding='utf-8', newline='') as f:
        # 获取读句柄
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) == 5 and 'gene' in row[1] and row[3]:
                # 获取需要的数据
                new_row = [row[0],row[2],row[3],row[4],'2019-03-29']
                if not new_row[1]:
                    new_row[1] = 0
                    # print(new_row)
                save_mysql(new_row, 'gene_primary', 'omim')

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
        if flag == 'gene_primary' and source:
            data = {
                'mim_id':source[0],
                'entrez_gene_id':source[1],
                'name':source[2],
                'ensembl_gene_id':source[3],
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

    infile = r'./mim2gene.txt'
    parse_txt(infile)

    print('stop', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    print('all', time.time()-start)