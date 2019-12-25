import pymysql.cursors
import json
import random
import hashlib
import datetime
from flask import (request, Blueprint)
from rema.__init__ import (connection, db_hash)

tables = ['comments', 'course', 'teacher', 'teaching', 'user', 'incrementTable']

def para(*args):
    s = '('
    comma = ','
    for x in args:
        if type(x) == str:
            s = s + '"' + x + '"' + comma
        else:
            s = s + str(x) + comma
    s = s[:-1]
    s = s + ')'
    return s

def consult_table(tablename):
    with connection.cursor() as Cursor:
        sql = 'SELECT * from {}'.format(tablename)
        #Cursor.execute(sql, (tablename))
        Cursor.execute(sql)
        res = Cursor.fetchall()
        return res

def print_table(tablename):
    res = consult_table(tablename)
    for x in res:
        print(x)

def generate_json(tablename):
    table_json = {}
    table_json['table'] = tablename
    res = consult_table(tablename)
    values = []
    # if table is comments
    # res[i] is (coid, uid, content, cid) 
    fields = []
    with connection.cursor() as Cursor:
        Cursor.execute('desc {}'.format(tablename))
        headers = Cursor.fetchall()
        for index, x in enumerate(headers):
            fields.insert(index, x[0])
        #print(fields)
    # x is a record
    for x in res:
        value = {}
        for index, f in enumerate(x):
            if fields[index] in ['password', 'type', 'addHash', 'addTime']:
                continue
            value[fields[index]] = f
        values.insert(0, value)
    table_json['values'] = values
    #print(table_json)
    with open("json/" + tablename + '.json', 'w', encoding='UTF-8') as f:
        json.dump(table_json, f)

def generate_all_jsons():
    for table in tables:
        generate_json(table)

def calculate_hash():
    hasher = hashlib.sha3_256()
    for table in tables:
        with open("json/" + table + '.json', 'r', encoding='UTF-8') as f:
            data = json.load(f)
        hasher.update(str(data).encode('utf-8'))
    h = hasher.hexdigest()
    return h

def get_last_hash():
    global db_hash
    with connection.cursor() as Cursor:
        sql = 'SELECT addHash from incrementTable ORDER BY addTime DESC LIMIT 1'
        Cursor.execute(sql)
        res = list(Cursor.fetchall())
        if len(res) == 0:
            db_hash = '00000'
            return db_hash
        db_hash = str(res[0][0], encoding='utf-8')
        return db_hash

def get_uid(username, password):
    with connection.cursor() as Cursor:
        sql = 'SELECT uid from user where username = %s and password = %s'
        Cursor.execute(sql, (username, password))
        res = Cursor.fetchall()
        if len(res) == 1:
            return res[0][0]
        # -1 represent no such uid
        return -1

def get_updates(last_hash):
    with connection.cursor() as Cursor:
        #print(last_hash)
        sql = 'SELECT addTime from incrementTable where addHash = %s'
        Cursor.execute(sql, (last_hash))
        hash_time = Cursor.fetchall()
        #print('hash_time = ' , hash_time)
        if hash_time == ():
            return None
        sql = 'SELECT opcode, content from incrementTable where addTime > %s'
        Cursor.execute(sql, (hash_time))
        res = Cursor.fetchall()
        respond = []
        for (o, c) in res:
            obj = {}
            obj['opcode'] = o
            obj['content'] = c
            respond.insert(-1, obj)
        print(respond)
        return respond

# update local file and add hash
def update(opcode, content):
    print(content)
    generate_all_jsons()
    h = calculate_hash()
    global db_hash
    db_hash = h[0:5]
    print('new db_hash = ' + db_hash)
    print("content = {}".format(content))
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with connection.cursor() as Cursor:
        sql = 'INSERT INTO incrementTable (addHash, addTime, opcode, content) value (%s, %s, %s, %s)'
        Cursor.execute(sql, (db_hash, dt, opcode, content))
    connection.commit()
    return db_hash

def insert_new_comment_db(uid, comment, cid):
    with connection.cursor() as Cursor:
        sql = 'INSERT INTO comments (uid, content, cid) value (%s, %s, %s)'
        Cursor.execute(sql, (uid, comment, cid))
    connection.commit()
    with connection.cursor() as Cursor:
        sql = 'SELECT coid FROM comments WHERE uid = %s AND content = %s AND cid = %s'
        Cursor.execute(sql, (uid, comment, cid))
        res = Cursor.fetchall()
        print(res)
        coid = res[0][0]
    h = update(100, para(coid, uid, comment, cid))
    return h

