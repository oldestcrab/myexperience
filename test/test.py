import re
# /htmlpaper/201861510484322846535.shtm
pattern = re.compile('[a-zA-Z./]')
a = '/htmlpaper/201861510484322846535.shtmhtmlnews/2018/6/414034.shtm'
b = pattern.sub('',a)
print(b.group(1))