# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.realpath(__file__), '../../..')))

from hpctf.models import User
from mongoengine.queryset import DoesNotExist

users = [
    {
        'email': 'test@mail.ru',
        'team': 'test',
        'password': 'test',
        'money': '500',
        'name': 'user1'
    }
]


def check_name(name):
    try:
        User.objects.get(name=name)
        return True
    except DoesNotExist:
        return False

for user in users:
    if check_name(user['name']):
        print('{} already exists. Skip'.format(user['name']))
        continue

    print(user['email'], user['name'], user['team'])
    entity = User(
        email=user['email'],
        name=user['name'],
        team=user['team']
    )

    entity.set_password(user['password'])
    entity.save()
