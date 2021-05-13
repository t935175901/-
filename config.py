import datetime
import re
import os
import time
from openpyxl import workbook  # 写入Excel表所用
pool_size=1
#线程池大小

today = datetime.date.today()
since = today-datetime.timedelta(days=1)
now=datetime.datetime.now()
#统计开始结束时间
datadir=["India",'Singapore']
#数据文件夹
update_interval=60*10
#相似系数,手动测试估计
similarity=0.44
#url正则
url_extract=re.compile(r"https?://[^\s]+\w\s?")
#去掉回车
huiche=re.compile(r'\n[\n]?')



#记录新闻来源twitterid及网址
india_sources={'PTI_News':{'name':'Press Trust of India','url':'http://www.ptinews.com/'},
               'timesofindia':{'name':'The Times Of India','url':'http://timesofindia.indiatimes.com/'},
               'IndianExpress':{'name':'The Indian Express','url':'https://indianexpress.com/'}}

def get_twitter_user_name(page_url: str) -> str:
    """提取Twitter的账号用户名称
    主要用于从Twitter任意账号页的Url中提取账号用户名称
    :param page_url: Twitter任意账号页的Url
    :return: Twitter账号用户名称
    """
    if pattern := re.search(r"(?<=twitter.com/)[^/]+", page_url):
        return pattern.group()
    return page_url


import re
from bs4 import BeautifulSoup as BS




