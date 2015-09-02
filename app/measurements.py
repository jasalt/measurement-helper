# CRUD operations for measurements.

from flask import Blueprint, render_template, flash, request, redirect, \
    url_for, current_app, g
from flask_wtf import Form
from flask.ext.login import login_required

from wtforms import TextField, SubmitField, SelectField, ValidationError, \
    IntegerField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, NumberRange
from datetime import date
from time import strptime, mktime
from toolz import dissoc

from model import entry_model, add_measurement, read_measurements, \
    delete_measurement, get_measurement

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


class MeasurementForm(Form):
    entry_choises = [(k, v['finnish']) for k, v in entry_model.items()]
    sorted_choises = sorted(entry_choises, key=lambda tuple: tuple[1])

    type = SelectField("Mittaustyyppi", choices=sorted_choises)
    date = DateField('Päiväys (muotoa. 12-20-2015)', default=date.today())
    value = IntegerField('Mittausarvo', validators=[DataRequired(),
                                                    value_validation])
    comment = TextField('Valinnainen kommentti')
    submit = SubmitField('Lähetä')


# TODO route to login if not logged in
@mod.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    '''Default view with box for adding measurements and list of five last
    entries.'''
    # request.form.last_added
    data = read_measurements() or None
    ## take 5 from data based on last dates
    form = MeasurementForm()
    if request.method == 'POST' and form.validate():
        add_measurement(dissoc(form.data, 'submit'))
        return redirect(url_for('measurements.dashboard'))

    return render_template('index.html', form=form, measurements=data)


@mod.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    print("Editing ID " + id)
    entry = get_measurement(id)
    g.entryid = entry.id

    form = MeasurementForm()

    # Change default values
    form.type.default = entry.type
    form.comment.default = entry.comment
    form.value.default = entry.value

    st = strptime(entry.date, "%Y-%m-%d")
    d = date.fromtimestamp(mktime(st))
    form.date.default = d

    form.process()

    if request.method == 'POST' and form.validate():
        add_measurement(dissoc(form.data, 'submit'))
        return redirect(url_for('measurements.dashboard'))

    return render_template('edit.html', form=form)


@mod.route('/history')
@login_required
def history():
    '''List all measurements from db'''
    data = read_measurements()
    if not data:
        flash("Tietokanta on tyhjä.")
        return redirect(url_for('measurements.dashboard'))
    return render_template('history.html', measurements=data)


@mod.route('/delete/<id>')
@login_required
def delete(id):
    delete_measurement(id)
    flash("Merkintä poistettu.")
    return redirect(url_for('measurements.dashboard'))
