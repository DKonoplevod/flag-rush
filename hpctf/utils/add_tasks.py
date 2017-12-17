# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.realpath(__file__), '../../..')))
from hpctf.models import Task, User
from mongoengine.queryset import DoesNotExist

tasks = [
    {
        'name': 'Some task title',
        'cat': 'crypto',
        'description': 'Sample description',
        'flag': 'someflag',
        'base_cost': '250',
        'base_time': '30',
        'cost': 250
    }
]


def check_name(name):
    try:
        Task.objects.get(name=name)
        return True
    except DoesNotExist:
        return False


for item in tasks:
    if check_name(item['name']):
        print('{} already exists. Skip'.format(item['name']))
        continue

    d = item['description']

    if 'link' in item:
        if isinstance(item['link'], basestring):
            d += '<br> <a href="{}">{}</a>'.format(item['link'], 'Ссылка')
        else:
            for l in item['link']:
                d += '<br> <a href="{}">{}</a>'.format(l, 'Ссылка')

    entity = Task(
        category=item['cat'],
        description=d,
        name=item['name'],
        flag=item['flag'],
        base_cost=item['base_cost'],
        base_time=int(item['base_time']) * 60,
        cost=item['base_cost']
    )

    entity.save()
