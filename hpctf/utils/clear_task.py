import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.realpath(__file__), '../../..')))

from hpctf.models import *

for item in Task.objects:
    item.delete()