# return status
def delete_comment_db(uid, coid):
    with connection.cursor() as Cursor:
        sql = 'SELECT uid FROM comments where coid = %s'
        Cursor.execute(sql, (coid))
        uid_return = Cursor.fetchone()
    print('uid return = ' + str(uid_return))
    uid_return = uid_return[0]
    if uid_return == None:
        # No such comment
        return (203, None)
    elif uid_return != uid:
        # No permission to delete comment
        return (204, None)
    else:
        with connection.cursor() as Cursor:
            sql = 'DELETE FROM comments where coid = %s'
            Cursor.execute(sql, (coid))
        connection.commit()
        h = update(200, para(coid))
        return (200, h)

# update comment
def update_comment_db(uid, coid, comment):
    with connection.cursor() as Cursor:
        sql = 'SELECT uid FROM comments where coid = %s'
        Cursor.execute(sql, (coid))
        uid_return = Cursor.fetchone()
    if len(uid_return) == 0:
        # No such comment
        return (203, None)
    elif uid_return[0] != uid:
        # No permission to delete comment
        return (204, None)
    else:
        with connection.cursor() as Cursor:
            sql = 'UPDATE comments SET content = %s WHERE coid = %s'
            Cursor.execute(sql, (comment, coid))
        connection.commit()
        h = update(200, para(coid, comment))
        return (200, h)

def get_tid_or_create_db(tname):
    with connection.cursor() as Cursor:
        sql = 'SELECT tid FROM teacher WHERE tname = %s'
        Cursor.execute(sql, (tname))
        tid = Cursor.fetchone()
        print('tid = {}'.format(tid))
    if tid == None:
        # no such teacher
        with connection.cursor() as Cursor:
            sql = 'INSERT INTO teacher (tname) value (%s)'
            Cursor.execute(sql, (tname))
        connection.commit()
        sql = 'SELECT tid FROM teacher WHERE tname = %s'
        Cursor.execute(sql, (tname))
        tid = Cursor.fetchone()
    return tid[0]

def insert_new_course_db(cname, tname, intro, uid):
    tid = get_tid_or_create_db(tname)
    with connection.cursor() as Cursor:
        sql = 'INSERT INTO course (cname, tid, intro, likes, uid) value (%s, %s, %s, 0, %s)'
        Cursor.execute(sql, (cname, tid, intro, uid))
    connection.commit()

    with connection.cursor() as Cursor:
        sql = 'SELECT cid FROM course WHERE cname = %s and tid = %s'
        Cursor.execute(sql, (cname, tid))
        cid = Cursor.fetchone()[0]
    h = update(300, para(cid, cname, tid, intro, uid, tname))
    return h

# return status
def delete_course_db(uid, cid):
    with connection.cursor() as Cursor:
        sql = 'SELECT uid FROM course WHERE cid = %s'
        Cursor.execute(sql, (cid))
        uid_return = Cursor.fetchone()
    if len(uid_return) == None:
        # No such course
        return (403, None)
    elif uid_return[0] != uid:
        # No permission to delete course
        return (404, None)
    else:
        with connection.cursor() as Cursor:
            sql = 'DELETE FROM course where cid = %s'
            Cursor.execute(sql, (cid))
        connection.commit()
        h = update(400, para(cid))
        return (400, h)

# update course 
def update_course_db(cid, cname, tname, intro, likes, uid):
    tid = get_tid_or_create_db(tname)
    with connection.cursor() as Cursor:
        sql = 'UPDATE comments SET cname = %s, tid = %s, intro = %s WHERE cid = %s'
        Cursor.execute(sql, (cname, tid , intro))
    connection.commit()
    h = update(400, para(cid, cname, tid, intro))
    return (400, h)

def like_course_db(cid, uid):
    with connection.cursor() as Cursor:
        sql = 'SELECT likes FROM course WHERE cid = %s'
        Cursor.execute(sql, (cid))
        res = list(Cursor.fetchone())
        if len(res) == 0:
            return 501
        likes = res[0]

    with connection.cursor() as Cursor:
        sql = 'UPDATE course SET likes = %s WHERE cid = %s'
        Cursor.execute(sql, (likes +1, cid))
    connection.commit()
    h = update(500, para(likes +1, cid))
    return (500, h)
