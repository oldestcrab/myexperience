import pymysql
import sys
import time

print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
with open(sys.path[0] + '/list_kw.txt', 'r', encoding = 'utf-8') as f:
    list_kw = f.readlines()

db = pymysql.connect(host='localhost', user='bmnars', password='vi93nwYV', port=3306, db='bmnars')
cursor = db.cursor()
update_time = time.strftime('%Y-%m-%d',time.localtime())

for i in list_kw:
    i = i.strip()
    data = {
        'kw':i,
	    'update_time':update_time
    }
    table = '_cs_bmnars_vigenebio_kw'
    keys = ','.join(data.keys())
    values = ','.join(['%s']*len(data))
    sql = 'INSERT INTO {table}({keys}) VALUES ({values}) on duplicate key update '.format(table=table, keys=keys, values=values)
    update = ', '.join(['{key} = %s'.format(key=key) for key in data]) + ';'
    sql += update
    # print(sql)
    try:
        if cursor.execute(sql,tuple(data.values())*2):
            db.commit()
    except:
        print("import_mysql_failed:")
        db.rollback()

cursor.close()      
db.close()
print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))