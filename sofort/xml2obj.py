"""Yet another XML to python object converter with Sofort schema in mind"""

from abc import ABCMeta
from argparse import Namespace
import xmltodict


class AnyList:
    __metaclass__ = ABCMeta

AnyList.register(list)
AnyList.register(tuple)


def fromstring(xmlstr, skip_root=True, collapse_lists=True):
    result = xmltodict.parse(xmlstr)

    if skip_root:
        (_, result) = result.popitem()

    if collapse_lists:
        __collapse_lists(result)

    return obj(result)


class obj(Namespace):
    """
    http://stackoverflow.com/a/1305682
    """
    def __init__(self, d):
        for a, b in d.iteritems():
            if isinstance(b, AnyList):
               setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, obj(b) if isinstance(b, dict) else b)


def __collapse_lists(collection):
    """
    When dict has items like dict['items']['item'] containing lists,
    then move inner ['item'] value to the ['items'].

    When `item` value is not list - it will be converted to list

    Match only when inner name is single form of container:
        (reasons - reason)
        (names - name)
        (items - item)

    Do nothing when parent container has different children names:
        (items:
            - item
            - item
            - something)
    """
    if not isinstance(collection, dict):
        return

    for k, v in collection.iteritems():
        if isinstance(v, dict):
            __collapse_lists(v)
            if len(v) == 1 and k == u"{}s".format(v.keys()[0]):
                inner = v.values().pop()
                if not isinstance(inner, AnyList):
                    inner = [inner]
                collection[k] = inner

        elif isinstance(v, AnyList):
            for item in v:
                __collapse_lists(item)
