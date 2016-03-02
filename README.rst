Sofort
======

.. rubric:: Building brick to ease Sofort payments in your application.

This library is still in hard development so when in doubt, check original
Sofort Reference_.

.. image:: https://travis-ci.org/spreecode/python-sofort.svg?branch=master
  :target: https://travis-ci.org/spreecode/python-sofort
  :alt: Build Status

.. image:: https://coveralls.io/repos/github/spreecode/python-sofort/badge.svg?branch=master
  :target: https://coveralls.io/github/spreecode/python-sofort?branch=master
  :alt: Coverage

.. image:: https://landscape.io/github/spreecode/python-sofort/master/landscape.svg?style=flat
  :target: https://landscape.io/github/spreecode/python-sofort/master
  :alt: Code Health

Installation
------------

::

    $ pip install git+ssh://git@github.com/spreecode/python-sofort.git

Usage
-----

::

    import sofort
    import some_abstract_http_framework as webserver
    import some_abstract_data_storage as db

    client = sofort.Client(my_user_id, my_api_key, my_project_id,
        success_url='https://mysite.de/thanks.html',
        abort_url='https://mysite.de/abort_payment.html',
        notification_urls={
            'default': 'https://mysite.de/notify.php?' + sofort.TRANSACTION_ID
        })

    payment_data = client.payment(
        200,
        reasons=[
            'Invoice 0001 payment',
            sofort.TRANSACTION_ID
        ]
    )

    db.save_transaction(payment_data.transaction)
    webserver.redirect(payment_data.payment_url)

When payment is proccessed, client will be redirected to ``success_url`` and
Sofort server will send POST-request to ``notification_urls`` as soon as
transaction status will be changed. You can use ``sofort.TRANSACTION_ID`` in
URL params, so notification url could be like this: ::

    'http://mysite.de/notify.php?trn=' + sofort.TRANSACTION_ID

it will be substituted to something like ::

    http://mysite.de/notify.php?trn=123456-321321-56A29EC6-066A

So you can catch transaction ID and check it's status (all responses are
wrapped with Schematics_ models) ::

    >>> details = client.details('123456-321321-56A29EC6-066A')
    >>> details[0]._data
    {'amount': Decimal('234.00'),
     'amount_refunded': Decimal('0.00'),
     'costs': <CostsModel: CostsModel object>,
     'currency_code': u'EUR',
     'email_customer': None,
     'exchange_rate': Decimal('1.0000'),
     'language_code': u'de',
     'payment_method': u'su',
     'phone_customer': None,
     'project_id': 123456,
     'reasons': [u'Invoice 52'],
     'recipient': <BankAccountModel: BankAccountModel object>,
     'sender': <BankAccountModel: BankAccountModel object>,
     'status': u'untraceable',
     'status_history_items': [<StatusHistoryItemModel: StatusHistoryItemModel object>],
     'status_modified': datetime.datetime(2016, 2, 28, 10, 1, 52, tzinfo=<FixedOffset u'+01:00' datetime.timedelta(0, 3600)>),
     'status_reason': u'sofort_bank_account_needed',
     'su': <SuModel: SuModel object>,
     'test': True,
     'time': datetime.datetime(2016, 2, 28, 10, 1, 52, tzinfo=<FixedOffset u'+01:00' datetime.timedelta(0, 3600)>),
     'transaction': u'123456-321321-56A29EC6-066A',
     'user_variables': None}


Testing
-------

::

    $ pip install -e '.[test]' # to obtain mock library
    $ python setup.py test

Be careful, transaction ID contains some sensitive data ::

    123456-321321-56A29EC6-066A
    ^^^^^^ ^^^^^^
       |      |
    User ID   |
          Project ID

Of course this data will be visible to customer on payment page, and it's
almost useless without API key. Still I think it's bad idea to store unmasked
transaction IDs in repo.

.. _Reference: https://www.sofort.com/integrationCenter-eng-DE/content/view/full/2513
.. _Schematics: https://github.com/schematics/schematics
