# User authentication specific code
from flask import Blueprint, render_template, flash, request, redirect, \
    url_for
from flask_wtf import Form
from wtforms import PasswordField, SubmitField
from flask_login import LoginManager, login_user, UserMixin, logout_user
from wtforms.validators import DataRequired, AnyOf
from utils import get_env

auth_key = get_env('FLASK_APP_PASSWORD') or 'topsecret'
auth_keys = [auth_key]  # TODO ugly quick workaround

mod = Blueprint('authentication', __name__)

login_manager = LoginManager()
login_manager.login_view = "authentication.login"


class User(UserMixin):
    # http://gouthamanbalaraman.com/blog/minimal-flask-login-example.html
    # https://flask-login.readthedocs.org/en/latest/#your-user-class

    # TODO
    # id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(80), unique=True)
    # email = db.Column(db.String(120), unique=True)

    def __init__(self):
        self.id = "no-one"

    @classmethod
    def get(cls, id):
        return User(id)


@login_manager.user_loader
def load_user(id):
    # ID is ignored, using single user authentication
    return User()


class LoginForm(Form):
    password = PasswordField('Salasana',
                             validators=[DataRequired(),
                                         AnyOf(auth_keys,
                                               'Salasana on väärä!')])
    submit = SubmitField('Kirjaudu')


@mod.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_user(User(), remember=True, force=True)
        flash("Kirjautuminen onnistui!")
        next = request.args.get('next')
        # note: next should be validated for security purposes!
        return redirect(next or url_for('measurements.dashboard'))
    return render_template('login.html', form=form)


@mod.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication.login'))
