# -*- coding:utf-8 -*-

import json
import jsonpath
import time
import pymysql
import re
from save_mysql_gene_disease import save_mysql

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
                    # name为父辈疾病 
                    parent_name_list = [name, children_name]
                    # print(name_list)
                    # 保存至mysql
                    save_mysql(parent_name_list, 'disease', 'kegg')

                else:
                    # name为父辈疾病,new_name为子疾病
                    new_name = re.sub(r'\[.*\]','',re.search(r'H\d+\s+(.*)', children_name).group(1))
                    disease_name_list = [name, new_name.strip()]
                    # print(disease_name_list)
                    # 保存至mysql
                    save_mysql(disease_name_list, 'disease_parent', 'kegg')
            else:
                # name为疾病信息，children_name为基因信息
                # print(name)
                # print(children_name)
                if re.search(r'.*\[.*\]', children_name) and re.search(r'^H\d+', name):
                    # 基因名
                    gene_name = re.sub(r'\(.*\)','',re.search(r'(.*?)\[.*\]', children_name).group(1))
                    # 保存至mysql
                    save_mysql(gene_name, 'gene_primary', 'kegg')
                    # 疾病名
                    disease_name = re.sub(r'\[.*\]','',re.search(r'H\d+\s+(.*)', name).group(1))
                    # 储存疾病、基因信息
                    gd_list = [disease_name, gene_name]
                    # 保存至mysql
                    save_mysql(gd_list, 'gd', 'kegg')

            # 遍历迭代
            handle_json(children_name, children_children)

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