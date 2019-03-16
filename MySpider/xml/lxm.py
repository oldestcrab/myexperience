# -*- coding:utf-8 -*-

from lxml import etree


# def parse():
#     infile = r'C:/Users/CRAB/Desktop/uniprot_sprot.xml/uniprot_sprot.xml'
#     # 读取entry标签
#     context = etree.iterparse(infile, tag='entry')
#     for event, element in context:
#         print('==================')
#         # 储存基因列表
#         gene_list = []
#         for i in element.xpath('./gene/name'):
#             # 获取基因名字
#             gene = i.text
#             gene_list.append(gene)
#         print(gene_list)

#         # # 储存疾病列表
#         disease_list = []
#         for i in element.xpath('.//disease/name'):
#             # 获取疾病名字
#             disease = i.text
#             disease_list.append(disease)
#         print(disease_list)
        
#         if gene_list and disease_list:
#             print('-------------')
            
#     element.clear()
#     while element.getprevious() is not None:
#         del element.getparent()[0]
        
def save():
    """
    保存数据到MySQL
    """

def fast_iter(context, func, *args, **kwargs):
    """
    http://lxml.de/parsing.html#modifying-the-tree
    Based on Liza Daly's fast_iter
    http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    See also http://effbot.org/zone/element-iterparse.htm
    """
    for event, elem in context:
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
        print('==================')
        # 储存基因列表
        gene_list = []
        for i in elem.xpath('./gene/name'):
            # 获取基因名字
            gene = i.text
            gene_list.append(gene)
        print(gene_list)

        # # 储存疾病列表
        disease_list = []
        for i in elem.xpath('.//disease/name'):
            # 获取疾病名字
            disease = i.text
            disease_list.append(disease)
        print(disease_list)
        
        if gene_list and disease_list:
            print('-------------')




if __name__ == '__main__':
    # parse()
    infile = r'C:/Users/CRAB/Desktop/uniprot_sprot.xml/uniprot_sprot.xml'
    context = etree.iterparse(infile, tag='entry' )
    fast_iter(context,process_element)
