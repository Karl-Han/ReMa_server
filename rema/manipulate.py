from rema.auth import login_required
from flask import (Blueprint, session, request, render_template)
from rema import (connection, db_hash)
from rema.db import (get_updates, insert_new_comment_db, delete_comment_db, insert_new_course_db, delete_course_db, like_course_db, update_comment_db, update_course_db)
import json

mani = Blueprint('manipualte', __name__, url_prefix='/mani')

tables = ['comments', 'course', 'teacher', 'teaching', 'user', 'incrementTable']

# last_hash is a hexadecimal number
@mani.route('/get_data/<lastHash>', methods=['POST', 'GET'])
@login_required
def fetch_data(lastHash):
    uid = session['uid']
    last_hash = str(lastHash)
    print(uid)
    respond = {}
    global tables
    tables_data = []
    table_list = []
    last_hash_int = int(last_hash, 16)
    print('last hash = ' + last_hash)
    global db_hash
    if uid == -1:
        respond['status'] = 404
        #print('No such user')
        return 'wrong user'
    else:
        respond['status'] = 600
        if last_hash_int == 0:
            print('Whole database')
            # new user and return the whole database
            for table in tables:
                print(table)
                if table == 'incrementTable':
                    continue
                with open("json/" + table + '.json', 'r') as f:
                    data = json.load(f)
                    tables_data.insert(0, data)
                    table_list.insert(0, table)
            respond['table_list'] = table_list
            respond['tables'] = tables_data
            respond['last_hash'] = db_hash
            print(db_hash)
            return respond
        elif last_hash != db_hash:
            # just send incrementTable
            print('Just increment')
            updates = get_updates(last_hash)
            if updates == None:
                respond['status'] = 603
            respond['status'] = 602
            respond['table'] = 'incrementTable'
            respond['values'] = updates
            respond['new_hash'] = db_hash
            return respond
        else:
            # already the latest update
            s = {}
            s['status'] = 601
            return s

@mani.route('/create_comment', methods=['POST', 'GET'])
@login_required
def create_comment():
    if request.method == 'POST':
        respond = {}
        try:
            cid = request.form['cid']
            comment = request.form['comment']
        except KeyError:
            respond['status'] = 102
            return respond
        else:
            uid = session['uid']
            cid = int(cid, 10)

            h = insert_new_comment_db(uid, comment, cid)
            respond['status'] = 100
            respond['new_hash'] = h
            respond['last_hash'] = db_hash
            print('db_hash = {}, new_hash = {}'.format(db_hash, h))
            return respond
    return render_template('mani/add_comment.html')

@mani.route('/delete_comment', methods=['POST'])
@login_required
def delete_comment():
    global db_hash
    respond = {}
    try:
        coid = request.form['coid']
    except KeyError:
        respond['status'] = 202
        return respond
    else:
        uid = session['uid']
        coid = int(coid, 10)
        (return_code, h) = delete_comment_db(uid, coid)

        respond['status'] = return_code
        if h == None:
            h = db_hash
        respond['new_hash'] = h
        print('db_hash = {}, new_hash = {}'.format(db_hash, h))
        return respond

@mani.route('/update_comment', methods=['POST'])
@login_required
def update_comment():
    global db_hash
    respond = {}
    try:
        coid = request.form['coid']
        comment = request.form['comment']
    except KeyError:
        respond['status'] = 202
        return respond
    else:
        uid = session['uid']
        coid = int(coid, 10)
        (return_code, h) = update_comment_db(uid, coid, comment)

        respond['status'] = return_code
        if h == None:
            h = db_hash
        respond['new_hash'] = h
        print('db_hash = {}, new_hash = {}'.format(db_hash, h))
        return respond

@mani.route('/create_course', methods=['POST'])
@login_required
def create_course():
    respond = {}
    try:
        cname = request.form['cname']
        tname = request.form['tname']
        intro = request.form['intro']
    except KeyError:
        respond['status'] = 302
        return respond
    else:
        uid = session['uid']

        h = insert_new_course_db(cname, tname, intro, uid)
        respond['status'] = 300
        respond['new_hash'] = h
        print('db_hash = {}, new_hash = {}'.format(db_hash, h))
        return respond

@mani.route('/delete_course', methods=['POST'])
@login_required
def delete_course():
    respond = {}
    try:
        cid = request.form['cid']
    except KeyError:
        cid = int(cid, 10)
        respond['status'] = 402
        return respond

    else:
        uid = session['uid']
        (return_code, h) = delete_course_db(uid, cid)

        respond['status'] = return_code
        respond['new_hash'] = h
        print('db_hash = {}, new_hash = {}'.format(db_hash, h))
        return respond

@mani.route('/update_course', methods=['POST'])
@login_required
def update_course():
    respond = {}
    try:
        cid = request.form['cid']
    except KeyError:
        respond['status'] = 402
        return respond

    else:
        cid = int(cid, 10)
        with connection.cursor() as Cursor:
            sql = 'SELECT cname, tid, intro, likes, uid FROM course WHERE cid == %s'
            Cursor.execute(sql, (cid))
            res = Cursor.fetchone()
        if len(res) == 0:
            # No such course
            respond['status'] = 403
            return respond
        cname = res[0]
        tid = res[1]
        intro = res[2]
        likes = res[3]
        uid_return = res[4]
        uid = session['uid']
        if uid != uid_return:
            # No permission
            respond['status'] = 404
            return respond
        if request.form.get('cname') != None:
            cname = request.form['cname']
        if request.form.get('tid') != None:
            tid = request.form['tid']
        if request.form.get('intro') != None:
            intro = request.form['intro']
        if request.form.get('likes') != None:
            likes = request.form['likes']
        if request.form.get('uid') != None:
            uid = request.form['uid']
        (return_code, h) = update_course_db(cid, cname, tid, intro, likes, uid)

        respond['status'] = return_code
        respond['new_hash'] = h
        print('db_hash = {}, new_hash = {}'.format(db_hash, h))
        return respond

@mani.route('/like', methods=['POST'])
@login_required
def like_course():
    respond = {}
    try:
        cid = request.form['cid']
    except KeyError:
        respond['status'] = 502
        return respond
    else:
        uid = session['uid']
        cid = int(cid, 10)
        (return_code, h) = like_course_db(cid, uid)
        respond = {}
        respond['status'] = return_code
        respond['new_hash'] = h
        return respond
