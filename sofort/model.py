import xmltodict
import copy
from warnings import warn

from sofort.exceptions import RequestError, RequestErrors, SofortWarning
from sofort.internals import as_list

def transaction_list(transaction_details):
    return [TransactionInfo(**transact)
                for transact
                in as_list(transaction_details)]


def error_list(error=None, **data):
    if isinstance(error, list):
        raise RequestErrors([RequestError(**error_item) for error_item in error])
    else:
        raise RequestError(**error)


def response(xmlstr):
    result = xmltodict.parse(xmlstr)
    # only one root element is allowed in XML
    for root, value in result.iteritems():
        if value is None:
            return None
        return factories[root](**value)


def is_sofort_list(value, collection_name):
    if len(value.keys()) != 1:
        return False

    item_key_name = value.keys()[0]
    if collection_name != item_key_name + 's':
        return False

    return True


class OpenStruct(object):
    def _load(self, data):
        for key, value in data.iteritems():
            setattr(self, key, self.__load_value(value, key))

    def __load_value(self, value, colname=''):
        if isinstance(value, list):
            return [self.__load_value(item) for item in value]

        elif isinstance(value, dict) and is_sofort_list(value, colname):
            item_name = value.keys()[0]
            return self.__load_value(as_list(value[item_name]))

        elif isinstance(value, dict):
            container = OpenStruct()
            container._load(value)
            return container

        else:
            return value

class BaseResponse(OpenStruct):
    def __init__(self, warnings=None, **payload):
        if warnings:
            for warning in as_list(warnings['warning']):
                warn(SofortWarning(**warning))


class TransactionInfo(BaseResponse):
    def __init__(self, **payload):
        super(TransactionInfo, self).__init__(**payload)
        self._load(payload)


class Payment(BaseResponse):
    def __init__(self, **payload):
        super(Payment, self).__init__(**payload)
        self._load(payload)


factories = {
    'errors': error_list,
    'transactions': transaction_list,
    'new_transaction': Payment,
}
