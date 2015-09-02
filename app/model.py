import dataset
from stuf import stuf

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
              "description": "ferrosulfaattimittarin prosenttilukema"},
             "ferrosulphate_addition_kg":
             {"finnish": "Ferrosulfaatin lisäys", "min": 1, "max": 1000,
              "description":
              "Ferrosulfaatin määrän lisäys kiloina."}}


def get_table():
    db = dataset.connect('sqlite:///measurements.db', row_type=stuf)
    return db['measurements']


def add_measurement(data):
    measurements = get_table()
    measurements.insert(data)


def read_measurements():
    measurements = get_table()
    return measurements.all()


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
    import ipdb; ipdb.set_trace()
    return 0
