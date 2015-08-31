from functools import partial


class DoTo(object):
    # https://nvbn.github.io/2014/09/18/doto-in-python/
    def __init__(self, obj):
        self._obj = obj

    def _do(self, name, *args, **kwargs):
        getattr(self._obj, name)(*args, **kwargs)
        return self

    def __getattr__(self, item):
        return partial(self._do, item)

