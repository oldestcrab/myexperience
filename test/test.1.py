# -*- coding:utf-8 -*-

a = [1,'',2,'',3]
print(len(a))
for i in range(len(a)):
    if not a[i] :
        print('get')
        a[i] = 1
print(a)
