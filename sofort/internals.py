import copy

class Config(object):
    def __init__(self, **params):
        self.update(params)

    def has(self, key):
        return key in self.__dict__.keys()

    def update(self, dict_):
        self.__dict__.update(dict_)
        return self

    def clone(self):
        return Config(**copy.deepcopy(self.__dict__))
