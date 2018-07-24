from lxml import etree
html ='''
<div>
    <ul>
         <li class="item-0"><a href="link1.html">first item</a></li>
         <li class="item-1"><a href="link2.html">second item</a></li>
         <li class="item-inactive"><a href="link3.html">third item</a></li>
         <li class="item-1"><a href="link4.html">fourth item</a></li>
         <li class="item-0"><a href="link5.html">fifth item</a> # 注意，此处缺少一个 </li> 闭合标签
     </ul>
 </div>
'''

result = etree.HTML(html)
#a = etree.tostring(result)
#print(a)
#print(type(result))
# 获取索引页文章列表内容
b = 'link1.html'
items = result.xpath('//li/a[@href="'+b+'"]')
print(items[0].text)
'''
# 写入当前爬取到的第一个文章url：/htmlpaper/2018625148872046611.shtm
#if page == 1:
#    # 领域新闻为 @width = "60%" ，
#    # next_judge = items[0].xpath('.//td[@width = "60%"]/a/@href')[0]
#    # 论文为 @width = "70%"
#    next_judge = items[0].xpath('.//td[@width = "70%"]/a/@href')[0]
#    with open('sciencenet_spider/judge.txt', 'w', encoding = 'utf-8') as f:
#        print("next_judge:\t" + next_judge)
#        f.write(next_judge)
## 提取每一个文章的url
print('asldgs')
for item in items:
    # 领域新闻为 @width = "60%" ，
    # kw = item.xpath('.//td[@width = "60%"]/a/@href')[0]
    # 论文为 @width = "70%"
    kw = item.xpath('.//td[@width = "60%"]/a/@href')[0]
   ##title = item.xpath('.//td[@width = "60%"]/a')[0].text.replace('\n','').replace(' ','')
   ## 判断是否爬取到上次爬取位置，是的话返回1
   #if kw == judge:
   #    print("已爬取到上次爬取位置！")
   #    return 1
   #    break
   ## 组合url
    print('as')
    url = 'http://paper.sciencenet.cn' + kw
    print(url)
    #/htmlpaper/201861510484322846535.shtm
    # 提取url中的数字作为文件名保存
    '''