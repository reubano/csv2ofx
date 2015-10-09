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

import hashlib
import itertools as it

from functools import partial
from datetime import datetime as dt
from operator import itemgetter

from tabutils.process import merge
from dateutil.parser import parse

from . import utils

__title__ = 'csv2ofx'
__package_name__ = 'csv2ofx'
__author__ = 'Reuben Cummings'
__description__ = 'converts a csv file of transactions to an ofx or qif file'
__email__ = 'reubano@gmail.com'
__version__ = '0.18.1'
__license__ = 'MIT'
__copyright__ = 'Copyright 2015 Reuben Cummings'


md5 = lambda content: hashlib.md5(content.encode('utf-8')).hexdigest()


class Content(object):
    def __init__(self, mapping=None, **kwargs):
        """ Base content constructor
        Args:
            mapping (dict): bank mapper (see csv2ofx.mappings)
            kwargs (dict): Keyword arguments

        Kwargs:
            split_header (str): Transaction field to use for the split account.
            start (date): Date from which to begin including transactions.
            end (date): Date from which to exclude transactions.

        Examples:
            >>> from csv2ofx.mappings.mint import mapping
            >>> Content(mapping)  #doctest: +ELLIPSIS
            <csv2ofx.Content object at 0x...>
        """
        mapping = mapping or {}
        [self.__setattr__(k, v) for k, v in mapping.items()]

        if not hasattr(self, 'is_split'):
            self.is_split = False

        if kwargs.get('split_header'):
            self.split_account = itemgetter(kwargs['split_header'])
        else:
            self.split_account = None

        self.start = kwargs.get('start', dt.now())
        self.end = kwargs.get('end', dt.now())

    def get(self, name, tr=None, default=None):
        """ Gets an attribute which could be either a normal attribute,
        a mapping function, or a mapping attribute

        Args:
            name (str): The attribute.
            tr (dict): The transaction. Require if `name` is a mapping function
                (default: None).

            default (str): Value to use if `name` isn't found (default: None).

        Returns:
            (mixed): Either the value of the attribute function applied to the
                transaction, or the value of the attribute.

        Examples:
            >>> from csv2ofx.mappings.mint import mapping
            >>> tr = {'Transaction Type': 'debit', 'Amount': 1000.00}
            >>> start = dt(2015, 1, 1)
            >>> Content(mapping, start=start).get('start')  # normal attribute
            datetime.datetime(2015, 1, 1, 0, 0)
            >>> Content(mapping).get('amount', tr)  # mapping function
            1000.0
            >>> Content(mapping).get('has_header')  # mapping attribute
            True
        """
        try:
            attr = getattr(self, name)
        except AttributeError:
            attr = None
            value = None
        else:
            value = None

        try:
            value = value or attr(tr) if attr else default
        except TypeError:
            value = attr
        except KeyError:
            value = default

        return value

    def skip_transaction(self, tr):
        """ Determines whether a transaction should be skipped (isn't in the
        specified date range)

        Args:
            tr (dict): The transaction.

        Returns:
            (bool): Whether or not to skip the transaction.

        Examples:
            >>> from csv2ofx.mappings.mint import mapping
            >>> tr = {'Date': '06/12/10', 'Amount': 1000.00}
            >>> Content(mapping, start=dt(2010, 1, 1)).skip_transaction(tr)
            False
            >>> Content(mapping, start=dt(2013, 1, 1)).skip_transaction(tr)
            True
        """
        return not (self.end >= parse(self.get('date', tr)) >= self.start)

    def convert_amount(self, tr):
        """ Converts a string amount into a number

        Args:
            tr (dict): The transaction.

        Returns:
            (decimal): The converted amount.

        Examples:
            >>> from csv2ofx.mappings.mint import mapping
            >>> tr = {'Date': '06/12/10', 'Amount': '$1,000'}
            >>> Content(mapping, start=dt(2010, 1, 1)).convert_amount(tr)
            Decimal('1000.00')
        """
        return utils.convert_amount(self.get('amount', tr))

    def transaction_data(self, tr):
        """ gets transaction data

        Args:
            tr (dict): the transaction

        Returns:
            (dict): the QIF content

        Examples:
            >>> from csv2ofx.mappings.mint import mapping
            >>> tr = {'Transaction Type': 'debit', 'Amount': 1000.00, \
'Date': '06/12/10', 'Description': 'payee', 'Original Description': \
'description', 'Notes': 'notes', 'Category': 'Checking', 'Account Name': \
'account'}
            >>> Content(mapping).transaction_data(tr)
            {u'account_id': 'e268443e43d93dab7ebef303bbe9642f', u'memo': \
u'description notes', u'split_account_id': None, u'currency': u'USD', \
u'date': datetime.datetime(2010, 6, 12, 0, 0), u'class': None, u'bank': \
u'account', u'account': u'account', u'split_account': None, u'bank_id': \
'e268443e43d93dab7ebef303bbe9642f', u'id': \
'ee86450a47899254e2faa82dca3c2cf2', u'payee': u'payee', u'amount': \
Decimal('-1000.00'), u'check_num': None, u'type': u'debit'}
        """
        account = self.get('account', tr)
        split_account = self.get('split_account', tr)
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
        memo = '%s %s' % (desc, notes) if desc and notes else desc or notes
        check_num = self.get('check_num', tr)
        details = ''.join(filter(None, [date, raw_amount, payee, memo]))

        return {
            'date': parse(date),
            'currency': self.get('currency', tr, 'USD'),
            'bank': bank,
            'bank_id': self.get('bank_id', tr, md5(bank)),
            'account': account,
            'account_id': self.get('account_id', tr, md5(account)),
            'split_account': split_account,
            'split_account_id': md5(split_account) if split_account else None,
            'amount': amount,
            'payee': payee,
            'memo': memo,
            'class': self.get('class', tr),
            'id': self.get('id', tr, check_num) or md5(details),
            'check_num': check_num,
            'type': _type,
        }

    def gen_trxns(self, groups, collapse=False):
        for group, transactions in groups:
            if self.is_split and collapse:
                # group transactions by `collapse` field and sum the amounts
                groupby = itemgetter(collapse)
                byaccount = utils.group_transactions(transactions, groupby)
                op = lambda values: sum(map(utils.convert_amount, values))
                merger = partial(merge, predicate=self.amount, op=op)
                trxns = [merger(dicts) for _, dicts in byaccount]
            else:
                trxns = transactions

            yield (group, trxns)

    def clean_trxns(self, groups):
        for group, trxns in groups:
            _args = [trxns, self.convert_amount]

            # if it's split, transactions skipping is all or none
            if self.is_split and self.skip_transaction(trxns[0]):
                continue
            elif self.is_split and not utils.verify_splits(*_args):
                raise Exception('Splits do not sum to zero.')
            elif not self.is_split:
                filtered_trxns = it.ifilterfalse(self.skip_transaction, trxns)
            else:
                filtered_trxns = trxns

            if self.is_split:
                main_pos = utils.get_max_split(*_args)[0]
            else:
                main_pos = 0

            keyfunc = lambda enum: enum[0] != main_pos
            sorted_trxns = sorted(enumerate(filtered_trxns), key=keyfunc)
            yield (group, main_pos, sorted_trxns)
