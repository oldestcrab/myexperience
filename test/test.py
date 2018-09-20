import re
a = '''config.py<img src="./img/13SsuHuXECVJ11hbkQKbyyf3vIylBimna0pU3yEe.jpeg" alt="WechatIMG9590" style="max-width:100%;">sdsdgsdfgdlgjdljd<img src="./img/13SsuHuXECVJ11hbkQKbyyf3vIylBimna0pU3yEe.jpeg" alt="WechatIMG9590"">dd">
'''

pattern = re.compile(r'<img.*?\ssrc="(.*?)".*?>{1}')

b = pattern.search(a)
print(b.group(),'\n',b.group(1))
