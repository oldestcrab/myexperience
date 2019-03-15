# -*- coding:utf-8 -*-

from Bio import Entrez

# 指定邮箱，有问题时会发送信息到该邮箱
Entrez.email = '18819425701@163.com'
# term = 'breast cancer OR biomarkers OR diagnosis OR prognosis OR drug response AND english[lang] AND human[word] AND Free full text[filt]'
# 603 13
# term = '"breast cancer" AND "biomarker" AND "prognosis" AND ("diagnosis"[tw] OR "biomarker"[tw] OR "prognosis"[tw] OR "drug response"[tw]) AND Humans[Mesh] AND english[Language] AND full text[sb]'
# 412 11
# term = '"breast cancer"[title] AND "biomarker" AND "prognosis" AND ("diagnosis"[tw] OR "biomarker"[tw] OR "prognosis"[tw] OR "drug response"[tw]) AND Humans[Mesh] AND english[Language] AND full text[sb]'
# 27 10
term = '"breast cancer"[tiab]  AND Humans[Mesh] AND english[Language] AND full text[sb] AND hasabstract[text] AND ("2009"[Publication Date] : "2014"[Publication Date]) '
term = term + ' AND (Journal Article[ptyp] OR  Clinical Trial[ptyp])'
# 53111 16
term = term + 'AND ("biomarker" OR "prognosis" ) '
# term = term + 'AND ("biomarker"[tw] AND "prognosis"[tw]) AND Clinical Trial[ptyp] '
# 获取检索句柄，db=数据库，term=检索条件, retmax=返回的id条数， datetype=日期类型，pdat为出版日期，maxdate,mindate=时间范围
# handle = Entrez.esearch(db='pubmed', term=term, retmax=50, datetype='pdat', mindate='2009', maxdate='2014')
handle = Entrez.esearch(db='pubmed', term=term, retmax=380020)
# 读取信息
info = Entrez.read(handle)
# print(info)
count = []
my_idlist = ['19118060', '23860928', '23744760', '24220913', '23868472', '18941892', '24012693', '24122389', '23970015', '20716629', '24186057', '23612454', '22544540', '21898387', '23490655', '23047592']
print(info['Count'])
for uid in info['IdList']:
    if uid in my_idlist:
        # print(uid, '在范围内')
        count.append(uid)
print('共有', len(count))
for i in my_idlist:
    if i not in count:
        print(i, '不在')
