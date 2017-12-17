# -*- coding: utf-8 -*-

import datetime
from flask import Blueprint, request, redirect, render_template, url_for
from flask_login import login_user, logout_user, current_user, login_required
from flask.views import MethodView
from hpctf.models import User, Task
from hpctf.tools import jsonify, render_json
from mongoengine.queryset import DoesNotExist


users_blueprint = Blueprint('users', __name__, template_folder='templates')


class LoginView(MethodView):
    def get(self):
        return render_template('login.html')

    def post(self):
        name = request.form['name']
        password = request.form['password']

        context = {
            'name': name,
            'password': password
        }

        try:
            user = User.objects.get(name=name)
        except DoesNotExist:
            context['error'] = u'Такой пользователь не найден!'
            return render_template('login.html', **context)

        if user.check_password(password):
            login_user(user)

        return redirect('/')


class LogoutView(MethodView):
        @login_required
        def get(self):
            logout_user()
            return redirect(url_for('users.login'))


class UpdateMoneyView(MethodView):
    def get(self):
        User.update_money()
        return render_json({'type': 'success', 'message': 'successs'})


class RegisterView(MethodView):
    def get(self):
        return render_template('register.html')

    def post(self):
        name = request.form.get('name', None)
        email = request.form.get('email', None)
        team = request.form.get('team', None)
        password = request.form.get('password', None)
        flag = request.form.get('key', None)

        context = {
            'email': email,
            'name': name,
            'team': team,
            'key': flag
        }
        if flag != 'h0n3yp0t_ctf_b3g1n':
            context['error'] = u'Неверный флаг'
            return render_template('register.html', **context)
        if name and email and team and password:
            if len(User.objects(name=name)):
                context['error'] = u'Пользователь с таки именем уже зарегестрирован!'
                return render_template('register.html', **context)
            user = User(name=name, email=email, team=team)
            user.set_password(password)
            user.save()
            return redirect(url_for('users.login'))
        else:
            context['error'] = u'Нужно заполнить все поля!'
            return render_template('register.html', **context)



class CurrentUserView(MethodView):
    @login_required
    def get(self):
        user = jsonify(current_user, include=['id'], exclude=['password_hash'])
        user['money'] = current_user.get_money()
        user['time'] = str(datetime.datetime.now())
        return render_json(user)


class ScoreboardView(MethodView):
    def get(self):
        tasks = Task.objects
        users = User.objects

        for user in users:
            user.profit = 0
            user.money = user.get_money()
            for task in tasks:
                if task.owner == user:
                    if not task.last_solved_at:
                        continue

                    user.profit += task.base_cost * 0.02

        context = {
            'users': users
        }

        return render_template('scoreboard.html', **context)



# Register urls
users_blueprint.add_url_rule('/api/user/current', view_func=CurrentUserView.as_view('current'))
users_blueprint.add_url_rule('/login', view_func=LoginView.as_view('login'))
users_blueprint.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
users_blueprint.add_url_rule('/scoreboard', view_func=ScoreboardView.as_view('scoreboard'))
users_blueprint.add_url_rule('/api/money/update', view_func=UpdateMoneyView.as_view('updatemoney'))
