import xmltodict
from warnings import warn

import iso8601

from schematics.models import Model
from schematics.types import (URLType, StringType, IntType, BooleanType,
                              DateTimeType, DecimalType, EmailType)
from schematics.types.compound import ListType, ModelType

from sofort.exceptions import RequestError, RequestErrors, SofortWarning
from sofort.internals import as_list

def response(xmlstr):
    result = xmltodict.parse(xmlstr)
    # only one root element is allowed in XML
    for root, value in result.iteritems():
        if value is None:
            return None
        factory = factories[root]
        return factory(value)


class ForcedListType(ListType):
    def to_native(self, value):
        return [self.field.to_native(item) for item in as_list(value)]


class SofortListType(ForcedListType):
    def __init__(self, field_name='', *args, **kwargs):
        ForcedListType.__init__(self, *args, **kwargs)
        self.field_name = field_name

    def to_native(self, value):
        return ForcedListType.to_native(self, value[self.field_name])


class Iso8601DateTimeType(DateTimeType):
    def to_native(self, value):
        return iso8601.parse_date(value)


class ErrorModel(Model):
    code = IntType()
    message = StringType()
    field = StringType()


class WarningModel(ErrorModel):
    def import_data(self, *args, **kwargs):
        ErrorModel.import_data(self, *args, **kwargs)
        warn(SofortWarning(**self.to_primitive()))


class SuErrorModel(Model):
    errors = SofortListType('error', ModelType(ErrorModel))


class RootErrorsModel(Model):
    error = ForcedListType(ModelType(ErrorModel))
    su = ModelType(SuErrorModel)


class NewTransactionModel(Model):
    transaction = StringType()
    payment_url = URLType()
    warnings = SofortListType('warning', ModelType(WarningModel))


class BankAccountModel(Model):
    holder = StringType()
    account_number = StringType()
    bank_code = StringType()
    bank_name = StringType()
    bic = StringType()
    iban = StringType()
    country_code = StringType()


class CostsModel(Model):
    fees = DecimalType()
    currency_code = StringType()
    exchange_rate = DecimalType()


class SuModel(Model):
    consumer_protection = BooleanType()


class StatusHistoryItemModel(Model):
    status = StringType()
    status_reason = StringType()
    time = Iso8601DateTimeType()


class TransactionDetailsModel(Model):
    project_id = IntType()
    transaction = StringType()
    test = BooleanType()
    time = Iso8601DateTimeType()
    status = StringType()
    status_reason = StringType()
    status_modified = Iso8601DateTimeType()
    payment_method = StringType()
    language_code = StringType()
    amount = DecimalType()
    amount_refunded = DecimalType()
    currency_code = StringType()
    reasons = SofortListType('reason', StringType())
    user_variables = SofortListType('user_variable', StringType())
    sender = ModelType(BankAccountModel)
    recipient = ModelType(BankAccountModel)
    email_customer = EmailType()
    phone_customer = StringType()
    exchange_rate = DecimalType()
    costs = ModelType(CostsModel)
    su = ModelType(SuModel)
    status_history_items = SofortListType('status_history_item',
                                          ModelType(StatusHistoryItemModel))


def transaction_list(transactions):
    return [TransactionDetailsModel(transact)
                for transact
                in as_list(transactions['transaction_details'])]


def error_handler(data):
    root = RootErrorsModel(data)
    errors = [RequestError(**error_item) for error_item in root.error]
    if root.su:
        errors.extend([RequestError(**error_item)
                            for error_item
                            in root.su.errors])
    raise RequestErrors(errors)


factories = {
    'errors': error_handler,
    'transactions': transaction_list,
    'new_transaction': NewTransactionModel,
}
