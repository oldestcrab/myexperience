import sys
import os
print(sys.path[0])
print(os.getcwd())
path_abs = sys.path[0]
a = path_abs+'/test.txt'
with open(a,'r', encoding = 'utf-8') as f:
    print(f.read())
print (a)