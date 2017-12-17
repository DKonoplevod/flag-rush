import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.realpath(__file__), '../../..')))
from hpctf.models import Task, User, Freeze


for freezes in Freeze.objects.all():
    print(freezes)
    freezes.delete()

for task in Task.objects:
    task.solver = None
    task.owner = None
    task.cost = task.base_cost
    task.best_time = 0
    task.last_solved_at = None
    task.save()

for user in User.objects:
    user.solved_tasks = []
    user.closed_tasks = []
    user.money = 500
    user.task_started_at = None
    user.save()

