a = [1,2,3,'sdgsd','sdgdgdffgdf',34]
for i in a:
    try:
        i +=1
        print(i)
    except:
        print('错了')
        break