Sofort
======

Building brick to ease Sofort payments in your application.

Installation
------------

::

    $ pip install git+ssh://git@bitbucket.org/spreenauten/python-sofort.git


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
Sofort server will send GET-request to ``notification_urls`` as soon as
transaction status will be changed. You can use ``sofort.TRANSACTION_ID`` in
URL params, so notification url could be like this:

::

    'http://mysite.de/notify.php?trn=' + sofort.TRANSACTION_ID

it will be substitute to something like

::

    http://mysite.de/notify.php?trn=123456-321321-56A29EC6-066A

So you can catch transaction ID and check it's status:

::

    >>> details = client.details('123456-321321-56A29EC6-066A')
    >>> vars(details.transaction_details)
    {'amount': 200.0,
     'amount_refunded': 0.0,
     'costs': <Element costs at 0x108207c68>,
     'currency_code': 'EUR',
     'email_customer': u'',
     'exchange_rate': 1.0,
     'language_code': 'en',
     'payment_method': 'su',
     'phone_customer': u'',
     'project_id': 123456,
     'reasons': <Element reasons at 0x108207998>,
     'recipient': <Element recipient at 0x108207b90>,
     'sender': <Element sender at 0x108207b48>,
     'status': 'untraceable',
     'status_history_items': <Element status_history_items at 0x108207cf8>,
     'status_modified': '2016-01-24T15:21:24+01:00',
     'status_reason': 'sofort_bank_account_needed',
     'su': <Element su at 0x108207cb0>,
     'test': 1,
     'time': '2016-01-24T15:21:24+01:00',
     'transaction': '123456-321321-56A29EC6-066A',
     'user_variables': u''}

Testing
-------

::

    $ pip install -e '.[test]' # to obtain mock library
    $ python setup.py test

Be careful, transaction ID contains some sensitive data:

::

    123456-321321-56A29EC6-066A
    ^^^^^^ ^^^^^^
       |      '---------------- Project ID
       '----------------------- User ID

Of course this data should be visible to customer on payment page, and it's
almost useless without API key. Still I think it's bad idea to store unmasked
transaction IDs in repo.

.. _Reference: https://www.sofort.com/integrationCenter-eng-DE/content/view/full/2513
