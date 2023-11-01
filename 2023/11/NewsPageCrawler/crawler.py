# 引入re模块 正则表达式提取时间
import re

# 引入requests用于发送http请求 下载网页源码
import requests

# 引入fake_useragent用于生成随机User-Agent 以实现反反爬
from fake_useragent import UserAgent

# 引入BeautifulSoup用于解析网页源码
from bs4 import BeautifulSoup

# 引入pandas用于处理并保存数据到Excel
import pandas as pd

# 此爬虫爬取天津理工大学的某个新闻板块内容：https://news.tjut.edu.cn/yw1.htm
# 并逐一爬取每个新闻详情页中的标题、时间、配图
# 最后将数据保存到Excel中
main_page_url = 'https://news.tjut.edu.cn/yw1.htm'

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"zh-CN,zh;q=0.9",
    "User-Agent": UserAgent().random
}

# 发送http请求，获取网页源码
response = requests.get(main_page_url, headers=headers, timeout=10)

response.encoding = "utf-8"

# 解析网页源码
main_page_soup = BeautifulSoup(response.text, 'html.parser')

# 获取新闻列表元素
main_page_news_list = main_page_soup.select_one("#main > div.page2.box > div.w720.fl > table")

# 提取所有tr元素
trs = main_page_news_list.select("tr")

# print(["### {}".format(tr) for tr in trs])

# 删除分割线, 只保留id为line开头的tr元素, 这些才是新闻标题
filtered_trs = []

for tr in trs:
    if tr is not None and tr.get("id") is not None and tr.get("id").startswith("line"):
        filtered_trs.append(tr)

# print(["### {}".format(tr) for tr in filtered_trs])
print("新闻条数：", len(filtered_trs))

# 爬取每个新闻详情页的标题、时间、配图
news_list = []
"""
数据结构:
[
    {
        "title": "xxx",
        "time": "xxx",
        "images: [
            "xxx",
            "xxx"
        ]
    }
]
"""

root_url = "https://news.tjut.edu.cn/"

for tr in filtered_trs:

    # 获取tr内td元素
    tds = tr.select("td")

    if tds is None or len(tds) < 4:
        continue

    # 获取新闻详情页url
    detail_url = root_url + tds[1].select_one("a").get("href")

    # print(detail_url)

    # 发送http请求，获取网页源码
    response = requests.get(detail_url, headers=headers, timeout=10)

    response.encoding = "utf-8"

    # 解析网页源码
    detail_page_soup = BeautifulSoup(response.text, 'html.parser')

    # 获取新闻标题
    title = detail_page_soup.find("div", class_="main_contit").select_one("h1").text

    # 获取新闻时间
    sub_title = detail_page_soup.find("div", class_="main_contit").select_one("div").text
    time_str = re.findall(r"\d{4}-\d{2}-\d{2}", sub_title)[0]

    # 获取新闻配图
    imgs_elements = detail_page_soup.find("div", class_="main_conDiv").select("img")

    imgs = []

    for img_element in imgs_elements:
        imgs.append(root_url+img_element.get("src"))

    news_list.append({
        "title": title,
        "time": time_str,
        "images": imgs
    })

print(news_list)

# 初始化pandas的DataFrame
df = pd.DataFrame(columns=['新闻标题', '发布日期'])

# 遍历每一条新闻数据
for new in news_list:
    data = {
        '新闻标题': [new['title']],
        '发布日期': [new['time']]
    }

    # 插入每一个图片链接
    for i in range(len(new['images'])):
        data['图片链接{}'.format(i+1)] = [new['images'][i]]

    # 将每一条新闻数据转换为DataFrame
    df = pd.concat([df, pd.DataFrame(data)])

# 保存数据到Excel
df.to_excel('news.xlsx', index=False)