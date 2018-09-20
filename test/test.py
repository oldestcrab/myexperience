import re
a = '''config.py<img src="./img/13SsuHuXECVJ11hbkQKbyyf3vIylBimna0pU3yEe.jpeg" alt="WechatIMG9590" style="max-width:100%;">sdsdgsdfg
dlgjdljd<img src="./img/13SsuHuXECVJ11hbkQKbyyf3vIylBimna0pU3yEe.jpeg" alt="WechatIMG9590"">dd">
'''

pattern = re.compile(r'<img(.*\ssrc="(.*?)".*?)>')

b = pattern.search(a)
print(b.group(),'\n',b.group(1),'\n',b.group(2))
c = pattern.sub(r'src="./img/">',a)
print(c)