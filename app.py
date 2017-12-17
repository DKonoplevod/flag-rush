import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



# from flask.ext.script import Manager, Server
from flask_script import Manager, Server
from hpctf import app


manager = Manager(app)

# Develop env
# manager.add_command('runserver', Server(
#     use_debugger=True,
#     use_reloader=True,
#     host='0.0.0.0')
# )

if __name__ == '__main__':
    manager.run(threaded=True)
