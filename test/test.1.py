import re

# a = 'H00048  Hepatocellular carcinoma [PATH:hsa05225 hsa05203 hsa05161 hsa05160 hsa05206]'
a = 'H00048  Hepatocellular carcinoma '
pattern = re.compile(r'H\d+(.*?)(\[.*\]{0,1})')
b = pattern.search(a).group(1)
print(b)