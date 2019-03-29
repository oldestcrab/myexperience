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
    f = open(infile, 'r', encoding='utf-8', newline='')
    # 获取读句柄
    reader = csv.reader(f, delimiter='\t')
    # 打开要写入的文件
    s = open(r'C:/Users/CRAB/Desktop/mim2gene.csv', 'w', encoding='utf-8', newline='')
    # 获取写句柄
    writer = csv.writer(s)
    # 写入头
    writer.writerow(['mim_id', 'entrez_gene_id', 'name', 'ensembl_gene_id'])
    for row in reader:
        if len(row) == 5 and 'gene' in row[1] and row[3]:
            # 获取需要的数据
            new_row = [row[0],row[2],row[3],row[4],'2019-03-29']
            if not new_row[1]:
                new_row[1] = 0
                # print(new_row)
            writer.writerow(new_row)
    f.close()
    s.close()


if __name__ == '__main__':
    print('start', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    start = time.time()

    infile = r'C:/Users/CRAB/Desktop/mim2gene.txt'
    parse_txt(infile)

    print('stop', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    print('all', time.time()-start)