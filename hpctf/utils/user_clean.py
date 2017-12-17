import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.realpath(__file__), '../../..')))

from hpctf.models import *

for user in User.objects:
    user.delete()
