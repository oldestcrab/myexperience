import re


a = 'http://gzdaily.dayoo.com/h5/resfile/2018-03-28/A13/545832_luozc_1522151092253_b.jpg?v=6C9EF44E72B7D8707973EFF2A2439B83'

pattern = re.compile(r'.*?(\w+.[jpb][pmn]\w+)')
b = pattern.search(a).group(1)
print(b)