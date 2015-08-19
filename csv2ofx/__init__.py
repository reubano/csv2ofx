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
    absolute_import, division, print_function, with_statement,
    unicode_literals)

__title__ = 'csv2ofx'
__package_name__ = 'csv2ofx'
__author__ = 'Reuben Cummings'
__description__ = 'converts a csv file of transactions to an ofx or qif file'
__email__ = 'reubano@gmail.com'
__version__ = '0.14.0'
__license__ = 'MIT'
__copyright__ = 'Copyright 2015 Reuben Cummings'

import tabutils
import hashlib

from datetime import datetime as dt
from itertools import starmap
from dateutil.parser import parse

md5 = lambda content: hashlib.md5(content).hexdigest()

class File(object):
    def __init__(self, mapping, **kwargs):
        # map(self.__setattr__, kwargs.keys(), kwargs.values())
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
        # transaction is not in the specified date range, skip it
        return not (self.end >= parse(self.get('date', tr)) >= self.start)

    def convert_amount(self, tr):
        raw_amount = self.get('amount', tr)
        after_comma = tabutils.afterish(raw_amount, ',')
        after_decimal = tabutils.afterish(raw_amount, '.')

        if after_comma in (-1, 0, 3) and after_decimal in (-1, 0, 2):
            amount = tabutils.decimalize(raw_amount)
        elif after_comma in (-1, 0, 2) and after_decimal in (-1, 0, 3):
            kwargs = {'thousand_sep': '.', 'decimal_sep': ','}
            amount = tabutils.decimalize(raw_amount, **kwargs)
        else:
            raise TypeError('Invalid number format for %s.' % raw_amount)

        return amount

    def transaction_data(self, tr):
        """ gets transaction data

        Args:
            tr (List[str]): the transaction
            time_stamp (str): the time stamp

        Kwargs:

        Returns:
            (List[str]): the QIF content

        Examples:
            >>> ({'Transaction Type': 'debit', 'amount': 1000.00, 'Date': '06/12/10', 'Description': 'payee', 'Original Description': 'description', 'Notes': 'notes', 'Category': 'Checking', 'Account Name': 'account'}) == {'amount': '-1000', 'Payee': 'payee', 'Date': '06/12/10', 'desc': 'description notes', 'id': '4fe86d9de995225b174fb3116ca6b1f4', 'check_num': None, 'type': 'debit', 'split_account': 'Checking', 'split_account_id': '195917574edc9b6bbeb5be9785b6a479'}
        """
        args = [self.account_types, self.def_type]

        currency = self.get('currency', tr)
        account = self.get('account', tr)
        account_id = self.get('account_id', tr, md5(account))
        bank = self.get('bank', tr, account)
        bank_id = self.get('bank_id', tr, md5(bank))
        account_type = utils.get_account_type(account, *args)

        raw_amount = self.get('amount', tr)
        amount = self.convert_amount(tr)
        tran_type = self.get('tran_type', tr)

        if tran_type:
            amount = '-%s' % amount if tran_type.lower() == 'debit' else amount
        else:
            tran_type = 'CREDIT' if amount > 0 else 'DEBIT'

        date = self.get('date', tr)
        payee = self.get('payee', tr)
        desc = self.get('desc', tr)
        check_num = self.get('check_num', tr)
        split_account = self.get('split_account', tr, '')
        split_account_type = utils.get_account_type(split_account, *args)
        details = utils.filter_join([date, raw_amount, payee, split_account, desc])
        tran_id = self.get('id', tr, check_num) or md5(details)

        return {
            'time_stamp': parse(self.get('date', tr)),
            'currency': currency,
            'bank': bank,
            'bank_id': bank_id,
            'account': account,
            'account_id': account_id,
            'account_type': account_type,
            'amount': amount,
            'payee': payee,
            'date': date,
            'desc': desc,
            'notes': self.get('notes', tr),  # TODO: find where to put this
            'tran_class': self.get('class', tr), # TODO: find where to put this,
            'id': tran_id,
            'check_num': check_num,
            'tran_type': tran_type,
            'split_account': split_account,
            'split_account_id': md5(split_account),
            'split_account_type': split_account_type,
        }
