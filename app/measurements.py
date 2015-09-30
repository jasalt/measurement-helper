# CRUD operations for measurements.

from flask import Blueprint, render_template, flash, request, redirect, \
    url_for, g
from flask_wtf import Form
from flask.ext.login import login_required

from wtforms import TextField, SubmitField, SelectField, ValidationError, \
    IntegerField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
from datetime import date
from toolz import dissoc, take

from model import entry_model, add_measurement, read_measurements, \
    delete_measurement, get_measurement, update_measurement, read_date_str, \
    get_notification_intervals, set_notification_intervals

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
    data = take(5, read_measurements()) or None
    g.entry_model = entry_model

    form = MeasurementForm()
    if request.method == 'POST' and form.validate():
        add_measurement(dissoc(form.data, 'submit'))
        flash("Merkintä lisätty.")
        return redirect(url_for('measurements.dashboard'))

    return render_template('index.html', form=form, measurements=data)


@mod.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    print("Editing ID " + id)
    entry = get_measurement(id)
    g.entryid = entry['id']

    # HACK worked around csrf missing problem
    form = MeasurementForm(csrf_enabled=False)

    if request.method == 'POST' and form.validate():
        entry = dissoc(form.data, 'submit')
        entry['id'] = int(id)
        update_measurement(entry)
        flash("Merkintä päivitetty.")
        return redirect(url_for('measurements.dashboard'))

    # Change default values
    form.type.default = entry['type']
    form.comment.default = entry['comment']
    form.value.default = entry['value']
    form.date.default = read_date_str(entry['date'])
    form.process()

    return render_template('edit.html', form=form)


@mod.route('/history')
@login_required
def history():
    '''List all measurements from db'''
    data = read_measurements()
    g.entry_model = entry_model
    
    if not data:
        flash("Tietokanta on tyhjä!")
        return redirect(url_for('measurements.dashboard'))
    
    graph_data = [[x['date'], x['value']]
                  for x in data if x['type'] == 'silt_active_ml_per_l']
    
    return render_template('history.html',
                           measurements=data, graph_data=graph_data)


@mod.route('/delete/<id>')
@login_required
def delete(id):
    delete_measurement(id)
    flash("Merkintä poistettu.")
    return redirect(url_for('measurements.dashboard'))


class SetupForm(Form):
    @classmethod
    def append_field(cls, name, field):
        '''Append field to form from outside code.'''
        setattr(cls, name, field)
        return cls


@mod.route('/setup', methods=['GET', 'POST'])
@login_required
def setup():
    # Form fields are appended dynamically
    class SetupForm(Form):
        pass

    for ni in get_notification_intervals():
        setattr(SetupForm,
                ni['type'],
                IntegerField(entry_model[ni['type']]['finnish'],
                             default=ni['interval_days']))
    SetupForm.submit = SubmitField('Tallenna')

    form = SetupForm()
    if request.method == 'POST' and form.validate():
        set_notification_intervals(dissoc(form.data, 'submit'))
        flash("Ilmoitusasetukset päivitetty!")
        return redirect(url_for('measurements.dashboard'))

    return render_template('setup.html', form=form)
