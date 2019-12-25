from flask import (Blueprint, request, render_template, session, redirect, url_for, flash)
from rema.__init__ import connection
from rema.auth import (login_required, admin_required)

get_primary = {
    'user':'uid',
    'course':'cid',
    'comments':'coid',
    'teacher':'tid',
    'teaching':'cid',
    'incrementTable':'addHash'
}

tableList = Blueprint('tableList', __name__)

@tableList.route('/')
@login_required
def index():
    with connection.cursor() as Cursor:
        sql = 'SHOW TABLES'
        Cursor.execute(sql)
        res = Cursor.fetchall()
    l = []
    for x in res:
        l.insert(0, x[0])
    with connection.cursor() as Cursor:
        sql = 'SELECT type FROM user WHERE uid = %s'
        Cursor.execute(sql, (session['uid']))
        user_type = Cursor.fetchone()[0]
    try:
        table = request.args['d']
    except:
        predicate = (user_type == "A")
        if predicate:
            print(True)
            return render_template('table_list/index.html', tables = l, T = predicate)
        else:
            print(False)
            return render_template('table_list/index.html', tables = l)

    else:
        # got table and display data
        with connection.cursor() as Cursor:
            sql = 'DESC {}'.format(table)
            Cursor.execute(sql)
            h = Cursor.fetchall()
        headers = []
        for attr in h:
            if table == 'user' and user_type == 'U' and attr[0] in ['password', 'type']:
                continue
            headers.insert(len(headers), attr[0])
        print(headers)
        with connection.cursor() as Cursor:
            print('user_type = ' + user_type)
            if table == 'user' and user_type == 'U':
                sql = 'SELECT uid, username FROM {}'.format(table)
            else:
                sql = 'SELECT * FROM {}'.format(table)
            Cursor.execute(sql)
            res = Cursor.fetchall()
        print(res)
        predicate = (user_type == "A")
        if predicate:
            print(True)
            return render_template('table_list/index.html', tables = l, T = predicate, content = res, headers = headers)
        else:
            print(False)
            return render_template('table_list/index.html', tables = l, content = res, headers = headers)

@tableList.route('/delete', methods=['POST','GET'])
@admin_required
def delete():
    try:
        table = request.args['table_name']
    except KeyError:
        flash('table or primary key information missing')
    else:
        #return(str(request.form.to_dict(flat=False).values()))
        primary = get_primary[table]
        l = list(request.form.to_dict(flat=False).values())
        for id in l:
            print(id[0])
            with connection.cursor() as Cursor:
                sql = 'DELETE FROM {} WHERE {} = {}'.format(table, primary, id[0])
                Cursor.execute(sql)
            connection.commit()
        flash('SUCCESS')
    return redirect(url_for('tableList.index'))
