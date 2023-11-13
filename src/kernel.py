from model.translator import translate
import json

class _dict(dict):
    """dict like object that exposes keys as attributes"""

    __slots__ = ()
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    __setstate__ = dict.update

    def __getstate__(self):
        return self

    def update(self, *args, **kwargs):
        """update and return self -- the missing dict feature in python"""

        super().update(*args, **kwargs)
        return self

    def copy(self):
        return _dict(self)

def _(text, lang="es-VE"):
    return translate(text, lang)

def get_config():

    config = None
    with open("config.json", "r", encoding="utf-8") as f:
        data_json = json.loads(f.read())
    try:
        config = _dict(data_json)
    except Exception as e:
        pass
    return _dict() if not config else config