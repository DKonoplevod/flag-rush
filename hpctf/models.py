# -*- coding: utf-8 -*-

import datetime
from flask_login import UserMixin, current_user
from hpctf import db, login_manager, app
from mongoengine.queryset import DoesNotExist
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    email = db.StringField(max_length=255, required=True)
    name = db.StringField(max_length=255, required=True)
    password_hash = db.StringField(max_length=255, required=True)
    money = db.IntField(default=500)
    closed_tasks = db.ListField(db.ReferenceField('Task', dbref=False))
    solved_tasks = db.ListField(db.ReferenceField('Task', dbref=False))
    task_started_at = db.DateTimeField(default=None)
    team = db.StringField(required=True)

    def __unicode__(self):
        return unicode(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '{}/{}'.format(self.id, self.email)

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'email'],
        'ordering': ['-created_at']
    }

    def get_money(self):
        base_money = self.money

        for task in Task.objects:
            if task.owner == self:
                if not task.last_solved_at:
                    continue

                diff = (datetime.datetime.now() - task.last_solved_at)
                base_money += (diff.seconds // 60) * task.base_cost * 0.02

        return base_money

    # must run every 1 minute
    @staticmethod
    def update_money():
        now = datetime.datetime.now()
        for user in User.objects:
            for task in user.solved_tasks:
                if task.owner == user:
                    bc_in_min = task.base_cost * 0.02
                    period = (now - app.last_users_update).seconds
                    money_for_period = bc_in_min * period / 60
                    user.money += money_for_period
                    print(user.name, money_for_period, now, app.last_users_update)
            bc_in_min = 2
            period = (now - app.last_users_update).seconds
            money_for_period = bc_in_min * period / 60
            user.money += money_for_period
            user.save()
        app.last_users_update = now


def create_user(email, name, password):
    password_hash = generate_password_hash(password)
    return User(email=email, name=name, password_hash=password_hash)


@login_manager.user_loader
def load_user(userid):
    try:
        return User.objects.get(id=userid)
    except DoesNotExist:
        return None


class Task(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    last_solved_at = db.DateTimeField(default=None)
    name = db.StringField(required=True)
    category = db.StringField()
    description = db.StringField(required=True)
    flag = db.StringField(required=True)
    base_cost = db.IntField(min_value=0, required=True)
    base_time = db.IntField(min_value=0, required=True)  # in sec
    best_time = db.IntField(min_value=0, default=0)  # in sec
    cost = db.IntField(min_value=0)
    owner = db.ReferenceField(User, default=None, dbref=False)
    solver = db.ReferenceField(User, default=None, dbref=False)

    def __repr__(self):
        return '{}/{}'.format(self.id, self.name)

    def __unicode__(self):
        return unicode(self.id)

    def close(self):
        self.solver = None
        self.save()
        current_user.closed_tasks.append(self)
        current_user.task_started_at = None
        current_user.save()

    def expired(self):
        user = self.solver
        if not user:
            return False

        try:
            freezes = Freeze.objects(user=user, task=self)
            freeze_time = reduce(lambda sum, f: sum + f.duration, freezes, 0)
        except DoesNotExist:
            print('Does not exist')
            return False
        except BaseException:
            print('Error')

        if not user.task_started_at:
            return False

        task_end = user.task_started_at + datetime.timedelta(seconds=self.base_time) + datetime.timedelta(seconds=freeze_time)

        now = datetime.datetime.now()
        if task_end < now:
            self.close()
            return True
        else:
            return False

    def time_remain(self):
        user = self.solver

        if not user:
            return False

        if self.expired():
            return False

        now = datetime.datetime.now()

        # get all available task time
        all_time = self.base_time + reduce(lambda x, y: x + y.duration, Freeze.objects(user=user, task=self), 0)

        if not user.task_started_at:
            return False

        time_remain = all_time - (now - user.task_started_at).seconds
        if time_remain < 0:
            return False
        return time_remain

    def solving_time(self):
        user = self.solver
        if not user:
            return False

        # if task now is freezed
        freeze = Freeze.current(self)
        if freeze:
            current = freeze.created_at
        else:
            current = datetime.datetime.now()

        if not user.task_started_at:
            return None

        solving = (current - user.task_started_at).seconds
        print(current, user.task_started_at)

        freezes = Freeze.objects(user=user, task=self, created_at__lt=current)

        if freezes and len(freezes):
            solving -= reduce(lambda x, y: x + y.duration, freezes, 0)
        return solving


class Freeze(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    duration = db.IntField(default=0, min_value=0)
    user = db.ReferenceField(User, default=None, dbref=False)
    task = db.ReferenceField(Task, default=None, dbref=False)

    @staticmethod
    def current(task):
        now = datetime.datetime.now()
        freezes = Freeze.objects(created_at__lte=now, user=current_user, task=task)
        for freeze in freezes:
            if (now - freeze.created_at).seconds < freeze.duration:
                return freeze
        return None
