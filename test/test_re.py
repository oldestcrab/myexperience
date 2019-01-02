import re

url = 'https://www.vigenebio.com/search/search.php?keyword=cdk2&totalresult=36&pageno=2'
print(url)
kw_re = re.search(r'keyword=(.*)&to', url)
if not kw_re:
    kw = re.search(r'keyword=(.*)', url).group(1)
else:
    kw = kw_re.group(1)


