# -*- coding:utf-8 -*-


"""

@author: Jan
@file: shenzhen_scoreline.py.py
@time: 2019/6/26 18:58
"""
from bs4 import BeautifulSoup
import requests

if __name__ == '__main__':
    url = 'https://gkcx.eol.cn/school/284/specialtyline?cid=0'
    str_html = requests.get(url)


    soup = BeautifulSoup(str_html.text, 'lxml')
    print(str_html)
    table = soup.select(".scoreLine-table > table > tbody > tr")
    for t in table:
        print(t)
