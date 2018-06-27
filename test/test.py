import re
# /htmlpaper/201861510484322846535.shtm
pattern = re.compile('不(.*?)吧')
a = '/ht不124356吧mlpaper/201861510484322846535.shtmhtmlnews/2018/6/4140不dsgds好吧34.shtm'
b = pattern.sub('好吧',a)
#print(b.group(1))
print(b)