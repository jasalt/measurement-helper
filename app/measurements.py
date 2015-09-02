# CRUD operations for measurements.

from flask import Blueprint, render_template, flash, request, redirect, \
    url_for, current_app
from flask_wtf import Form
from flask.ext.login import login_required

from wtforms import TextField, SubmitField, SelectField, ValidationError, \
    IntegerField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, NumberRange

from model import entry_types

mod = Blueprint('measurements', __name__)


def value_validation(form, field):
    import ipdb; ipdb.set_trace()
    # Validate that field.data corresponds to value range of form.data['type']
    # defined in model

    if (field.data < 100):
        print("ValidationFail")
        raise ValidationError("Less than 100")


# TODO https://pypi.python.org/pypi/wtforms-html5
class AddForm(Form):
    # Build choises from model.entry_types
    entry_choises = [(k, v['finnish']) for k, v in entry_types.items()]
    sorted_choises = sorted(entry_choises, key=lambda tuple:
                            tuple[1])
    type = SelectField("Mittaustyyppi", choices=sorted_choises)
    date = DateField('Päiväys')  # TODO default to today, tidy formatting
    value = IntegerField('Mittausarvo', validators=[DataRequired(),
                                                    value_validation])
    comment = TextField('Valinnainen kommentti')
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
    # request.form.last_added
    form = AddForm()
    if request.method == 'POST' and form.validate():
        print("Valid!")
        print(form.data)
        flash('Thanks for registering')
        return redirect(url_for('measurements.dashboard'))

    return render_template('index.html', form=form)

# Default to dashboard view with 10 last measurements and addition box
#
