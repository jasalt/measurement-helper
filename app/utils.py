from functools import partial
import requests
from secret import mailgun_key


class DoTo(object):
    # https://nvbn.github.io/2014/09/18/doto-in-python/
    def __init__(self, obj):
        self._obj = obj

    def _do(self, name, *args, **kwargs):
        getattr(self._obj, name)(*args, **kwargs)
        return self

    def __getattr__(self, item):
        return partial(self._do, item)


def send_mail(address, content):
    '''Send mail via Mailgun API.'''
    return requests.post(
        "https://api.mailgun.net/v3/sandbox9ad2bba97910488e831f2e314e32ed0f." +
        "mailgun.org/messages",
        auth=("api", mailgun_key),
        data={"from": '''Milkilo Huomautus
        <mailgun@sandbox9ad2bba97910488e831f2e314e32ed0f.mailgun.org>''',
              "to": address,
              "subject": "Automaattinen huomautus Milkilo järjestelmästä",
              "text": content})
