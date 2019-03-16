# -*- coding:utf-8 -*-

import xml.sax

class MyHandler(xml.sax.ContentHandler):
    def __init__(self):
        super(MyHandler, self).__init__()
        self.data = ''
        self.gene = ''
        self.protein = ''

    def startElement(self, tag, attributes):
        self.data = tag
        if tag == 'gene':
            print('+++++++++++++++++++++++++++++')
            # t = attributes['created']
            # print(t)

    def endElement(self, tag):
        if self.data == 'name':
            print('gene', self.gene)
        # if self.data == 'protein':
        #     print('protein', self.protein)

    def characters(self, content):
        if self.data == 'name':
            self.gene = content
            # print('gene', content)
        # if self.data == 'protein':
        #     self.gene = content

if __name__ == '__main__':
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    handler = MyHandler()
    parser.setContentHandler(handler)
    parser.parse(r'C:/Users/CRAB/Desktop/1/1.xml')
