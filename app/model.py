import dataset
from operator import itemgetter
from datetime import date
from flask.ext.script import Command
from utils import send_mail, read_date_str
from secret import mail_addresses, server_address


def get_db():
    return dataset.connect('sqlite:///measurements.db', row_type=dict)


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


class CheckNotifications(Command):
    '''Check if too long time has passed since last measurement.
    TODO Notify user via mail.'''
    def run(self):
        print("Reading DB")
        entries = read_measurements()
        last_entry = entries[0]

        last_time = read_date_str(last_entry['date'])
        today = date.today()
        diff = today - last_time

        if diff.days > 14:
            print("No measurements in last 14 days, notifying user.")
            return send_mail(mail_addresses[0], "Viimeisin merkintä otettu " +
                             str(diff.days) + " päivää sitten. " +
                             server_address)
