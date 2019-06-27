# -*- coding:utf-8 -*-


"""

@author: Jan
@file: main.py.py
@time: 2019/6/17 1:19
"""

from flask import Flask, request, render_template, redirect, url_for
import simplejson
import os
import time
import pymysql
import urllib
import shutil
import json
import base64


connection = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user='root',
    password='Winer20Chopin@',
    database='minibookhouse',
    charset='utf8'
)

app = Flask(__name__)

# ### user register
@app.route('/Mini_Bookhouse/register_usr', methods=['POST', 'GET'])
def register_usr():
    state = 0
    '''
    0 - nothing
    1 - successfully registered
    2 - registered already
    '''
    usr_openid = json.loads(request.values.get('usr_openid'))
    sex = json.loads(request.values.get('gender'))
    # print(sex)
    # print(usr_openid)
    if int(sex) == 1:
        sex = 'male'
    else:
        sex = 'female'
    args = (usr_openid, sex)
    sql_usr = "insert into usr (openid, sex) value (%s, %s)"
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql_usr, args)
        connection.commit()

        # mkdirs
        pth = os.path.join(os.getcwd(), 'static', 'Users', usr_openid)
        if os.path.exists(pth) is not True:
            os.mkdir(pth)
            os.mkdir(os.path.join(pth, 'Audios'))
            os.mkdir(os.path.join(pth, 'Articles'))
        state = 1
    except:
        connection.rollback()
        cursor("Fail to register!")
    cursor.close()

    return simplejson.dumps({
        'state': state
    })

@app.route('/Mini_Bookhouse/get_usr_info', methods=['POST', 'GET'])
def get_usr_info():
    state = 0
    usr_openid = json.loads(request.values.get('usr_openid'))

    score = 0
    new_biu = 0
    new_mess = 0
    pen_name = ''
    signature = ''

    # sql
    args = (usr_openid)
    sql_usr = "select * from usr where openid = %s;"
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql_usr, args)
        data = cursor.fetchall()
        if len(data) > 0:
            state = 1# successfully got it
            d = data[0]
            score = d['score']
            new_biu = d['new_biu']
            new_mess = d['new_mess']
            pen_name = d['pen_name']
            signature = d['signature']
            # print(d)
    except:
        connection.rollback()
    cursor.close()

    return simplejson.dumps({
        'state': state,
        'score': score,
        'new_biu': new_biu,
        'new_mess': new_mess,
        'pen_name': pen_name,
        'signature': signature
    })

@app.route('/Mini_Bookhouse/submit_usr_info', methods=['POST', 'GET'])
def submit_usr_info():
    state = -1

    openid = json.loads(request.values.get('openid'))
    pen_name = json.loads(request.values.get('pen_name'))
    signature = json.loads(request.values.get('signature'))

    args = (pen_name, signature, openid)
    sql_usr = "update usr set pen_name=%s, signature=%s where openid=%s"
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql_usr, args)
        connection.commit()
        state = 1
    except:
        connection.rollback()
    cursor.close()

    return simplejson.dumps({
        'state': state
    })

@app.route('/Mini_Bookhouse/upload_temp_audio', methods=['POST', 'GET'])
def upload_temp_audio():
    state = -1
    count = 0
    try:
        audio = request.files['audio']
        openid = request.values.get('openid')
        title = request.values.get('title')


        file_name = audio.filename
        ext = file_name.split('.')[-1]

        # save the audio and return the id
        audio_pth = os.path.join(os.getcwd(), 'static', 'Users', openid, 'Audios')
        count = len(os.listdir(audio_pth)) + 1
        audio_pth = os.path.join(audio_pth, '%06d'%count)
        # print(os.path.join(audio_pth, title+'.'+ext))
        os.mkdir(audio_pth)
        audio.save(os.path.join(audio_pth, 'audio.'+ext))

        t_pth = os.path.join(audio_pth, 'title')
        fh = open(t_pth, 'w')
        fh.write(title)
        fh.close()

        state = 1
    except:
        pass

    """
    <FileStorage: 'wxee12059dd125800a.o6zAJs2T5e796_VeTXam3mbBvJ2c.Krl5njUL3KHec3e14bbe1e347c8980d92f245e149ae4.durationTime=3274.mp3' ('audio/mpeg')>
    """
    return simplejson.dumps({
        'state': state,
        'count': count
    })

