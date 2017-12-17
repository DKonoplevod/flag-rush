import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.realpath(__file__), '../../..')))

from hpctf.models import User, Task, Freeze

print("Users")
for user in User.objects.all():
    print(user)


print("Tasks")
for item in Task.objects.all():
    print(item  )
