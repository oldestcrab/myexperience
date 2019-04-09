# -*- coding:utf-8 -*-
import csv

with open(r'C:/Users/CRAB/Desktop/ene.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['mim_id', 'entrez_gene_id', 'name', 'ensembl_gene_id'])
