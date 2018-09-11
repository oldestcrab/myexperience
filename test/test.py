import sys
import os
print(sys.path[0])
print(os.getcwd())

dir  = sys.path[0] + '/aa.txt'
if not os.path.exists(dir):
    with open(dir, 'w', encoding = 'utf-8'):
        pass
with open(dir, 'r+', encoding = 'utf-8') as f:
    print(f.readline())