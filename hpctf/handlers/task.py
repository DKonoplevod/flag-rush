# -*- coding: utf-8 -*-

import datetime
from flask import Blueprint, request
from flask_login import current_user, login_required
from flask.views import MethodView
from hpctf.models import Task, Freeze, User
from hpctf.tools import jsonify, render_json
from mongoengine import ValidationError
from mongoengine.queryset import DoesNotExist


task_blueprint = Blueprint('task', __name__, template_folder='templates')


class TaskListView(MethodView):
    @login_required
    def get(self):
        tasks = []
        for task_obj in Task.objects:
            task = jsonify(task_obj, include=['id'], exclude=['flag', 'description'])
            task['closed'] = task_obj in current_user.closed_tasks
            task['solved'] = task_obj in current_user.solved_tasks
            if task_obj.solver:
                task['solver_name'] = task_obj.solver.name
            if task_obj.owner:
                task['owner_name'] = task_obj.owner.name
            tasks.append(task)

        return render_json(tasks)


class TaskView(MethodView):
    @login_required
    def get(self):
        task_id = request.args.get('id', None)

        try:
            task_obj = Task.objects.get(id=task_id)
        except DoesNotExist:
            return render_json({'type': 'error', 'message': u'Task is not found'})
        except ValidationError as e:
            return render_json({'type': 'error', 'message': u'Task is not found'})
        except BaseException:
            print('Exception')

        task = jsonify(task_obj, include=['id'], exclude=['flag', 'description'])

        if task_obj.solver:
            task['solver_name'] = task_obj.solver.name

        if task_obj.owner:
            task['owner_name'] = task_obj.owner.name

        if getattr(task_obj.solver, 'id', None) == current_user.id:
            task['description'] = task_obj.description

        # Time remain
        time_remain = task_obj.time_remain()

        if time_remain:
            task['time_remain'] = time_remain

        solving_time = task_obj.solving_time()
        if solving_time is not None:
            task['solving_time'] = solving_time

        task['solved'] = task_obj in current_user.solved_tasks

        return render_json(task)


class TaskOpenView(MethodView):
    @login_required
    def get(self):
        task_id = request.args.get('id')
        try:
            task = Task.objects.get(id=task_id)
        except ValidationError:
            return render_json({'type': 'error', 'message': u'Неверный таск'})
        if task in current_user.solved_tasks:
            return render_json({'type': 'error', 'message': u'Невозможно начать уже решенный таск'})
        if task in current_user.closed_tasks:
            return render_json({'type': 'error', 'message': u'Невозможно начать проваленный таск'})
        if task.solver:
            return render_json({'type': 'error', 'message': u'Таск уже решают'})
        if task.owner:
            cost = task.cost
        else:
            cost = task.base_cost
        if current_user.get_money() < cost:
            return render_json({'type': 'error', 'message': u'Денег нет?'})
        if len(Task.objects(solver=current_user.id)):
            return render_json({'type': 'error', 'message': u'Вы уже решаете таск, сначала завершите его.'})

        current_user.money -= cost
        current_user.task_started_at = datetime.datetime.now()
        current_user.save()
        print 'open task:', current_user.task_started_at, datetime.datetime.now()
        task.solver = current_user.to_dbref()
        task.save()

        return render_json({'type': 'success', 'message': u'Вы начали таск {}. Вы должны решить его за {} сек.'.format(task.name, task.base_time)})


