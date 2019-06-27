# -*- coding:utf-8 -*-


"""

@author: Jan
@file: table_updating.py
@time: 2019/6/25 9:25
"""

import pymysql
import os

connection = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user='root',
    password='Winer20Chopin@',
    database='minibookhouse',
    charset='utf8'
)
"""
sql = "alter table temp add column new_flag boolean default True not null;"
cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
cursor.execute(sql)
cursor.close()

sql = "alter table temp add column num_biu int default 0 not null;"
cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
cursor.execute(sql)
cursor.close()

sql = "alter table temp add column title char(100);"
cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
cursor.execute(sql)
cursor.close()
"""

### to add title
sql_1 = "select * from temp;"
cursor1 = connection.cursor(cursor=pymysql.cursors.DictCursor)

data = ''
try:
    cursor1.execute(sql_1)
    data = cursor1.fetchall()
    print(len(data))
except:
    connection.rollback()
cursor1.close()

for d in data:
    print(d)
    category = d['category']
    usr_id = d['usr_id']
    count = d['num']

    if category == 'article':
        pth = os.path.join(os.getcwd(), 'static', 'Users', usr_id, 'Articles', count, 'article.txt')
        fh = open(pth, 'r', encoding='utf-8')
        title = fh.readlines()[0][:-1]
        print(title)
        fh.close()
    else:
        pth = os.path.join(os.getcwd(), 'static', 'Users', usr_id, 'Audios', count)
        fh = open(os.path.join(pth, 'title'), 'r', encoding='utf-8')
        title = fh.read()
        print(title)
        fh.close()
    args = (title, usr_id, category, count)
    sql_2 = "update temp set title=%s where usr_id=%s and category=%s and num=%s;"
    cursor2 = connection.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor2.execute(sql_2, args)
        connection.commit()
        print("Successful!")
    except:
        connection.rollback()
    cursor2.close()