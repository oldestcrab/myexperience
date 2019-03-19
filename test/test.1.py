from lxml import etree

context = etree.parse(r'C:/Users/CRAB/Desktop/a.xml')
print(context)
elem = context.xpath('//revision')[0]
# print(elem.getparent()[1].text)
# for i in elem.getparent():
#     print(i)
while elem.getprevious() is not None:
    print(elem.getparent()[0])
    del elem.getparent()[0]