# CRUD operations for measurements.

from flask import Blueprint, render_template, flash, request, redirect, \
    url_for, current_app
from flask_wtf import Form
from wtforms import PasswordField, SubmitField
from flask.ext.login import login_required
from wtforms.validators import DataRequired, AnyOf

mod = Blueprint('measurements', __name__)


@mod.route('/show')
@login_required
def show_measurements():
    return "This is the history"


@mod.route('/add')
@login_required
def add_measurement():
    return "Should show form for adding new stuff."


@mod.route('/tiedot')
@login_required
def dashboard():
    return "Logged in"


# Default to dashboard view with 10 last measurements and addition box
#
