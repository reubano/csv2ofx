#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
csv2ofx
~~~~~~~

Converts a csv file to ofx and qif

Examples:
    literal blocks::

        python example_google.py

Attributes:
    ENCODING (str): Default file encoding.
"""

from __future__ import (
    division, print_function, with_statement,
    unicode_literals)

import hashlib
import sys

from os import path as p
from datetime import datetime as dt
from operator import itemgetter
from dateutil.parser import parse
from . import utils

__title__ = 'csv2ofx'
__package_name__ = 'csv2ofx'
__author__ = 'Reuben Cummings'
__description__ = 'converts a csv file of transactions to an ofx or qif file'
__email__ = 'reubano@gmail.com'
__version__ = '0.14.0'
__license__ = 'MIT'
__copyright__ = 'Copyright 2015 Reuben Cummings'

md5 = lambda content: hashlib.md5(content).hexdigest()


class File(object):
    def __init__(self, mapping=None, **kwargs):
        mapping = mapping or {}
        [self.__setattr__(k, v) for k, v in mapping.items()]

        if kwargs.get('split_account'):
            self.split_account = itemgetter(kwargs['split_account'])
        else:
            self.split_account = ''

        self.start = kwargs.get('start', dt.now())
        self.end = kwargs.get('end', dt.now())

    def get(self, name, tr=None, default=None):
        try:
            attr = getattr(self, name)
        except AttributeError:
            value = default
        else:
            try:
                value = attr(tr)
            except TypeError:
                value = attr
            except KeyError:
                value = default

        return value

    def skip_transaction(self, tr):
        # if transaction is not in the specified date range, skip it
        return not (self.end >= parse(self.get('date', tr)) >= self.start)

    def convert_amount(self, tr):
        return utils.convert_amount(self.get('amount', tr))

    def transaction_data(self, tr):
        """ gets transaction data

        Args:
            tr (List[str]): the transaction

        Kwargs:

        Returns:
            (List[str]): the QIF content

        Examples:
            >>> from mappings.mint import mapping
            >>> tr = {'Transaction Type': 'debit', 'Amount': 1000.00, \
'Date': '06/12/10', 'Description': 'payee', 'Original Description': \
'description', 'Notes': 'notes', 'Category': 'Checking', 'Account Name': \
'account'}
            >>> File(mapping).transaction_data(tr)
            {u'account_id': 'e268443e43d93dab7ebef303bbe9642f', u'memo': \
u'description notes', u'split_account_id': \
'195917574edc9b6bbeb5be9785b6a479', u'currency': u'USD', u'date': \
datetime.datetime(2010, 6, 12, 0, 0), u'id': \
'0b9df731dbf286154784222755482d6f', u'bank': u'account', u'account': \
u'account', u'split_account': u'Checking', u'bank_id': \
'e268443e43d93dab7ebef303bbe9642f', u'class': None, u'payee': u'payee', \
u'amount': Decimal('-1000.00'), u'check_num': None, u'type': u'debit'}
        """
        account = self.get('account', tr)
        split_account = self.get('split_account', tr, '')
        bank = self.get('bank', tr, account)

        raw_amount = str(self.get('amount', tr))
        amount = self.convert_amount(tr)
        _type = self.get('type', tr)

        if _type:
            amount = -1 * amount if _type.lower() == 'debit' else amount
        else:
            _type = 'CREDIT' if amount > 0 else 'DEBIT'

        date = self.get('date', tr)
        payee = self.get('payee', tr)
        desc = self.get('desc', tr)
        notes = self.get('notes', tr)

        if desc and notes:
            memo = '%s %s' % (desc, notes)
        else:
            memo = desc or notes

        check_num = self.get('check_num', tr)
        details = utils.filter_join([date, raw_amount, payee, memo])

        return {
            'date': parse(date),
            'currency': self.get('currency', tr, 'USD'),
            'bank': bank,
            'bank_id': self.get('bank_id', tr, md5(bank)),
            'account': account,
            'account_id': self.get('account_id', tr, md5(account)),
            'split_account': split_account,
            'split_account_id': md5(split_account),
            'amount': amount,
            'payee': payee,
            'memo': memo,
            'class': self.get('class', tr),
            'id': self.get('id', tr, check_num) or md5(details),
            'check_num': check_num,
            'type': _type,
        }
