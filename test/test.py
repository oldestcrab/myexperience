import re
# /htmlpaper/201861510484322846535.shtm
#pattern = re.compile('[a-zA-Z./]')
patterns = re.compile('<img src="(.*?).jpg', re.S)
a = '''
<table id="content" style="border: solid 1px #bbc89b; width: 680px; text-align: center;

                                background-color: #f8f9f4">

                                <tr>

                                    <td align="left">

                                        <div style="height: 20px; margin: 0 auto; border-bottom: solid 1px #bbc89b; margin-top: 10px;

                                            width: 82%; font: 12px 宋体; float: left; ">

                                            作者：晋楠 来源：<a href="http://www.sciencenet.cn/dz/dznews_photo.aspx" class="highlight2">中国科学报</a> 发布时间：2018/6/20 9:18:03</div>

                                        <div style="height: 20px; margin: 0 auto; border-bottom: solid 1px #bbc89b; margin-top: 10px;

                                            width: 18%; font: 12px 宋体; float: right">

                                            选择字号：<span onclick="showsize(12)" style="background-color: #587c19; color: #fff;

                                                font-size: 12px; cursor: pointer">小</span> <span onclick="showsize(14)" style="background-color: #587c19;

                                                    color: #fff; font-size: 12px; cursor: pointer">中</span> <span onclick="showsize(16)"

                                                        style="background-color: #587c19; color: #fff; font-size: 12px; cursor: pointer">

                                                        大</span>

                                        </div>

                                    </td>

                                </tr>

                                <tr>

                                    <td align="center">

                                        <div id="content1" style=" padding:15px; text-align: left; line-height: 24px;

                                            word-wrap: break-word" class="f14">

                                            <table width="100%" border="0" cellspacing="0" cellpadding="0">

                                                <tr>

                                                    <td height="20">

                                                    </td>

                                                </tr>

                                                <tr>

                                                    <td align="center" valign="middle" class="style1" style="font-size: 13px; color: #333333;

                                                        font-family: 宋体; line-height: 20px">

                                                        <b></b></td>

                                                </tr>

                                                <tr>

                                                    <td align="center" class="style1" style="font-size: 22px; color: #587c19; font-family: 黑体;

                                                        line-height: 30px">

                                                        世界杯期间俄生化学家“被放假”</td>

                                                </tr>

                                                <tr>

                                                    <td align="center" valign="middle" class="style1" style="font-size: 13px; color: #333333;

                                                        font-family: 宋体; line-height: 20px">

                                                        <b></b></td>

                                                </tr>

                                            </table>

                                            <br />

<p align="center">

	<img src="/upload/news/images/2018/6/2018620530352120.jpg" /></p>

<p>

	&nbsp;</p>

<p style="text-indent: 2em; text-align: center">

	世界杯前采取的安保措施对一些俄罗斯科学家产生了影响。<strong>图片来源： Olga Maltseva/AFP</strong></p>

<p style="text-indent: 2em">

	全世界足球迷都在关注世界杯。而一些俄罗斯研究人员发现他们看比赛的时间比自己预期的要多。</p>

<p style="text-indent: 2em">

	《自然》杂志采访了俄罗斯相关分子生物学家和生物化学家，他们表示，由于该国政府在世界杯前采取的安全和反恐措施，一些俄罗斯实验室无法获得其迫切需要的放射性试剂。</p>

<p style="text-indent: 2em">

	在5月11日发布的总统令中，俄罗斯政府以安全考虑为由，将危险化学和生物物质（包括有毒和放射性化学物质）的销售和运输暂停两个月。世界杯将持续到7月15日。莫斯科附近斯科尔科沃科技学院生物化学家Konstantin Severinov表示，该法令仅适用于举办比赛的城市，但包括莫斯科在内的许多城市恰好是研究中心。</p>

<p style="text-indent: 2em">

	Severinov说，这些措施可能会阻碍俄罗斯相对较少的分子生物学研究。今年5月下了放射性核甘酸（用于测量基因表达和其他实验）订单的俄罗斯研究人员接到了来自莫斯科俄罗斯科学院有机化学研究所的坏消息：因为法令要求，预计6月交付给他们实验室的供给品将被取消。而俄罗斯其他研究中心不能提供这种试剂。</p>

<p style="text-indent: 2em">

	&ldquo;这让我的实验室的整个工作处于困境。&rdquo;同时担任莫斯科俄罗斯科学院分子遗传学和基因生物学研究所课题组长的Severinov说。他表示，包括CRISPR-Cas9基因编辑实验和测量毒素对细胞影响的许多项目都受到了影响。</p>

<p style="text-indent: 2em">

	圣彼得堡杜布赞斯基基因组生物信息学中心主任Stephen O &rsquo;Brien说，他所在团队的工作主要涉及计算，因此并未受到影响。但他从其他研究所的同事那里听说，他们在获得放射性试剂和其他有毒化学物质方面遇到了困难<strong>。（晋楠）</strong></p>

<div style="text-indent:2em;color: #587c19">

	《中国科学报》 (2018-06-20 第3版 国际)</div>



                                           

                                            <div style="border-bottom: solid 1px #bfc89d; vertical-align: bottom; width: 100%;

                                                height: 20px">

                                            </div>

                                            <div style="width: 100%; height: 20px; text-align: center; margin:10px">

                                            <!-- JiaThis Button BEGIN -->

<script src="/html/js/share.js" type="text/javascript"></script>

<!-- JiaThis Button END -->

                                            </div>

                                            

                                        </div>

                                    </td>

                                </tr>



                            </table>'''
j = re.compile('<img src="(.*?).jpg"', re.S)
img_findall = j.findall(a)
print(img_findall)

def test(match):
    #print(match.group(0))
    #print(match.group(1))
    pattern = re.compile('[a-zA-Z/]')
    c = pattern.sub('', match.group(1))
    d = '<img src="./img/' + c
    print(d)
    return d
b = patterns.sub(test, a)

#print(b.group(1))
#print(b)


