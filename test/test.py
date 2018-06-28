import re
# /htmlpaper/201861510484322846535.shtm
#pattern = re.compile('[a-zA-Z./]')
patterns = re.compile('<img src="(.*?).jpg', re.S)
a = '''
<img src="/upload/news/images/2018/6/2018s621135十大高手给是嘀咕嘀咕9331460.jpg">
<img src="/upload/news/images/2018/6/20186211359331460.jpg">
'''
patternss = re.compile('s(r)c')
j = patternss.search(a)
print(j,type(j))
print(j.group(1),type(j.group()))

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


