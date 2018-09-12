import re

a = r"\s\tsd\n"
print(a)
pattern = re.compile(r'\\t')
b = pattern.search(a)
print(b.group())