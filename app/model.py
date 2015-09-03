import dataset
from operator import itemgetter
from time import strptime, mktime
from datetime import date
from flask.ext.script import Command
from utils import send_mail
from secret import mail_addresses, server_address

entry_model = \
            {"silt_active_ml_per_l":
             {"finnish": "Aktiivilietemittaus", "min": 0, "max": 1000,
              "description": "aktiivilietteen mittaus (ml per litra)"},
             "silt_surplus_removal_l":
             {"finnish": "Poistopumppaus", "min": 1, "max": 1000,
              "description": "ylijäämälietteen poistomäärä litroina"},
             "pump_usage_hours":
             {"finnish": "Pumpun käyttötunnit", "min": 1, "max": 9999999,
              "description": "pumpun käyttötuntilaskurin lukema"},
             "water_quality":
             {"finnish": "Kirkasvesinäyte", "min": 1, "max": 5,
              "description":
              "kirkasveden laatu asteikolla 1-5 (1 on parhain)"},
             "ferrosulphate_level_percent":
             {"finnish": "Ferrosulfaatin määrä", "min": 0, "max": 100,
              "description": "ferrosulfaatin määrä sentteinä"},
             "ferrosulphate_addition_kg":
             {"finnish": "Ferrosulfaatin lisäys", "min": 1, "max": 1000,
              "description":
              "Ferrosulfaatin määrän lisäys kiloina."}}


def read_date_str(timestr):
    '''Read date string that's stored in database'''
    st = strptime(timestr, "%Y-%m-%d")
    return date.fromtimestamp(mktime(st))


def get_table():
    db = dataset.connect('sqlite:///measurements.db', row_type=dict)
    return db['measurements']


def add_measurement(data):
    measurements = get_table()
    measurements.insert(data)


def read_measurements():
    '''Return all measurements from db. Sorted primarily by date, secondarily
    by id.'''
    measurements = get_table()
    all = [a for a in measurements.all()]
    all_sorted = sorted(all, key=itemgetter('date', 'id'), reverse=True)
    return all_sorted


def get_measurement(id):
    measurements = get_table()
    return measurements.find_one(id=id)


def update_measurement(data):
    '''Update entry by id.'''
    measurements = get_table()
    print(data)
    measurements.update(data, ['id'])


def delete_measurement(id):
    measurements = get_table()
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
