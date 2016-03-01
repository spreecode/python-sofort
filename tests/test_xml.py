import datetime

import unittest
from doctest import Example
from lxml.doctestcompare import LXMLOutputChecker

import sofort.xml
import sofort.internals


class XmlTest(unittest.TestCase):
    """
    http://stackoverflow.com/questions/321795/comparing-xml-in-a-unit-test-in-python
    """
    def assertXmlEqual(self, want, got):
        checker = LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(Example("", want), got, 0)
            raise AssertionError(message)


class TestSofortXML(XmlTest):
    def test_multipay(self):
        conf = sofort.internals.Config(
            amount=777,
            project_id=123456,
            currency_code='EUR',
            success_url = 'http://success.url?trn={}'.format(sofort.TRANSACTION_ID),
            abort_url = 'http://abort.url?trn={}'.format(sofort.TRANSACTION_ID),
            notification_urls={
                'default': 'http://notify.url?trn={}'.format(sofort.TRANSACTION_ID),
                'loss': 'http://notify.url?trn={}'.format(sofort.TRANSACTION_ID),
                'refund': 'http://notify.url?trn={}'.format(sofort.TRANSACTION_ID)
            },
            reasons=[
                'Invoice 0001 payment',
                sofort.TRANSACTION_ID
            ]
        )
        self.assertXmlEqual(MULTIPAY_SAMPLE, sofort.xml.multipay(conf))

    def test_transactions_request_by_id(self):
        ids = [
            '99999-53245-5483-4891',
            '99999-53245-5741-1896'
        ]

        self.assertXmlEqual(
            TRANS_BY_IDS_SAMPLE,
            sofort.xml.transaction_request_by_params({'transaction': ids})
        )

    def test_transactions_request_by_params(self):
        params = {
            'from_time': datetime.datetime(2007, 12, 6, 16, 29, 43, 79043),
            'to_time': datetime.datetime(2007, 12, 7, 16, 29, 43, 79043),
            'number': 10
        }

        self.assertXmlEqual(
            TRANS_BY_FILTER_SAMPLE,
            sofort.xml.transaction_request_by_params(params)
        )


MULTIPAY_SAMPLE = """
<multipay>
    <project_id>123456</project_id>
    <amount>777</amount>
    <currency_code>EUR</currency_code>
    <success_url>http://success.url?trn=-TRANSACTION-</success_url>
    <abort_url>http://abort.url?trn=-TRANSACTION-</abort_url>
    <reasons>
        <reason>Invoice 0001 payment</reason>
        <reason>-TRANSACTION-</reason>
    </reasons>
    <notification_urls>
        <notification_url>http://notify.url?trn=-TRANSACTION-</notification_url>
        <notification_url notify_on="loss,refund">http://notify.url?trn=-TRANSACTION-</notification_url>
    </notification_urls>
    <su />
</multipay>
"""

TRANS_BY_IDS_SAMPLE = """
<transaction_request version="2">
    <transaction>99999-53245-5483-4891</transaction>
    <transaction>99999-53245-5741-1896</transaction>
</transaction_request>
"""

TRANS_BY_FILTER_SAMPLE = """
<transaction_request version="2">
    <from_time>2007-12-06T16:29:43.079043</from_time>
    <to_time>2007-12-07T16:29:43.079043</to_time>
    <number>10</number>
</transaction_request>
"""
