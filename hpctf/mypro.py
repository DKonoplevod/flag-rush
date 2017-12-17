# -*- coding: utf-8 -*-

import datetime
from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.mongoengine import MongoEngine


app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {'DB': 'hpctf'}
app.config['SECRET_KEY'] = '#Very5ecr3etKey'
app.last_users_update = datetime.datetime.now()
app.debug = True

login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'users.login'
login_manager.login_message = u'Пожалуйста, авторизуйтесь.'

db = MongoEngine(app)


def register_blueprints(app):
    # Prevents circular imports
    from hpctf.handlers import users_blueprint, main_blueprint, task_blueprint
    app.register_blueprint(users_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(task_blueprint)

register_blueprints(app)

if __name__ == '__main__':
    app.run()
