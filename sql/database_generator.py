# -*- coding:utf-8 -*-


"""

@author: Jan
@file: database_generator.py
@time: 2019/6/17 1:19
"""

import pymysql
import os

if __name__ == '__main__':
    # ### 02
    # goto mysql and create a new database
    '''
    # CREATE DATABASE MINIBOOKHOUSE;
    # USE MINIBOOKHOUSE;
    '''

    # ### 01
    connection = pymysql.connect(
        host="127.0.0.1",
        port=3306,
        user='root',
        password='Winer20Chopin@',
        database='minibookhouse'
    )

    # ### 02
    # drop all the tables

    sql_del = '''drop table if exists usr'''
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql_del)
    cursor.close()
    print('Successfully delete table \'USR\'!')

    sql_del = '''drop table if exists voice'''
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql_del)
    cursor.close()
    print('Successfully delete table \'VOICE\'!')

    sql_del = '''drop table if exists article'''
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql_del)
    cursor.close()
    print('Successfully delete table \'ARTICLE\'!')

    sql_del = '''drop table if exists biu'''
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql_del)
    cursor.close()
    print('Successfully delete table \'BIU\'!')

    sql_del = '''drop table if exists temp'''
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql_del)
    cursor.close()
    print('Successfully delete table \'TEMP\'!')

    # ### 03
    # create table
    sql_usr = """create table usr(
    id int primary key auto_increment,
    new_biu int not null default 0,
    new_mess int not null default 0,
    score int not null default 0,
    
    openid char(30) not null,
    edge int default 0,
    sex enum('male', 'female') default 'male',
    pen_name char(20),
    signature char(200)
    )
    """

    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql_usr)
    cursor.close()
    print("Successfully create table \'USR\'!")


    sql_voi = """create table voice(
    id int primary key auto_increment,
    usr_id char(30) not null,
    
    num_biu int not null default 0,
    
    new_flag boolean default true
    )
    """
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql_voi)
    cursor.close()
    print("Successfully create table \'VOICE\'!")

    sql_tmp = """create table temp(
    id int primary  key auto_increment,
    usr_id char(30) not null,
    num char(6) ,
    category enum('audio', 'article') default 'article',
    state enum('checked', 'unchecked') default 'unchecked',
    res enum('pass', 'reject') default 'reject'
    )"""
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql_tmp)
    cursor.close()
    print("Successfully create table \'TEMP\'!")

    sql_art = """create table article(
    id int primary key auto_increment,
    usr_id char(30) not null,
    
    num_biu int not null default 0,
    new_flag boolean default true
    )
        """
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql_art)
    cursor.close()
    print("Successfully create table \'ARTICLE\'!")


    sql_biu = """create table biu(
    id int primary key auto_increment,
    from_usr_id int not null,
    to_usr_id int not null,
    work_type enum('article', 'audio') default 'article',
    new_flag boolean default true
    )
    """
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql_biu)
    cursor.close()
    print("Successfully create table \'BIU\'!")

    # ### 04
    # end.

