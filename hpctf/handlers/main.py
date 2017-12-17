from flask import Blueprint, render_template
from flask.views import MethodView
from flask_login import login_required

main_blueprint = Blueprint('main', __name__, template_folder='templates')


class HomeView(MethodView):
    @login_required
    def get(self):
        return render_template('main.html')


main_blueprint.add_url_rule('/', view_func=HomeView.as_view('home'))
