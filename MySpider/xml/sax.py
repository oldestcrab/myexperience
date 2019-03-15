# -*- coding:utf-8 -*-

import xml.sax

class MyHandler():
    def __init__(self):
        super(MyHandler, self).__init__()


if __name__ == '__main__':
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    handler = MyHandler()
    parser.setContentHandler(handler)
    parser.parse(r'C:/Users/CRAB/Desktop/uniprot_sprot.xml/uniprot_sprot.xml')
