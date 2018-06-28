import re
# /htmlpaper/201861510484322846535.shtm
#pattern = re.compile('[a-zA-Z./]')
patterns = re.compile('<img src="(.*?).jpg', re.S)
a = '''
<img src="/upload/news/images/2018/6/2018s621135十大高手给是嘀咕嘀咕9331460.jpg">
<img src="/upload/news/images/2018/6/20186211359331460.jpg">
'''


def test(match):
    #print(match.group(0))
    #print(match.group(1))
    pattern = re.compile('[a-zA-Z/]')
    c = pattern.sub('', match.group(1))
    d = '<img src="./img/' + c
    #print(d)
    return d
b = patterns.sub(test, a)

#print(b.group(1))
#print(b)
kw = '''
<img alt="" oldsrc="W020180517381868922980.jpg" src="http://www.ivpp.ac.cn/xwdt/kydt/201805/W020180517381868922980.jpg" style="border-width: 0px;">
'''
img_pattern = re.compile(r'<img(.*?)\ssrc="(.*?)"', re.S)
img_findall = img_pattern.findall(kw)
for detail in img_findall:
    print(type(detail), detail[1])