@app.route('/Mini_Bookhouse/upload_image_for_audio', methods=['POST', 'GET'])
def upload_image_for_audio():
    state = -1
    try:
        try:
            img = request.files['image']
        except:
            img = request.values.get('image')

        openid = request.values.get('openid')
        count = int(request.values.get('count'))
        title = request.values.get('title')

        if img == 'ori':
            img_pth = os.path.join(os.getcwd(), 'static', 'Users', openid, 'Audios', '%06d' % count)
            shutil.copyfile('default_img.png', os.path.join(img_pth, 'image.jpg'))
            pass
        else:
            file_name = img.filename
            ext = file_name.split('.')[-1]

            img_pth = os.path.join(os.getcwd(), 'static', 'Users', openid, 'Audios', '%06d'%count)
            img.save(os.path.join(img_pth, 'image.'+ext))
        state += 1
    except:
        pass
    if state == 0:
        # 新建一个记录，在temp中，等待审核
        args = (openid, "audio", '%06d'%count, title)
        sql_tmp = "INSERT INTO temp (usr_id, category, num, title) values (%s, %s, %s, %s);"

        cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
        try:
            cursor.execute(sql_tmp, args)
            connection.commit()
            state += 1
        except:
            connection.rollback()
            # insert fail, remove all the files
            files = os.listdir(img_pth)
            for file_ in files:
                os.remove(os.path.join(img_pth, file_))
            # os.remove(img_pth)

            print("Fail to register!")
        cursor.close()

    if state == 1:
        pass
        # ask the manager to check the new message
    return simplejson.dumps({
        'state': state,

    })

@app.route('/Mini_Bookhouse/upload_temp_article', methods=['POST', 'GET'])
def upload_temp_article():
    state = -1
    try:
        openid = request.values.get('usr_id')
        txt = request.values.get('txt')
        title = request.values.get('title')
        count = request.values.get('count')
        #print(openid)
        #print(count)

        pth = os.path.join(os.getcwd(), 'static', 'Users', openid, 'Articles', count)
        fh = open(os.path.join(pth, 'article.txt'), 'w', encoding='utf-8')
        fh.write(title+'\n')
        txt = json.loads(txt)

        for line in txt:
            #print(line)
            p_s = line.split("\n")
            for p in p_s:
                fh.write(p+'\n')
        fh.close()
        state += 1 # 0
    except:
        pass

    if state == 0:
        # 新建一个记录，在temp中，等待审核
        args = (openid, "article", count, title)
        sql_tmp = "INSERT INTO temp (usr_id, category, num, title) values (%s, %s, %s, %s);"

        cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
        try:
            cursor.execute(sql_tmp, args)
            connection.commit()
            state += 1
        except:
            connection.rollback()
            # insert fail, remove all the files
            files = os.listdir(pth)
            for file_ in files:
                os.remove(os.path.join(pth, file_))
            # os.remove(img_pth)

            print("Fail to register!")
        cursor.close()

    return simplejson.dumps({
        'state': state,
    })

@app.route('/Mini_Bookhouse/upload_image_for_article', methods=['POST', 'GET'])
def upload_image_for_article():
    state = -1

    usr_id = request.values.get('usr_id')
    try:
        img = request.files['image']
    except:
        img = request.values.get('image')
    title = request.values.get('title')
    txt = request.values.get('txt')
    try:

        pth = os.path.join(os.getcwd(), 'static', 'Users', usr_id, 'Articles')
        count = '%06d'%( len(os.listdir(pth)) )
        pth = os.path.join(pth, count)

        if os.path.exists(pth) is not True:
            os.mkdir(pth)

        if img == '../../src/default_img.png':
            shutil.copyfile('default_img.png', os.path.join(pth, 'image.jpg'))
        else:
            file_name = img.filename
            ext = file_name.split(".")[-1]
            img.save(os.path.join(pth, 'image.'+ext))
        state= 1
    except:
        pass

    return simplejson.dumps({
        'state': state,
        'count': count
    })

@app.route('/Mini_Bookhouse/get_propose', methods=['GET', 'POST'])
def get_propose():
    state = -1
    usr_id = request.values.get('usr_id')
    # print(usr_id)
    all_audios = []
    all_articles = []
    # new_audios = []
    # new_articles = []

    args = (usr_id, "pass", "checked")
    sql_tmp = "select * from temp where usr_id=%s and res=%s and state=%s;"
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql_tmp, args)
        data = cursor.fetchall()
        # print(len(data))
        # print(data[0])
        for d in data:
            if d['category'] == 'audio':
                all_audios.append(d)
            else:
                all_articles.append(d)

        state = 1
    except:
        connection.rollback()
    cursor.close()
    return simplejson.dumps({
        'state': state,
        'audios': all_audios,
        'articles': all_articles
    })

