import re

a = re.compile('\w')

b = '---'

c = a.search(b)
print(c,type(c))

for c in c:
    print('aaa')