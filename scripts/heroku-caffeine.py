# "Free dynos are allowed 18 hours awake per 24 hour period."
# This script keeps the free Heroku dyno awake during daytime.
# During night, user needs to wait ~10s for server wakeup.

# Tested on with Python 2.7 and Python 3.4. Depends on UNIX.

# Configuration & Usage:
# - Setup server endpoints in KEEP_AWAKE_SERVERS env var, separated by ':'.
# - Schedule script with crontab, eg. run every 30 min:
#   0,30 * * * * python path/to/heroku-caffeine.py
# - Customize script timezone and sleeping hours to your liking

###

import os
import time
from datetime import datetime
import urllib2

# Current machine time is
# time.strftime('%X %x %Z')

# Set environment timezone
# Valid timezones: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
os.environ['TZ'] = 'Europe/Helsinki'                    # <- Customize timezone
time.tzset()
time.now()
now = datetime.now()

sleeping_hours = [22, 23, 0, 1, 2, 3, 4, 5]  # <- Customize dyno sleeping hours

if (now.hour in sleeping_hours):
    print("Letting Heroku server sleep, time is " + time.strftime('%X %x %Z'))
    return


def wakeup_server(url):
    print("Waking up " + url)
    response = urllib2.urlopen(os.environ['KEEP_AWAKE_SERVERS'])
    return response.read()

# os.environ['KEEP_AWAKE_SERVERS'] = 'testing:stuff'
servers = os.environ['KEEP_AWAKE_SERVERS'].split(':')
map(lambda url: wakeup_server(url), servers)
