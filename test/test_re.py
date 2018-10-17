import re

text = '''
        来源：中国科学报
        发布者：ailsa
        日期：2018-08-31
'''

pattern_search = re.compile(r'来源：(.*?)发布者：', re.I|re.S)
result_serach = pattern_search.search(text)
result_serach = result_serach.group(1)
print(type(result_serach), result_serach)