# -*- coding:utf-8 -*-

from lxml import etree
import pymysql
import time

def fast_iter(context, func, *args, **kwargs):
    """
    读取xml数据，并释放空间
    :params context: etree.iterparse生成的迭代器
    :params func:处理xml数据的func
    """
    # 事件、元素
    for event, elem in context:
        # 处理xml数据
        func(elem, *args, **kwargs)
        # 重置元素，清空元素内部数据
        elem.clear()
        # 选取当前节点的所有先辈（父、祖父等）以及当前节点本身
        for ancestor in elem.xpath('ancestor-or-self::*'):
            # 如果当前节点还有前一个兄弟，则删除父节点的第一个子节点。getprevious():返回当前节点的前一个兄弟或None。
            while ancestor.getprevious() is not None:
                # 删除父节点的第一个子节点，getparent()：返回当前节点的父元素或根元素或None。
                del ancestor.getparent()[0]
    # 释放内存
    del context


def process_element(elem):
    """
    处理element
    :params elem: Element
    """
    # 储存基因列表
    gene_list = []
    for i in elem.xpath('.//*[local-name()="gene"]/*[local-name()="name"]'):
        # 获取基因名字
        gene = i.text
        # 添加到列表
        gene_list.append(gene)
    # 存入mysql
    # print('gene', gene_list)
    save_mysql(gene_list, 'gene')
    
    # 储存所有疾病列表
    disease_list = []
    # print(elem.xpath('./@created'))
    for i in elem.xpath('.//*[local-name()="disease"]'):
        # 储存每个疾病列表的详细信息
        disease_list_inner = []
        # 获取疾病名字
        disease_name = i.xpath('./*[local-name()="name"]')[0].text
        # 添加到列表
        disease_list_inner.append(disease_name)
        # 获取疾病缩写
        disease_acronym = i.xpath('./*[local-name()="acronym"]')[0].text
        # 添加到列表
        disease_list_inner.append(disease_acronym)
        # print(disease_list_inner)
        # 嵌套列表
        disease_list.append(disease_list_inner)
    # 存入mysql
    # print('disease', disease_list)
    save_mysql(disease_list, 'disease')
    
    # 判断是否都有
    if gene_list and disease_list:
        # 储存基因和疾病关联信息
        gd_list = []
        for gene_name in gene_list:
            for disease in disease_list:
                disease_name = disease[0]
                # 组合基因和疾病
                gd_list_inner = [gene_name, disease_name]
                # 添加到列表
                gd_list.append(gd_list_inner)
        print(gd_list)
        # 存入mysql
        save_mysql(gd_list, 'gd')

def save_mysql(source, flag):
        """
        保存到mysql
        :param source: 数据
        :param flag: 标识
        """
        # 连接数据库
        db = pymysql.connect(host='localhost', user='bmnars', password='vi93nwYV', port=3306, db='gene_disease')
        # 获得句柄
        cursor = db.cursor()
        # 时间
        update_time = time.strftime('%Y-%m-%d',time.localtime())
        try:
            # 如果标识为gene，且存在内容，则为基因信息存入表gene中，
            if flag == 'gene' and source:
                for name in source:
                    data = {
                        'name':name,
                        'update_time':update_time
                    }
                    table = 'gene'
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
                    except:
                        print("save mysql gene failed")
                        # 错误则回滚
                        db.rollback()

            # 如果标识为disease，且存在内容，则为基因信息存入表disease中，
            if flag == 'disease' and source:
                # print(source)
                # i为列表
                for i in source:
                    data = {
                        'name':i[0],
                        'acronym':i[1],
                        'update_time':update_time
                    }
                    table = 'disease'
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
                        # print('save mysql disease success')
                    except:
                        print("save mysql disease failed")
                        # 错误则回滚
                        db.rollback()

            # 如果标识为gd，且存在内容，则为基因与疾病关系存入表gd中，
            if flag == 'gd' and source:
                for i in source:
                    # 通过disease_name查询disease_id
                    try:
                        sql_disease_id = 'select id from disease where name = "{disease_name}";'.format(disease_name=i[1])
                        cursor.execute(sql_disease_id)
                        disease_id = cursor.fetchone()[0]
                        # print(disease_id)
                    except:
                        print('get disease id error', i[1])

                    # 通过gene_name查询gene_id
                    try:
                        sql_gene_id = 'select id from gene where name = "{gene_name}";'.format(gene_name=i[0])
                        # print(sql_gene_id)
                        cursor.execute(sql_gene_id)
                        gene_id = cursor.fetchone()[0]
                        # print(gene_id)
                    except:
                        print('get disease id error', i[1])

                    data = {
                        'disease_id':disease_id,
                        'gene_id':gene_id,
                        'update_time':update_time
                    }
                    table = 'gd'
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
        except:
            print('save_mysql error')
        finally:
            # 关闭句柄
            cursor.close()      
            # 关闭连接
            db.close()

if __name__ == '__main__':
    print('start', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    start = time.time()

    # 文件路径
    infile = r'C:/Users/CRAB/Desktop/a.xml'
    # 通过迭代读取xml，带命名空间的要加上命名空间
    context = etree.iterparse(infile,events=('end',),encoding='UTF-8',tag='{http://uniprot.org/uniprot}entry')
    # 快速读取xml数据
    fast_iter(context,process_element)

    print('stop', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    print('time', time.time()-start)