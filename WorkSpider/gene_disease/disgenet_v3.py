# -*- coding:utf-8 -*-

import time
import csv
from save_mysql_gene_disease import save_mysql

def parse_dsv(infile):
    """
    解析dsv数据
    :params infile: dsv文件路径
    """
    with open(infile, encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            # geneSymbol row[1]
            # 储存基因信息
            save_mysql(row[1], 'gene_primary', 'disgenet')
            # diseaseName row[5]
            # 储存疾病信息
            disease_list = ['', row[5]]
            save_mysql(disease_list, 'disease', 'disgenet')
            # 储存疾病、基因相关信息
            gd_list = [row[5], row[1]]
            save_mysql(gd_list, 'gd', 'disgenet')


if __name__ == '__main__':
    print('start', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    start = time.time()
    # 文件路径
    infile = r'./all_gene_disease_pmid_associations.tsv'

    # 解析数据
    parse_dsv(infile)
     
    print('stop', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    print('all', time.time()-start)
