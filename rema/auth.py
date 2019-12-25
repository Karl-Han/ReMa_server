from flask import (Blueprint, session, render_template, redirect, flash, request, url_for)
import functools
from rema.__init__ import connection
from rema.db import update, para

auth= Blueprint('authorize', __name__, url_prefix='/autho')

@auth.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        respond = {}
        error = None
        try:
            username = request.form['username']
            password = request.form['password']
        except KeyError:
            respond["status"] = 702
            return respond
        else:
            #db = get_db()
            status = 700

            #elif db.execute(
            #    'SELECT id FROM user WHERE username = ?', (username,)
            #).fetchone() is not None:
            with connection.cursor()as Cursor:
                Cursor.execute( 'SELECT uid FROM user WHERE username = %s', (username))
                res = Cursor.fetchone()
                print(res)
                if res != None:
                    error = 'User {} is already registered.'.format(username)
                    status = 701

            if error is None:
                #db.execute(
                #    'INSERT INTO user (username, password) VALUES (?, ?)',
                #    (username, generate_password_hash(password))
                #)
                #db.commit()
                with connection.cursor() as Cursor:
                    Cursor.execute(
                        'INSERT INTO user (type, username, password) values (%s, %s, %s)'
                    , ('U', username, password))
                connection.commit()
                with connection.cursor() as Cursor:
                    Cursor.execute(
                        'SELECT uid, type from user WHERE username = %s'
                    , (username))
                    res = Cursor.fetchone()
                    print(res)
                    uid = res[0]
                    user_type = res[1]
                update(700, para(uid, user_type, username))
                # it use blueprint.function to distinguish
                #return redirect(url_for('authorize.login'))

            flash(error)
            respond = {}
            respond['status'] = status
            return respond

    return render_template('auth/register.html')

@auth.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        print('username = {}, password = {}'.format(username, password))
        #user = db.execute(
        #    'SELECT * FROM user WHERE username = ?', (username,)
        #).fetchone()
        with connection.cursor() as Cursor:
            Cursor.execute('SELECT password, uid FROM user WHERE username = %s' , (username))
            user_password = Cursor.fetchone()
            print(user_password)

        if user_password is None:
            error = 'Incorrect username.'
        elif user_password[0] != password:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['uid'] = user_password[1]
            return redirect(url_for('tableList.index'))

        flash(error)
        respond = {}
        respond["status"] = 1
        respond["Advice"] = "Please refresh this page"
        return respond
    # it is GET return login panel
    return render_template('autho/login.html')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        try:
            uid = session['uid']
        except KeyError:
            flash('Login first')
            return redirect(url_for('authorize.login'))
        else:
            return view(**kwargs)

    return wrapped_view

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        try:
            uid = session['uid']
        except KeyError:
            flash('Login first')
            return redirect(url_for('authorize.login'))
        else:
            with connection.cursor() as Cursor:
                sql = 'SELECT type FROM user WHERE uid = %s'
                Cursor.execute(sql, (uid))
                res = Cursor.fetchone()
                print(res)
                if res[0] == 'U':
                    flash('NOT administrator, Permission Denied')
                    return redirect(url_for('authorize.login'))
            return view(**kwargs)

    return wrapped_view

@auth.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    if request.method == 'POST':
        respond = {}
        respond['status'] = 0
        print(respond)
        return respond
    return redirect(url_for('index'))
