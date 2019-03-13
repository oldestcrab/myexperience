# -*- coding:utf-8 -*-

from Bio import Entrez

# 指定邮箱，有问题时会发送信息到该邮箱
Entrez.email = '18819425701@163.com'
# 检索关键词 english[lang]语言
# diagnostic performance, prognosis and drug response[]
# term = 'breast cancer AND biomarkers AND diagnosis AND prognosis AND response AND english[lang] AND Free full text[filt] AND human[tiab] '
term = '(breast cancer OR biomarkers OR diagnosis OR prognosis OR drug response AND english[lang] AND human[word] AND Free full text[filt]'
# einfo获取的["DbInfo"]["FieldList"]ESearch可用的 搜索值列表
'''
ALL, All Fields, All terms from all searchable fields
UID, UID, Unique number assigned to publication
FILT, Filter, Limits the records
TITL, Title, Words in title of publication
WORD, Text Word, Free text associated with publication
MESH, MeSH Terms, Medical Subject Headings assigned to publication
MAJR, MeSH Major Topic, MeSH terms of major importance to publication
AUTH, Author, Author(s) of publication
JOUR, Journal, Journal abbreviation of publication
AFFL, Affiliation, Author's institutional affiliation and address
ECNO, EC/RN Number, EC number for enzyme or CAS registry number
SUBS, Supplementary Concept, CAS chemical name or MEDLINE Substance Name
PDAT, Date - Publication, Date of publication
EDAT, Date - Entrez, Date publication first accessible through Entrez
VOL, Volume, Volume number of publication
PAGE, Pagination, Page number(s) of publication
PTYP, Publication Type, Type of publication (e.g., review)
LANG, Language, Language of publication
ISS, Issue, Issue number of publication
SUBH, MeSH Subheading, Additional specificity for MeSH term
SI, Secondary Source ID, Cross-reference from publication to other databases
MHDA, Date - MeSH, Date publication was indexed with MeSH terms
TIAB, Title/Abstract, Free text associated with Abstract/Title
OTRM, Other Term, Other terms associated with publication
INVR, Investigator, Investigator
COLN, Author - Corporate, Corporate Author of publication
CNTY, Place of Publication, Country of publication
PAPX, Pharmacological Action, MeSH pharmacological action pre-explosions
GRNT, Grant Number, NIH Grant Numbers
MDAT, Date - Modification, Date of last modification
CDAT, Date - Completion, Date of completion
PID, Publisher ID, Publisher ID
FAUT, Author - First, First Author of publication
FULL, Author - Full, Full Author Name(s) of publication
FINV, Investigator - Full, Full name of investigator
TT, Transliterated Title, Words in transliterated title of publication
LAUT, Author - Last, Last Author of publication
PPDT, Print Publication Date, Date of print publication
EPDT, Electronic Publication Date, Date of Electronic publication
LID, Location ID, ELocation ID
CRDT, Date - Create, Date publication first accessible through Entrez
BOOK, Book, ID of the book that contains the document
ED, Editor, Section's Editor
ISBN, ISBN, ISBN
PUBN, Publisher, Publisher's name
AUCL, Author Cluster ID, Author Cluster ID
EID, Extended PMID, Extended PMID
DSO, DSO, Additional text from the summary
AUID, Author - Identifier, Author Identifier
PS, Subject - Personal Name, Personal Name as Subject
COIS, Conflict of Interest Statements, Conflict of Interest Statements
'''
# 获取检索句柄，db=数据库，term=检索条件, retmax=返回的id条数， datetype=日期类型，pdat为出版日期，maxdate,mindate=时间范围
handle = Entrez.esearch(db='pubmed', term=term, retmax=50, datetype='pdat', mindate='2009', maxdate='2014')
# 读取信息
info = Entrez.read(handle)
# print(info)
print(info['Count'])
print(info['IdList'])


    