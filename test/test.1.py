import json
import sys
a = [ 1, '23', '小红', '小明']
with open(sys.path[0] + '/123.json', 'w', encoding = 'utf-8') as f:
    f.write(json.dumps(a, indent = 2, ensure_ascii= False))
b = json.load(open(sys.path[0] + '/123.json', 'r', encoding = 'utf-8'))
print(b)