@app.route('/Mini_Bookhouse/get_public_propose', methods=['GET', 'POST'])
def get_public_propose():
    state = -1
    start_flag_aud = int(request.values.get('start_flag_aud'))
    start_flag_art = int(request.values.get('start_flag_art'))

    last_query_index_aud = -1
    last_query_index_art = -1
    cnt = -1
    """
    if start_flag == -1:
        # get the current max index of records
        sql_cnt = "select count(id) from temp;"
        cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
        try:
            cursor.execute(sql_cnt)
            cnt = cursor.fetchall()
            print(cnt[0]['count(id)'])
        except:
            connection.rollback()
        cursor.close()
        
        cnt
        arqs = (cnt, "pass")
        sql = "select * from temp where id>%d and res='%s'limit 0,10;"
        pass
    else:
        pass
    """
    articles = [] # ele for: pen_name, num_biu, image_base64, title, txts
    audios = []   # ele for: pen_name, num_biu, image_base64, title, audio
    sql_aud = "select * from temp where id>%d and res='%s' and category='%s' limit 0,1;"%(start_flag_aud, "pass", "audio")
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql_aud)
        data = cursor.fetchall()
        for d in data:
            dt = {}
            dt['id'] = d['id']
            dt['usr_id'] = d['usr_id']# for pen_name
            dt['num_biu'] = d['num_biu']
            dt['title'] = d['title']
            dt['count'] = d['num']# for resource
            last_query_index_aud = d['id']

            audios.append(dt)
        state = 0
    except:
        connection.rollback()
    cursor.close()

    sql_art = "select * from temp where id>%d and res='%s' and category='%s' limit 0,1;" % (start_flag_art, "pass", "article")
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql_art)
        data = cursor.fetchall()
        for d in data:
            dt = {}
            dt['id'] = d['id']
            dt['usr_id'] = d['usr_id']  # for pen_name
            dt['num_biu'] = d['num_biu']
            dt['title'] = d['title']
            dt['count'] = d['num']  # for resource
            last_query_index_art = d['id']

            articles.append(dt)
        state = 0
    except:
        connection.rollback()
    cursor.close()

    for i in range(len(articles)):
        art = articles[i]
        pth = os.path.join(os.getcwd(), 'static', 'Users', art['usr_id'], 'Articles', art['count'])
        # get pen_name
        name = "佚名"
        sql_pen = "select pen_name from usr where openid='%s';"%(art['usr_id'])
        cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
        try:
            cursor.execute(sql_pen)
            name = cursor.fetchall()[0]['pen_name']
            # print(name)
        except:
            connection.rollback()
        cursor.close()
        if name is not None:
            pen_name = name
        articles[i]['pen_name'] = pen_name

        # get txts
        txts = []
        fh = open(os.path.join(pth, 'article.txt'), 'r', encoding='utf-8')
        lines = fh.readlines()[1:]
        fh.close()
        for line in lines:
            txts.append(line[:-1])
        articles[i]['txts'] = txts

        # get image_base64
        files = os.listdir(pth)
        articles[i]['img'] = files[1]
        '''
        img_base64 = ''
        with open(os.path.join(pth, files[1]), "rb") as f:
            img_base64 = base64.b64encode(f.read())
        articles[i]['img'] = img_base64
        '''

        # articles[i]['count'] = articles[i]['usr_id'] = ''
    # print(articles)
    for i in range(len(audios)):
        aud = audios[i]
        pth = os.path.join(os.getcwd(), 'static', 'Users', aud['usr_id'], 'Audios', aud['count'])
        # get pen_name
        name = "佚名"
        sql_pen = "select pen_name from usr where openid='%s';"%(aud['usr_id'])
        cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
        try:
            cursor.execute(sql_pen)
            name = cursor.fetchall()[0]['pen_name']
            # print(name)
        except:
            connection.rollback()
        cursor.close()
        if name is not None:
            pen_name = name
        audios[i]['pen_name'] = pen_name

        # get audio
        files = os.listdir(pth)
        audios[i]['audio'] = files[0]

        # get image_base64
        audios[i]['img'] = files[1]
        '''
        img_base64 = ''
        with open(os.path.join(pth, files[1]), "rb") as f:
            img_base64 = base64.b64encode(f.read())
        audios[i]['img'] = img_base64
        '''
        # audios[i]['count'] = articles[i]['usr_id'] = ''
    # print(audios)
    state = 1
    return simplejson.dumps({
        'state': state,
        'last_query_index_aud': last_query_index_aud,
        'last_query_index_art': last_query_index_art,
        'articles': articles,
        'audios': audios
    })

