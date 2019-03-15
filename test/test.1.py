#  -*- coing:utf-8 -*-

from xml.etree import ElementTree

dom = ElementTree.parse(r'C:/Users/CRAB/Desktop/uniprot_sprot.xml/uniprot_sprot.xml')
a = dom.findall('gene')
for i in a:
    print(i.xml)
    print(i.text)
# print(dom)