# User authentication specific code
from flask import Blueprint, render_template, flash, request, redirect, \
    url_for
from flask_wtf import Form
from wtforms import PasswordField, SubmitField
from flask.ext.login import LoginManager, login_user
from wtforms.validators import DataRequired, AnyOf

mod = Blueprint('authentication', __name__)

from secret import auth_keys

login_manager = LoginManager()


@login_manager.user_loader
def load_user(userid):
    # TODO load user from DB
    if userid == "test":
        return {'username': 'tester',
                'email': 'test@example.net'}
    else:
        return None


class LoginForm(Form):
    password = PasswordField('Salasana',
                             validators=[DataRequired(),
                                         AnyOf(auth_keys,
                                               'Salasana on väärä!')])
    submit = SubmitField('Kirjaudu')


@mod.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # TODO set wtform
    if form.validate_on_submit():
        # login_user(user)
        flash("Kirjautuminen onnistui!")
        next = request.args.get('next')
        # if not next_is_valid(next):
        #     return flash.abort(400)

        return redirect(next or url_for('index'))
    # TODO setup login page template
    return render_template('login.html', form=form)
