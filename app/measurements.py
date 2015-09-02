# CRUD operations for measurements.

from flask import Blueprint, render_template, flash, request, redirect, \
    url_for, current_app
from flask_wtf import Form
from flask.ext.login import login_required

from wtforms import TextField, SubmitField, SelectField, ValidationError, \
    IntegerField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, NumberRange
from datetime import date
from toolz import dissoc

from model import entry_model, add_measurement, read_measurements

mod = Blueprint('measurements', __name__)


def value_validation(form, field):
    ''' Validates that field.data corresponds to value range of form.data['type']
    defined in model. Builds error message accordingly.'''
    value = field.data
    value_model = entry_model[form.data['type']]
    if value > value_model['max'] or value < value_model['min']:
        raise ValidationError(
            "Virheellinen arvo. Syötä %s väliltä %d - %d."
            % (value_model['description'],
               value_model['min'],
               value_model['max']))


class AddForm(Form):
    entry_choises = [(k, v['finnish']) for k, v in entry_model.items()]
    sorted_choises = sorted(entry_choises, key=lambda tuple: tuple[1])

    type = SelectField("Mittaustyyppi", choices=sorted_choises)
    date = DateField('Päiväys (muotoa. 12-20-2015)', default=date.today())
    value = IntegerField('Mittausarvo', validators=[DataRequired(),
                                                    value_validation])
    comment = TextField('Valinnainen kommentti')
    submit = SubmitField('Lähetä')


@mod.route('/show')
@login_required
def show_measurements():
    return "This is the history"


# TODO route to login if not logged in
@mod.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    # request.form.last_added
    data = read_measurements()
    form = AddForm()
    if request.method == 'POST' and form.validate():
        add_measurement(dissoc(form.data, 'submit'))
        return redirect(url_for('measurements.dashboard'))

    return render_template('index.html', form=form, measurements=data)

# Default to dashboard view with 10 last measurements and addition box
#
