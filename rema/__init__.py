import os
import pymysql

from flask import Flask

#connection = pymysql.connect(
#    host='10.243.0.186',
#    user='rema',
#    password='rema-team',
#    db='rema'
#)

connection = pymysql.connect(
    host='127.0.0.1',
    user='rema',
    password='ReMaTeam',
    db='rema'
)
db_hash = ''

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        #DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    print(app.config['SECRET_KEY'])
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    global db_hash

    from . import db
    # import db
    db.generate_all_jsons()
    db_hash = db.get_last_hash()

    from . import auth
    # import blueprint
    app.register_blueprint(auth.auth)

    from . import manipulate
    app.register_blueprint(manipulate.mani)
    #app.add_url_rule('/', endpoint='index')

    from . import table_list
    app.register_blueprint(table_list.tableList)
    app.add_url_rule('/', endpoint='index')

    return app