@app.route('/Mini_Bookhouse/get_more_public_proposes', methods=['GET', 'POST'])
def get_more_public_proposes():
    state = -1
    start_flag = -1
    category = ''
    records = []

    start_flag = int(request.values.get('start_flag'))
    category = request.values.get("category")
    last_query_index = start_flag
    # print(last_query_index)

    sql_aud = "select * from temp where id>%d and res='%s' and category='%s' limit 0,1;" % (start_flag, "pass", category)
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql_aud)
        data = cursor.fetchall()
        if len(data) == 0:
            return simplejson.dumps({
                'state': state,
                'last_query_index': last_query_index,
                'records': records
            })
        for d in data:
            dt = {}
            dt['id'] = d['id']
            dt['usr_id'] = d['usr_id']  # for pen_name
            dt['num_biu'] = d['num_biu']
            dt['title'] = d['title']
            dt['count'] = d['num']  # for resource
            last_query_index = d['id']

            records.append(dt)
        state += 1# 0
    except:
        connection.rollback()
    cursor.close()

    if category == 'article':
        for i in range(len(records)):
            art = records[i]
            pth = os.path.join(os.getcwd(), 'static', 'Users', art['usr_id'], 'Articles', art['count'])
            # get pen_name
            name = "佚名"
            sql_pen = "select pen_name from usr where openid='%s';" % (art['usr_id'])
            cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
            try:
                cursor.execute(sql_pen)
                name = cursor.fetchall()[0]['pen_name']
                # print(name)
            except:
                connection.rollback()
            cursor.close()
            if name is not None:
                pen_name = name
            records[i]['pen_name'] = pen_name

            # get txts
            txts = []
            fh = open(os.path.join(pth, 'article.txt'), 'r', encoding='utf-8')
            lines = fh.readlines()[1:]
            fh.close()
            for line in lines:
                txts.append(line[:-1])
            records[i]['txts'] = txts
            # print(txts)

            # get image_base64
            files = os.listdir(pth)
            records[i]['img'] = files[1]
    else:
        # audio
        for i in range(len(records)):
            aud = records[i]
            pth = os.path.join(os.getcwd(), 'static', 'Users', aud['usr_id'], 'Audios', aud['count'])
            # get pen_name
            name = "佚名"
            sql_pen = "select pen_name from usr where openid='%s';" % (aud['usr_id'])
            cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
            try:
                cursor.execute(sql_pen)
                name = cursor.fetchall()[0]['pen_name']
                # print(name)
            except:
                connection.rollback()
            cursor.close()
            if name is not None:
                pen_name = name
            records[i]['pen_name'] = pen_name

            # get audio
            files = os.listdir(pth)
            records[i]['audio'] = files[0]

            # get image_base64
            records[i]['img'] = files[1]

    # print(last_query_index)
    return simplejson.dumps({
        'state': state,
        'last_query_index': last_query_index,
        'records': records
    })

@app.route('/Mini_Bookhouse/likeIT', methods=['GET', 'POST'])
def likeIT():
    state = -1
    id = request.values.get('id')
    id = int(id)

    sql_tmp = "update temp set num_biu=num_biu+1 where id=%d;"%id
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql_tmp)
        connection.commit()
        state = 1
    except:
        pass

    return simplejson.dumps({
        'state': state
    })

@app.route('/Mini_Bookhouse/update_new', methods=['GET', 'POST'])
def update_new():
    state = -1

    ids = request.values.get('ids')
    ids = json.loads(ids)
    # print(ids)
    for id in ids:
        id = int(id)
        sql_tmp = "update temp set new_flag=false where id=%d;"%id
        cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
        try:
            cursor.execute(sql_tmp)
            connection.commit()
            state = 1
        except:
            connection.rollback()
        cursor.close()

        
    return simplejson.dumps({
        'state': state,
    })

@app.route('/Mini_Bookhouse/get_txts', methods=['GET', 'POST'])
def get_txts():
    state = -1
    txts = []

    id = int(request.values.get("temp_id"))

    sql_tmp = "select * from temp where id=%d;"%id
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql_tmp)
        data  =cursor.fetchall()[0]
        # print(data)
        state = 1
    except:
        connection.rollback()
    cursor.close()

    if state == 1:
        pth = os.path.join(os.getcwd(), 'static', 'Users', data['usr_id'], 'Articles', data['num'], 'article.txt')
        fh = open(pth, 'r', encoding='utf-8')
        lines = fh.readlines()[1:]
        fh.close()
        for line in lines:
            txts.append(line[:-1])
    # print(txts)

    return simplejson.dumps({
        'state': state,
        'txts': txts
    })


