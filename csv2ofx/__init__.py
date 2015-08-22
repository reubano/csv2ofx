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
from dateutil.parser import parse
from tabutils import process
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
        # map(self.__setattr__, kwargs.keys(), kwargs.values())
        mapping = mapping or {}
        [self.__setattr__(k, v) for k, v in mapping.items()]
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

        return value

    def skip_transaction(self, tr):
        # if transaction is not in the specified date range, skip it
        return not (self.end >= parse(self.get('date', tr)) >= self.start)

    def convert_amount(self, tr):
        raw_amount = str(self.get('amount', tr))
        after_comma = process.afterish(raw_amount, exclude='.')
        after_decimal = process.afterish(raw_amount, '.', ',')

        if after_comma in {-1, 0, 3} and after_decimal in {-1, 0, 1, 2}:
            amount = process.decimalize(raw_amount)
        elif after_comma in {-1, 0, 1, 2} and after_decimal in {-1, 0, 3}:
            kwargs = {'thousand_sep': '.', 'decimal_sep': ','}
            amount = process.decimalize(raw_amount, **kwargs)
        else:
            print('after_comma', after_comma)
            print('after_decimal', after_decimal)
            raise TypeError('Invalid number format for `%s`.' % raw_amount)

        return amount

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
            {u'account': u'account', u'check_num': None, u'account_id': \
'e268443e43d93dab7ebef303bbe9642f', u'payee': u'payee', u'tran_class': None, \
u'split_account': u'Checking', u'notes': u'notes', u'tran_type': u'debit', \
u'split_account_id': '195917574edc9b6bbeb5be9785b6a479', u'bank_id': \
'e268443e43d93dab7ebef303bbe9642f', u'currency': u'USD', u'amount': \
Decimal('-1000.00'), u'date': datetime.datetime(2010, 6, 12, 0, 0), u'id': \
'b045c43277d797f8a6993ee6668958d9', u'bank': u'account', u'desc': \
u'description'}
        """
        currency = self.get('currency', tr, 'USD')
        account = self.get('account', tr)
        account_id = self.get('account_id', tr, md5(account))
        bank = self.get('bank', tr, account)
        bank_id = self.get('bank_id', tr, md5(bank))

        raw_amount = str(self.get('amount', tr))
        amount = self.convert_amount(tr)
        tran_type = self.get('tran_type', tr)

        if tran_type:
            amount = -1 * amount if tran_type.lower() == 'debit' else amount
        else:
            tran_type = 'CREDIT' if amount > 0 else 'DEBIT'

        date = self.get('date', tr)
        payee = self.get('payee', tr)
        desc = self.get('desc', tr)
        check_num = self.get('check_num', tr)
        split_account = self.get('split_account', tr, '')
        _details = [date, raw_amount, payee, split_account, desc]
        details = utils.filter_join(_details)
        tran_id = self.get('id', tr, check_num) or md5(details)

        # TODO: find where to put notes and tran_class
        return {
            'date': parse(date),
            'currency': currency,
            'bank': bank,
            'bank_id': bank_id,
            'account': account,
            'account_id': account_id,
            'amount': amount,
            'payee': payee,
            'desc': desc,
            'notes': self.get('notes', tr),
            'tran_class': self.get('class', tr),
            'id': tran_id,
            'check_num': check_num,
            'tran_type': tran_type,
            'split_account': split_account,
            'split_account_id': md5(split_account),
        }
