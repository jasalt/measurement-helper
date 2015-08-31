from flask import Flask, redirect, render_template, flash, request, url_for

from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

from flask.ext.login import LoginManager, login_user

from flask.ext.bootstrap import Bootstrap



login_manager = LoginManager()

app = Flask(__name__)
Bootstrap(app)

# LoginManager.init_app(app)


@login_manager.user_loader
def load_user(userid):
    # TODO load user from DB
    if userid == "test":
        return {'username': 'tester',
                'email': 'test@example.net'}
    else:
        return None


class LoginForm(Form):
    name = StringField('name', validators=[DataRequired()])
    password = PasswordField()
    submit = SubmitField('Kirjaudu')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # TODO set wtform
    if form.validate_on_submit():
        # login_user(user)
        flash("Logged in successfully")
        next = request.args.get('next')
        # if not next_is_valid(next):
        #     return flash.abort(400)

        return redirect(next or url_for('index'))
    # TODO setup login page template
    return render_template('login.html', form=form)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", name="jouko")


@app.route("/protected/", methods=["GET"])
# @login_required
def protected():
    return "Hello, protected!", 200
