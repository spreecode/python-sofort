import datetime
import requests

import sofort.xml

from sofort.exceptions import UnauthorizedError
from sofort.internals import Config, as_list
from sofort import model

from _version import __version__

API_URL = 'https://api.sofort.com/api/xml'
TRANSACTION_ID = '-TRANSACTION-'

TRANSACTION_HISTORY_LIMIT = datetime.timedelta(days=29)


class Client(object):
    """
    Sofort client. You can pass additional arguments to use them
    as default fall-back values when ``payment(...)`` request is
    performed.

    :param str user_id:
        User ID
    :param str api_key:
        API key
    :param str project_id:
        Project ID
    """
    def __init__(self, user_id, api_key, project_id, **kwargs):
        self.config = Config(
            base_url=API_URL,
            user_id=user_id,
            api_key=api_key,
            project_id=project_id,
            interface_version='python_sofort_v.{0}'.format(__version__),
            currency_code='EUR',
            country_code='DE',
            success_link_redirect=True,
        ).update(kwargs)

    def payment(self, amount, **kwargs):
        """Get payment URL and new transaction ID

        Usage::

            >>> import sofort
            >>> client = sofort.Client('123456', '123456', '123456',
                                       abort_url='https://mysite.com/abort')
            >>> t = client.pay(12, success_url='http://mysite.com?paid')

            >>> t.transaction
            123123-321231-56A3BE0E-ACAB
            >>> t.payment_url
            https://www.sofort.com/payment/go/136b2012718da216af4c20c2ec2f51100c90406e
        """
        params = self.config.clone()\
            .update({ 'amount': amount })\
            .update(kwargs)

        mandatory = ['abort_url', 'reasons', 'success_url']

        for field in mandatory:
            if not params.has(field):
                raise ValueError('Mandatory field "{}" is not specified'.format(field))

        params.reasons = [sofort.internals.strip_reason(reason)
                                for reason
                                in params.reasons]

        return self._request(sofort.xml.multipay(params), params)

    def details(self, transaction_ids):
        request_body = sofort.xml.transaction_request_by_params({
            'transaction': as_list(transaction_ids)
        })
        return self._request(request_body)

    def find_transactions(self, from_time=None, to_time=None, number=10,
                          **extra_params):
        today = datetime.datetime.now()

        if to_time is None:
            to_time = today

        if from_time is None:
            from_time = max(
                today - TRANSACTION_HISTORY_LIMIT,
                to_time - TRANSACTION_HISTORY_LIMIT
            )

        params = {
            'from_time': from_time,
            'to_time': to_time,
            'number': number
        }
        params.update(extra_params)
        request_body = sofort.xml.transaction_request_by_params(params)
        return self._request(request_body)

    def _request(self, data, config=None):
        if config is None:
            config = self.config.clone()

        response = self._request_xml(config, data).encode('utf-8')
        return model.response(response)

    def _request_xml(self, config, data):
        r = requests.post(config.base_url,
                          auth=(config.user_id, config.api_key),
                          data=data)

        if r.status_code == 200:
            return r.text
        elif r.status_code == 401:
            raise UnauthorizedError()
        elif r.status_code == 404:
            raise Exception('Sofort resource not found: {}'.format(
                                config.base_url))
        else:
            raise NotImplementedError(
                'Unknown response status: {}'.format(r.status_code)
            )