# MANAGER # ##################################################################################### #
@app.route('/Mini_Bookhouse/manager')
def manager():
    response = render_template('index.html')
    return response

@app.route('/Mini_Bookhouse/manager/get_checking')
def get_checking():
    state = -1

    articles = []
    audios = []
    args = ("unchecked")
    sql_tmp = "select * from temp where state=%s;"
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)

    try:
        cursor.execute(sql_tmp, args)
        data = cursor.fetchall()
        for i in range(len(data)):
            sample = {}
            sample["usr_id"] = data[i]["usr_id"]
            sample['dir'] = data[i]["num"]

            if data[i]["category"] == 'audio':
                audios.append(sample)
            else:
                articles.append(sample)
        state = 1
    except:
        pass
    cursor.close()

    return simplejson.dumps({
        'state': state,
        'articles': articles,
        'audios': audios
    })

@app.route('/Mini_Bookhouse/manager/checking_audio_detail')
def checking_audio_detail():
    state = -1
    return redirect(url_for('audio_detail'))
    return "audio_detail"

@app.route('/Mini_Bookhouse/manager/audio_detail')
def audio_detail():
    usr_id = request.args.get("usr_id")
    dir_ = request.args.get("dir")
    print(usr_id)
    print(dir_)

    response = render_template('audio_detail.html')

    return response

@app.route('/Mini_Bookhouse/manager/article_detail')
def article_detail():
    response = render_template('article_detail.html')
    return response

@app.route('/Mini_Bookhouse/manager/get_title')
def get_title():
    files = []
    title = ''

    usr_id = request.args.get("usr_id")
    dir_ = request.args.get("dir")
    category = request.args.get("category")

    pth = os.path.join(os.getcwd(), 'static', 'Users', usr_id, category, dir_)
    # print(pth)
    if os.path.exists(pth):
        files = os.listdir(pth)

    fh = open(os.path.join(pth, 'title'), 'r')
    title = fh.read()
    # print(title)
    fh.close()

    return simplejson.dumps({
        'files': files,
        'title': title
    })

@app.route('/Mini_Bookhouse/manager/get_article_checking')
def get_article_checking():
    state = -1
    img = ''
    txts = []
    title = ''

    usr_id = request.args.get("usr_id")
    dir_ = request.args.get("dir")
    category = request.args.get("category")
    pth = os.path.join(os.getcwd(), 'static', 'Users', usr_id, category, dir_)

    files = os.listdir(pth)
    img = files[1]

    fh = open(os.path.join(pth, 'article.txt'), 'r', encoding='utf-8')
    lines = fh.readlines()
    fh.close()
    for line in lines:
        txts.append(line[:-1])
    # print(txts)

    return simplejson.dumps({
        'state': state,
        'img': img,
        'txt': txts
    })

@app.route('/Mini_Bookhouse/manager/judge')
def judge():
    state = -2

    usr_id = request.args.get("usr_id")
    count = request.args.get("count")
    category = request.args.get("category")
    res = request.args.get("res")

    # get id
    args = (usr_id, count, category)
    sql_tmp = "select id from temp where usr_id=%s and num=%s and category=%s;"
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql_tmp, args)
        data = cursor.fetchall()

        if len(data) == 1:
            id = data[0]['id']
            # print(id)
            state += 1#-1
    except:
        connection.rollback()
    cursor.close()

    if state == -1:
        sql_tmp = "update temp set state='%s', res='%s' where id=%d;"%("checked", res, int(id))
        cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
        try:
            cursor.execute(sql_tmp)
            connection.commit()
            state += 1#0
        except:
            connection.rollback()
        cursor.close()
    if state == 0:
        # insert into the true table
        args = (usr_id)
        if category == "audio":
            sql_nor = "insert into voice (usr_id) values (%s);"
        else:
            # category == "article"
            sql_nor = "insert into article (usr_id) values (%s);"
        cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
        try:
            cursor.execute(sql_nor, args)
            connection.commit()
            state += 1
        except:
            connection.rollback()
        cursor.close()

    return simplejson.dumps({
        'state': state
    })

if __name__ == '__main__':
    app.run(debug=True)