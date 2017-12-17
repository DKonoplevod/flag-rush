# -*- coding: utf-8 -*-
import os
import datetime
from flask import Flask
from flask_login import LoginManager
from flask_mongoengine import MongoEngine


app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db' : 'hpctf',
    'host': 'mongodb',
    'port': 27017
}
app.config['SECRET_KEY'] = '#CTFcupsecretKeY5261'
app.last_users_update = datetime.datetime.now()
app.debug = False

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
