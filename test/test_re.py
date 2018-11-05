import re

text = 'https://ve.media.tumblr.com/tumblr_pg205dxF8G1xthtef.mp4'

pattern_search = re.compile(r'.*(\.mp4)', re.I)
result_serach = pattern_search.search(text)
result_serach = result_serach
if result_serach:
    print(type(result_serach.group()), result_serach.group())
else:
    print(type(result_serach))



'''
source_local = '
<p><img src="./img/Q3mGfKnoUwySqT6TvXpUT0m5xmhzAK01B6tlwq3h.jpeg" /></p><p>主要工作职责：</p><ul><li> 协助进行市场推广活动的前期准备工作；<li> 协助市场部收集和整理各种资料和文件；<li> 协助管理分发部门资料库、礼品库；<li> 协助产品资料的翻译及广审流程并归档；<li> 部门安排的其他工作。<p>基本要求：</p><ul><li>1. 可随时上岗者或每周能保证三天工作时间者优先考虑；<li> 善于与人沟通，具有良好的时间管理安排能力，能够随机应变处理突发状况；<li> 工作需勤快且仔细，认真负责，思维活跃；<li> 熟悉使用 MS Office 及具备一定的网络搜索能力；<li> 本科及以上学历，医学、药学、生物相关学科；<li> 良好的中文 / 英语书面表达能力；<li> 工作地点：申长路 900 号虹桥天地 2 号楼；工作环境舒适，部门员工 nice。<p>薪资：</p><ul><li> 税前本科生 130/ 天，硕士生 150/ 天，博士生 190/ 天。<p><font> 点击此链接，投递简历 </p><p></p><p> 更多精彩活动推荐，扫码即可参加，免费礼品，拿到手软！</p><p><img src="./img/Z1XTgJOxt0WSeUg6kNVu3JqXn9vZcW1qOQdxyaKl.png" /></p></content>
</Document>
'
def article_change(match):

#     匹配文章内容中的标签（a、img）除外，剔除其中的样式

    # <p src="./img/13SsuHuXECVJ<p style="text-align: center;"> p
    # print(match.group(),match.group(1))
    name_tag = ''
    return name_tag

pattren_article_change = re.compile(r'<([^aip]).*?>{1}')
source_local = pattren_article_change.sub(article_change, source_local)
print(source_local)
'''