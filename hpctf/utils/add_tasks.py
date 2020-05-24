# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.realpath(__file__), '../../..')))
from hpctf.models import Task, User
from mongoengine.queryset import DoesNotExist

tasks = [
    {
        'name': 'The simplest task',
        'cat': 'start',
        'description': 'Flag is "tеstflаg. Flag format democtf{...}"',
        'flag': 'democtf{testflag}',
        'base_cost': '10',
        'base_time': '15',
        'cost': 10
    },
    {
        'name': 'Simple task',
        'cat': 'misc',
        'description': 'EasyCTF started on November 3rd, 2015 this year. Find the position where the numerical representation of the month and day of this date 1103 is first found within pi. Use any language you want! The flag is the position of the first digit of the date within pi, where 3 is the first digit and the decimal point . is not considered a position.',
        'flag': 'democtf{3494}',
        'base_cost': '200',
        'base_time': '20',
        'cost': 200
    },
    {
        'name': 'Difficult task',
        'cat': 'crypto',
        'description': 'Apparently some bitwise boi is posting flags all over the place. He gave us a hint, though. ZGVtb2N0ZntmbGFnX2Zvcl9jcnlwdG99',
        'flag': 'democtf{flag_for_crypto}',
        'base_cost': '300',
        'base_time': '30',
        'cost': 300
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
