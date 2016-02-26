import datetime
import requests
from lxml import objectify

import sofort.exceptions
import sofort.internals
import sofort.xml

from _version import __version__

API_URL = 'https://api.sofort.com/api/xml'
TRANSACTION_ID = '-TRANSACTION-'

TRANSACTION_HISTORY_LIMIT = datetime.timedelta(days=30)


class Client(object):
    def __init__(self, user_id, api_key, project_id, **kwargs):
        self.config = sofort.internals.Config(
            base_url=API_URL,
            user_id=user_id,
            api_key=api_key,
            project_id=project_id,
            interface_version='python_sofort_v.{}'.format(__version__),
            currency_code='EUR',
            country_code='DE',
            success_link_redirect=True,
        ).update(kwargs)

    def payment(self, amount, **kwargs):
        """Get payment URL and transaction ID

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
        if isinstance(transaction_ids, basestring):
            transaction_ids = [transaction_ids]
        return self._request(sofort.xml.transaction_request_by_ids(transaction_ids))

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
        sofort.xml.transaction_request_by_params(params)
        raise NotImplementedError()

    def _request(self, data, config=None):
        if config is None:
            config = self.config.clone()

        # Actually there are no unicode characters in response
        response = str(self._request_xml(config, data))
        result = objectify.fromstring(response)
        if hasattr(result, 'error'):
            raise sofort.exceptions.RequestErrors(result)
        else:
            return result

    def _request_xml(self, config, data):
        r = requests.post(config.base_url,
                          auth=(config.user_id, config.api_key),
                          data=data)

        if r.status_code == 200:
            return r.text
        elif r.status_code == 401:
            raise sofort.exceptions.UnauthorizedError()
        else:
            raise NotImplementedError(
                'Unknown response status: {}'.format(r.status_code)
            )