class TaskCheckView(MethodView):
    @login_required
    def get(self):
        try:
            task = Task.objects.get(solver=current_user)
        except DoesNotExist:
            return render_json({'type': 'error', 'message': u'Вы не решаете таск. Хакер шоле?'})
        flag = request.args.get('flag', None)
        if task.expired():
            return render_json({'type': 'error', 'message': u'Вы просрочили таск.'})
        print(task.flag.upper(), flag.upper())
        if task.flag.upper() == flag.upper():
            solve_time = task.solving_time()
            # We have new tsar of mount
            if not task.owner or solve_time < task.best_time:
                current_user.money += (task.base_cost * 2)
                current_user.solved_tasks.append(task)
                current_user.task_started_at = None
                current_user.save()

                if task.owner:
                    prev_leader = User.objects.get(name=task.owner.name)
                    diff = (datetime.datetime.now() - task.last_solved_at)
                    prev_leader.money += (diff.seconds // 60) * task.cost * 0.02

                task.owner = current_user.to_dbref()
                task.best_time = solve_time
                task.last_solved_at = datetime.datetime.now()
                task.solver = None
                task.save()

                return render_json({'type': 'success', 'message': u'Поздравляем, вы решили таск "{}"'.format(task.name)})

            current_user.money += task.base_cost
            current_user.solved_tasks.append(task)
            current_user.task_started_at = None
            current_user.save()

            task.solver = None
            task.save()

            return render_json({'type': 'success', 'message': u'Поздравляем, вы решили таск. Однако очки не зачислились, т.к. вы затратили больше времени, чем предыдущая команда "{}"'.format(task.owner.name)})
        else:
            return render_json({'type': 'error', 'message': u'Неверный флаг'})


class TaskTimeRemainView(MethodView):
    @login_required
    def get(self):
        task_id = request.args.get('id', None)
        try:
            task = Task.objects.get(id=task_id)
        except DoesNotExist:
            return render_json({'type': 'error', 'message': u'Неверный id таска.'})
        if task.expired():
            return render_json({'type': 'error', 'message': u'Таск просрочен.'})
        user = task.solver
        if not user:
            return render_json({'type': 'error', 'message': u'Таск не решают. Или вы просрочили таск.'})
        if not user.task_started_at:
            return render_json({'type': 'error', 'message': u'Внутренняя ошибка инициализации таймера'})
        time_remain = task.time_remain()
        if not time_remain:
            return render_json({'type': 'error', 'message': u'Таск уже решен?'})
        return render_json({'type': 'success', 'message': time_remain})


class TaskCloseView(MethodView):
    @login_required
    def get(self):
        try:
            task = Task.objects.get(solver=current_user)
        except DoesNotExist:
            return render_json({'type': 'error', 'message': u'Вы не решаете таск. Хакер шоле?'})
        task.close()
        return render_json({'type': 'success', 'message': u'Такс {} закрыт!'.format(task.name)})


class TaskSetCostView(MethodView):
    @login_required
    def get(self):
        task_id = request.args.get('id', None)
        try:
            cost = abs(int(request.args.get('cost', None)))
        except ValueError:
            return render_json({'type': 'error', 'message': u'Неверная стоимость таска'})
        try:
            task = Task.objects.get(id=task_id)
        except DoesNotExist:
            return render_json({'type': 'error', 'message': u'Неверный таск id'})
        if task in current_user.solved_tasks:

            if current_user.get_money() < cost:
                return render_json({'type': 'error', 'message': u'Недостаточно денег!'})

            diff = (datetime.datetime.now() - task.last_solved_at)

            current_user.money += (diff.seconds // 60) * task.cost * 0.02
            current_user.money -= cost
            print('SetCoin: Current money - ' + current_user.money)

            current_user.save()

            task.last_solved_at = datetime.datetime.now()
            task.cost += cost
            task.save()
            return render_json({'type': 'success', 'message': u'Стоимость таска обновлена!'})
        else:
            return render_json({'type': 'error', 'message': u'Стоимость таска может менять только его хозяин.'})


class TaskFreezeAddView(MethodView):
    @login_required
    def get(self):
        try:
            task = Task.objects.get(solver=current_user)
        except DoesNotExist:
            return render_json({'type': 'error', 'message': u'Для остановки времени нужно решать таск.'})
        try:
            duration = abs(int(request.args.get('duration', None)))
        except ValueError:
            return render_json({'type': 'error', 'message': u'Неверное время заморозки'})
        cost = duration * 10 / 60  # calculate cost from freeze duration
        if current_user.get_money() < cost:
            return render_json({'type': 'error', 'message': u'Недстаточно денег!'})
        else:
            if task.expired():
                return render_json({'type': 'error', 'message': u'Таск уже просрочен!'})
            freeze = Freeze.current(task)
            if freeze:
                # if we have mo then one added freeze in future append to end
                freezes = Freeze.objects(created_at__gt=freeze.created_at).order_by('-created_at')
                if len(freezes):
                    freeze = freezes[0]
                created = freeze.created_at + datetime.timedelta(seconds=freeze.duration)
            else:
                created = datetime.datetime.now()
            current_user.money -= cost
            current_user.save()
            freeze = Freeze(created_at=created, user=current_user.to_dbref(), task=task, duration=duration)
            freeze.save()
            return render_json({'type': 'success', 'message': u'Время таска заморожено!'})


# Register urls
task_blueprint.add_url_rule('/api/task/list', view_func=TaskListView.as_view('list'))
task_blueprint.add_url_rule('/api/task/get', view_func=TaskView.as_view('get'))
task_blueprint.add_url_rule('/api/task/open', view_func=TaskOpenView.as_view('open'))
task_blueprint.add_url_rule('/api/task/close', view_func=TaskCloseView.as_view('close'))
task_blueprint.add_url_rule('/api/task/check', view_func=TaskCheckView.as_view('check'))
task_blueprint.add_url_rule('/api/task/cost', view_func=TaskSetCostView.as_view('cost'))
task_blueprint.add_url_rule('/api/task/freeze', view_func=TaskFreezeAddView.as_view('freeze'))
task_blueprint.add_url_rule('/api/task/remain', view_func=TaskTimeRemainView.as_view('remain'))
