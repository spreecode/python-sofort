# -*- coding: utf-8 -*-

import re
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


def strip_reason(reason):
    """
    only the following characters are allowed:
    '0-9', 'a-z', 'A-Z', ' ', '+', ',', '-', '.'.
    Umlauts are replaced, e.g. ä -> ae.

    @see: https://www.sofort.com/integrationCenter-eng-DE/content/view/full/2513#h5-1
    """
    return re.sub('(?u)[^\w\ \+\-\.\,]', '', reason)


def as_list(value):
    if not isinstance(value, list):
        value = [value]
    return value
