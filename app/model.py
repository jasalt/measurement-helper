# DB operations that are (not performance optimized at all).
import dataset
from operator import itemgetter
from datetime import date
from time import strptime, mktime
from flask.ext.script import Command, prompt_bool
from utils import send_mail, read_date_str
import csv
from toolz.curried import dissoc, first, second
from utils import get_env

mail_addresses = [get_env('ADMIN_EMAIL'), get_env('FLASK_APP_EMAIL')]
server_address = get_env('SERVER_ADDRESS')


def get_db():
    return dataset.connect('sqlite:///database.db', row_type=dict)


def get_table(table_name):
    db = get_db()
    return db[table_name]

entry_model = \
            {"silt_active_ml_per_l":
             {"finnish": "Aktiivilietemittaus", "min": 0, "max": 1000,
              "description": "aktiivilietteen mittaus (ml per litra)",
              "default_interval": 14},
             "silt_surplus_removal_l":
             {"finnish": "Poistopumppaus", "min": 1, "max": 1000,
              "description": "ylijäämälietteen poistomäärä litroina"},
             "pump_usage_hours":
             {"finnish": "Pumpun käyttötunnit", "min": 1, "max": 9999999,
              "description": "pumpun käyttötuntilaskurin lukema"},
             "water_quality":
             {"finnish": "Kirkasvesinäyte", "min": 1, "max": 5,
              "description":
              "kirkasveden laatu asteikolla 1-5 (1 on parhain)",
              "default_interval": 30},
             "ferrosulphate_level_percent":
             {"finnish": "Ferrosulfaatin määrä", "min": 0, "max": 100,
              "description": "ferrosulfaatin määrä sentteinä",
              "default_interval": 14},
             "ferrosulphate_addition_kg":
             {"finnish": "Ferrosulfaatin lisäys", "min": 1, "max": 1000,
              "description":
              "Ferrosulfaatin määrän lisäys kiloina.",
              "default_interval": 30}}


def init_notification_intervals():
    '''Set default notification intervals to DB.'''
    tablename = 'notification_settings'
    print("Checking if table %s exists." % tablename)
    db = get_db()
    if tablename in db.tables:
        print('Table exists. Skipping.')
        return
    print('Table not found, initializing default notification intervals.')

    tbl = db[tablename]

    for k, v in entry_model.items():
        if v.get('default_interval'):
            tbl.insert({'type': k, 'interval_days': v['default_interval']})


def load_csv():
    '''Initialize data from csv.'''
    tablename = 'measurements'
    print("Checking if table %s exists." % tablename)
    tbl = check_table(tablename)

    if tbl is not None:
        print('Table exists, skipping. Drop it first?')
        return

    print('Table not found, initializing with csv data.')
    tbl = get_table(tablename)

    with open('../data/old_entries.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:

            if row['site_id'] is not '3':
                print('Skip entry for test_site')
                continue

            # Remove empty items from dict
            cleaned_row = dict((k, v) for k, v in row.items() if v)
            # Take date part of time string gotten from postgres
            datestr = cleaned_row['date'][:10]
            st = strptime(datestr, "%Y-%m-%d")
            entry_date = date.fromtimestamp(mktime(st))

            typeval_dict = dissoc(cleaned_row, 'id', 'date', 'site_id')
            typeval = first(typeval_dict.items())

            entry = {'type': first(typeval),
                     'value': second(typeval),
                     'date': entry_date}
            print("Adding " + str(entry))
            tbl.insert(entry)


def get_notification_intervals():
    tbl = get_table('notification_settings')
    all = [a for a in tbl.all()]
    return sorted(all, key=itemgetter('type'))


def set_notification_intervals(nis):
    '''Update notification intervals given in iterable.'''
    tbl = get_table('notification_settings')
    print("Setting new notification values")
    for name, val in nis.items():
        tbl.update({'type': name, 'interval_days': val}, ['type'])


def add_measurement(data):
    measurements = get_table('measurements')
    measurements.insert(data)


def read_measurements():
    '''Return all measurements from db. Sorted primarily by date, secondarily
    by id.'''
    measurements = get_table('measurements')
    all = [a for a in measurements.all()]
    all_sorted = sorted(all, key=itemgetter('date', 'id'), reverse=True)
    return all_sorted


def get_measurement(id):
    measurements = get_table('measurements')
    return measurements.find_one(id=id)


def update_measurement(data):
    '''Update entry by id.'''
    measurements = get_table('measurements')
    print(data)
    measurements.update(data, ['id'])


def delete_measurement(id):
    measurements = get_table('measurements')
    print("DELETE " + str(id))
    measurements.delete(id=id)


def check_table(tablename):
    '''Check if database table exists, return it or None if not existing.'''
    print("Checking if table %s exists." % tablename)
    db = get_db()
    if tablename in db.tables:
        return db[tablename]
    else:
        return None


class CheckNotifications(Command):
    '''Check if too long time has passed since last measurement and notify
    user via email. '''
    def run(self):
        msg = ''' Viimeisin merkintä otettu %s  päivää sitten. %s '''
        measurements = get_table('measurements')
        for setting in get_notification_intervals():
            entry_type = setting['type']
            interval = setting['interval_days']

            print("Checking " + entry_type)
            entries = measurements.find(type=entry_type, order_by='-date')

            try:
                last_entry = entries.next()
            except:
                print("Cannot read records.")
                continue

            last_time = read_date_str(last_entry['date'])
            today = date.today()
            diff = today - last_time

            if diff.days > interval:
                print("No measurements in last %s days, notifying user."
                      % interval)
                for address in mail_addresses:
                    if address is not None:
                        send_mail(address,
                                  msg % (str(diff.days), server_address))
            else:
                print('OK')


class InitDb(Command):
    '''Set default notification intervals to DB.'''
    def run(self):
        load_csv()
        init_notification_intervals()


class DropDb(Command):
    '''Drop the measurements table. Prompts user first.'''
    def run(self):
        if prompt_bool("Are you sure you want to lose all your data"):
            mtable = get_table('measurements')
            mtable.drop()
            ntable = get_table('notification_settings')
            ntable.drop()
            print("Tables dropped.")
