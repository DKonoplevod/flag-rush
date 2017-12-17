from hpctf.handlers.main import Home
from hpctf.handlers.user import LoginView


def urls(app):
    app.add_url_rule('/', endpoint='main', view_func=Home.as_view('main'))
    app.add_url_rule('/login', endpoint='login', view_func=LoginView.as_view('login'))
