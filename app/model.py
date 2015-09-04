# DB operations that are (not performance optimized at all).
import dataset
from operator import itemgetter
from datetime import date
from flask.ext.script import Command, prompt_bool
from utils import send_mail, read_date_str
from secret import mail_addresses, server_address
import csv


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


class InitNotificationIntervals(Command):
    '''Set default notification intervals to DB.'''
    def run(self):
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
                return send_mail(mail_addresses[0],
                                 ''' Viimeisin merkintä otettu %s  päivää sitten.
                                 %s ''' % (str(diff.days), server_address))
            else:
                print('OK')


class DropDb(Command):
    '''Drop the measurements table. Prompts user first.'''
    def run(self):
        if prompt_bool("Are you sure you want to lose all your data"):
            table = get_table('measurements')
            table.drop()
            print("Table 'measurements' dropped.")


class InitFromCsv(Command):
    '''Initialize data from csv.'''
    def run(self):
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
                if row['site_id'] is not 3:
                    print('Skip entry for test_site')
                    continue

                import ipdb; ipdb.set_trace()
                print("Add")
                # if v.get('default_interval'):
                #     tbl.insert({'type': k, 'interval_days': v['default_interval']})
