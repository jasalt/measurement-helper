from functools import partial
import requests
from time import strptime, mktime
from datetime import date
import os


def get_env(x):
    os.environ.get(x)


class DoTo(object):
    # https://nvbn.github.io/2014/09/18/doto-in-python/
    def __init__(self, obj):
        self._obj = obj

    def _do(self, name, *args, **kwargs):
        getattr(self._obj, name)(*args, **kwargs)
        return self

    def __getattr__(self, item):
        return partial(self._do, item)


def read_date_str(timestr):
    '''Read date string that's stored in database'''
    st = strptime(timestr, "%Y-%m-%d")
    return date.fromtimestamp(mktime(st))


def send_mail(address, content):
    '''Send mail via Mailgun API.'''
    return requests.post(
        "https://api.mailgun.net/v3/sandbox9ad2bba97910488e831f2e314e32ed0f." +
        "mailgun.org/messages",
        auth=("api", get_env('MAILGUN_KEY')),
        data={"from": '''Milkilo Huomautus
        <mailgun@sandbox9ad2bba97910488e831f2e314e32ed0f.mailgun.org>''',
              "to": address,
              "subject": "Automaattinen huomautus Milkilo järjestelmästä",
              "text": content})
