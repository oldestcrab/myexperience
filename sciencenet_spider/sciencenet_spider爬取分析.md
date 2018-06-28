### 目标
利用 Selenium 抓取科学网生命科学分类下的论文以及新闻部分，并用正则表达式通过解析索引页文章标题以及链接，得到文章的具体内容信息，并保存。

### 分析
通过requests模拟post请求的话比较繁琐，难以分析参数，所以选择使用python的selenium模块以及Phantomjs模拟浏览器请求，获取真正的相应页面。
#### 索引页分析
捉取入口链接为：
```python
# 论文链接
#url = 'http://paper.sciencenet.cn/paper/fieldlist.aspx?id=2'
# 领域新闻链接
url = 'http://news.sciencenet.cn/fieldlist.aspx?id=3'
```
![](http://ww1.sinaimg.cn/mw690/e2528559gy1fspodp08vlj20vq0qhqa0.jpg)
对于该页面，不管你点击第几页，它的url都是不变的。如果想要分页的话，不过在页面下方有一个分页导航，包括前 10页的链接，也包括下一页的链接，同时还有一个输入任意页码跳转的链接，如下图：

![](http://ww1.sinaimg.cn/large/e2528559gy1fspoimilegj20um02baac.jpg)

可以看到，一共有612页，我们要获取每一页的内容，只需要将页码从 1 到612页顺次遍历即可，页码数是确定的。所以在这里我们可以直接在页面跳转文本框中输入要跳转的页码，然后点击确定按钮跳转即可到达页码对应的页面。
当我们成功加载出某一页时，利用 Selenium 即可获取页面源代码，然后我们再用lxml解析库解析,获取文章的详细链接。

#### 索引页获取
```
http://news.sciencenet.cn/fieldlist.aspx?id=3
```
用 Selenium 进行抓取上面url，通过以下方法抓取索引页：
```python
# -*- coding:utf-8 -*-

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from lxml import etree

browser = webdriver.PhantomJS(executable_path=r'C:/Users/CRAB/Desktop/mybooks/execute/phantomjs-2.1.1-windows/bin/phantomjs.exe')
wait = WebDriverWait(browser, 10)

def index_page(page, judge):
    print('正在爬取第', page, '页索引页')
    try:
        url = 'http://news.sciencenet.cn/fieldlist.aspx?id=3'
        browser.get(url)
        if page > 1:
            input = wait.until(
                EC.presence_of_element_located((By.NAME, 'AspNetPager1_input')))
            submit = wait.until(
                EC.element_to_be_clickable((By.NAME, 'AspNetPager1')))
            input.clear()
            input.send_keys(page)
            submit.click()
        wait.until(EC.text_to_be_present_in_element_value((By.NAME, 'AspNetPager1_input'), str(page)))
        return get_products(page, judge)
    except TimeoutException:
        print('爬取第', page, '页索引页time out,尝试重新爬取!')
        index_page(page, judge)
```
通过构造一个 WebDriver 对象，使用无界浏览器 phantomjs，然后定义一个 get_index() 方法，用于抓取索引页。
在该方法里我们首先访问了这个链接，然后判断了当前的页码，如果大于 1 ，那就进行跳页操作，然后等待页面跳转完成。
等待加载指定为最长 10 秒。如果在这个时间内成功匹配了等待条件，那就立即返回相应结果并继续向下执行，否则到了最大等待时间还没有加载出来就直接抛出超时异常。
判断是否加载以及跳页完成，可以通过判断当前高亮的页码数是当前的页码数即可，如下：
![](http://ww1.sinaimg.cn/large/e2528559gy1fspoimilegj20um02baac.jpg)
所以在这里使用等待条件:
```
text_to_be_present_in_element_value((By.NAME, 'AspNetPager1_input'), str(page))
```
通过判断高亮页码节点对应的页码数是否与我们传递过去的参数相等，如果是，那就证明页面成功跳转到了这一页，页面跳转成功。
然后通过 get_pages() 方法进行页面解析。

#### 解析索引页文章url以及保存文章
获取页面源代码，然后用 lxml 进行解析，实现如下：
```python
def get_pages(page, judge):
    """
    提取文章内容
    :param page: 页码
    :param judge: 用于判断上次爬取位置
    """
    html = browser.page_source
    result = etree.HTML(html)
    items = result.xpath('//*[@id="DataGrid1"]/tbody//tbody')
    if page == 1:
        #领域新闻为 @width = "60%" ， 论文为 @width = "70%"
        next_judge = items[0].xpath('.//td[@width = "60%"]/a/@href')[0]
        with open('sciencenet_spider/judge.text', 'w', encoding = 'utf-8') as f:
            print(next_judge)
            f.write(next_judge)
    for item in items:
        kw = item.xpath('.//td[@width = "60%"]/a/@href')[0]
        if kw == judge:
            print("爬取到上次爬取位置，结束爬取！")
            return 1
            break
        url = 'http://paper.sciencenet.cn' + kw
        #/htmlpaper/201861510484322846535.shtm
        filename_pattern = re.compile('[a-zA-Z./]')
        filename = filename_pattern.sub('', kw)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
        }
        response = requests.get(url, headers = headers)
        response.encoding = 'utf-8'
        time.sleep(2)
        detail_pattern = re.compile(r'<table id="content".*<!-- JiaThis Button END -->.*?</table>',re.S)
        detail_result = detail_pattern.search(response.text)        
        save_page(detail_result, filename)
        print('保存第', page, '页索引页所有文章成功') 

```
调用 page_source 属性获取了页码的源代码，然后构造 lxml 解析对象，通过
```
items = result.xpath('//*[@id="DataGrid1"]/tbody//tbody')
```
获取具体文章的url所在的list,用 for 循环提取每个文章列表节点内部的url，通过组合得到每个文章的真正url。并提取url中的数字，作为保存的数据文件名，然后通过save_page方法保存内容。
```python
def save_page(result, filename):
    """
    保存到文件
    :param result: 结果
    :param filename: 保存的文件名
    """
    full_filename = './sciencenet_spider/sciencenet_spider_result/' + filename + '.html'
    with open(full_filename, 'w', encoding = 'utf-8') as f:
        f.write(result.group())
    #print('文件' + full_filename + '保存成功')    
```
#### 判断上次爬取位置
判断爬取的文章是否已进行过爬取，通过引入一个值进行对比，每次脚本进行爬取时，都会把当前爬取的第一个文章的url写入文件next_judge。
```python
if page == 1:
    #领域新闻为 @width = "60%" ， 论文为 @width = "60%"
    next_judge = items[0].xpath('.//td[@width = "60%"]/a/@href')[0]
    with open('sciencenet_spider/judge.text', 'w', encoding = 'utf-8') as f:
        print(next_judge)
        f.write(next_judge)
```
然后在下一次脚本爬取时，先读取这个文件，获得一个字符串，把这个字符串与每次获取的文章url进行对比，如果相等，就break，退出循环，结束爬取。
首先在爬取开始时读取上次爬取保存的字符串：
```python
with open('sciencenet_spider/judge.text', 'r', encoding = 'utf-8') as f:
    judge = f.read()
for i in range(1, 4):
    params = index_page(i, judge)
    if params == 1:
        break
```
通过传递参数judge,在get_pages方法中进行判断，如果相等，就退出循环，返回1,爬取脚本判断`params == 1`,脚本退出。
```python
if kw == judge:
    print("爬取到上次爬取位置，结束爬取！")
    return 1
    break
```