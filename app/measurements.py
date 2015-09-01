# CRUD operations for measurements.

from flask import Blueprint, render_template, flash, request, redirect, \
    url_for, current_app
from flask_wtf import Form
from wtforms import TextField, SubmitField
from flask.ext.login import login_required
from wtforms.validators import DataRequired

mod = Blueprint('measurements', __name__)


class AddForm(Form):
    field = TextField('Loota',
                      validators=[DataRequired()])
    submit = SubmitField('Lähetä')


@mod.route('/show')
@login_required
def show_measurements():
    return "This is the history"


@mod.route('/add')
@login_required
def add_measurement():
    return "Should show form for adding new stuff."


@mod.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = AddForm()
    return render_template('index.html', form=form)

# Default to dashboard view with 10 last measurements and addition box
#
