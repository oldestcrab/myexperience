# -*- coding:utf-8 -*-

from lxml import etree
import pymysql
import time

def fast_iter(context, func, *args, **kwargs):
    """
    读取xml数据，并释放空间
    :params context: etree.iterparse生成的可迭代对象
    :params func:处理xml数据的func
    """
    # 时间、元素
    for event, elem in context:
        # 处理xml数据
        func(elem, *args, **kwargs)
        # It's safe to call clear() here because no descendants will be
        # accessed
        elem.clear()
        # Also eliminate now-empty references from the root node to elem
        for ancestor in elem.xpath('ancestor-or-self::*'):
            while ancestor.getprevious() is not None:
                del ancestor.getparent()[0]
    del context


def process_element(elem):
        # 储存主要基因列表
        gene_primary_list = []
        # 储存别名基因列表
        gene_synonym_list = []

        for i in elem.xpath('.//*[local-name()="gene"]'):
            # 获取主要基因名字
            gene_primary = i.xpath('./*[local-name()="name"][@type="primary"]')
            for gene in gene_primary:
                # 添加到列表
                gene_primary_list.append(gene.text)
            # 获取别名基因名字
            gene_synonym = i.xpath('./*[local-name()="name"][@type="synonym"]')
            for gene in gene_synonym:
                # 添加到列表
                gene_synonym_list.append(gene.text)

        # 储存基因列表
        gene_list = [gene_primary_list, gene_synonym_list]
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
        if gene_primary_list and disease_list:
            # 储存基因和疾病关联信息
            gd_list = []
            for gene_name in gene_primary_list:
                for disease in disease_list:
                    disease_name = disease[0]
                    # 组合基因和疾病
                    gd_list_inner = [gene_name, disease_name]
                    # 添加到列表
                    gd_list.append(gd_list_inner)

            # print(gd_list)
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
            # 如果标识为gene，且储存primary的列表存在内容，则为主要基因信息存入表gene_primary_uniprot中，
            if flag == 'gene' and source[0]:
                for name in source[0]:
                    data = {
                        'name':name,
                        'update_time':update_time
                    }
                    table = 'gene_primary_uniprot'
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

            # 如果标识为gene，且储存synonym的列表存在内容，则为别名基因信息存入表gene_synonym_uniprot中，
            if flag == 'gene' and source[0]  and source[1] :
                for primary_name in source[0]:
                    for name in source[1]:
                        # 通过primary_name查询primary_id
                        try:
                            sql_primary_id = 'select id from gene_primary_uniprot where name = "{primary_name}";'.format(primary_name=primary_name)
                            cursor.execute(sql_primary_id)
                            primary_id = cursor.fetchone()[0]
                            # print(primary_id)
                        except Exception as e:
                            print('get  primary id error', e.args)
                        data = {
                            'name':name,
                            'update_time':update_time,
                            'primary_id':primary_id
                        }
                        table = 'gene_synonym_uniprot'
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
                            print("save mysql synonym gene failed", e.args)
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
                    table = 'disease_uniprot'
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
                    except Exception as e:
                        print("save mysql disease failed", e.args)
                        # 错误则回滚
                        db.rollback()

            # 如果标识为gd，且存在内容，则为基因与疾病关系存入表gd中，
            if flag == 'gd' and source:
                for i in source:
                    # 通过disease_name查询disease_id
                    try:
                        sql_disease_id = 'select id from disease_uniprot where name = "{disease_name}";'.format(disease_name=i[1])
                        cursor.execute(sql_disease_id)
                        disease_id = cursor.fetchone()[0]
                        # print(disease_id)
                    except Exception as e:
                        print('get disease id error', e.args)

                    # 通过gene_name查询gene_id
                    try:
                        sql_gene_id = 'select id from gene_primary_uniprot where name = "{gene_name}";'.format(gene_name=i[0])
                        # print(sql_gene_id)
                        cursor.execute(sql_gene_id)
                        gene_id = cursor.fetchone()[0]
                        # print(gene_id)
                    except:
                        print('get gene id error', i[1])

                    data = {
                        'disease_id':disease_id,
                        'gene_id':gene_id,
                        'update_time':update_time
                    }
                    table = 'gd_uniprot'
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
    infile = r'./uniprot_sprot.xml'
    # 通过迭代读取xml，带命名空间的要加上命名空间
    context = etree.iterparse(infile,events=('end',),encoding='UTF-8',tag='{http://uniprot.org/uniprot}entry')
    # 快速读取xml数据
    fast_iter(context,process_element)
    print('stop', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    print('time', time.time()-start)