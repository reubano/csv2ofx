#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
csv2ofx.utils
~~~~~~~~~~~~~

Provides miscellaneous utility methods

Examples:
    literal blocks::

        python example_google.py

Attributes:
    ENCODING (str): Default file encoding.
"""

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import itertools as it

from operator import itemgetter
from tabutils.fntools import get_separators
from tabutils.convert import to_decimal


def get_account_type(account, account_types, def_type='n/a'):
    """ Detects the account type of a given account

    Args:
        account (str): The account name
        account_types (dict): The account types with matching account names.
        def_type (str): The default account type.

    Returns:
        (str): The resulting account type.

    Examples:
        >>> get_account_type('somecash', {'Cash': ('cash',)})
        u'Cash'
        >>> get_account_type('account', {'Cash': ('cash',)})
        u'n/a'
    """
    _type = def_type

    for key, values in account_types.items():
        if any(v in account.lower() for v in values):
            _type = key
            break

    return _type


def convert_amount(content):
    kwargs = get_separators(content)
    return to_decimal(content, **kwargs)


def get_max_split(splits, keyfunc):
    """ Returns the split in a transaction with the largest absolute value

    Args:
        splits (List[dict]): return value of group_transactions()
        keyfunc (func): key function

    Returns:
        (Tuple[str]): splits collapsed content

    Examples:
        >>> splits = [{'amount': 350}, {'amount': -450}, {'amount': 100}]
        >>> get_max_split(splits, itemgetter('amount'))
        (1, {u'amount': -450})
        >>> splits = [{'amount': 350}, {'amount': -350}]
        >>> get_max_split(splits, itemgetter('amount'))
        (0, {u'amount': 350})
    """
    maxfunc = lambda enum: abs(keyfunc(enum[1]))
    return max(enumerate(splits), key=maxfunc)


def verify_splits(splits, keyfunc):
    """ Verifies that the splits of each transaction sum to 0

    Args:
       splits (dict): return value of group_transactions()
       keyfunc (func): function that returns the transaction amount

    Returns:
        (bool): true on success

    Examples:
        >>> splits = [{'amount': 100}, {'amount': -150}, {'amount': 50}]
        >>> verify_splits(splits, itemgetter('amount'))
        True
        >>> splits = [{'amount': 200}, {'amount': -150}, {'amount': 50}]
        >>> verify_splits(splits, itemgetter('amount'))
        False
    """
    return not sum(map(keyfunc, splits))


def group_transactions(transactions, keyfunc):
    """Groups transactions by keyfunc

    Args:
        transactions (List[dict]): csv content
        keyfunc (func):
    Returns:
        (List[dict]): csv content organized by transaction

    Examples:
        >>> transactions = [{'amount': '1,000.00', 'Date': '06/12/10', \
'Category': 'Checking', 'account': 'account1'}, {'amount': '1,000.00', \
'Date': '06/12/10', 'Category': 'Checking', 'account': 'account2'}]
        >>> group_transactions(transactions, itemgetter('account')).next()
        (u'account1', [{u'Date': u'06/12/10', u'Category': u'Checking', \
u'amount': u'1,000.00', u'account': u'account1'}])
    """
    sorted_transactions = sorted(transactions, key=keyfunc)

    for account, group in it.groupby(sorted_transactions, keyfunc):
        yield (account, list(group))


def gen_data(groups):
    for group, main_pos, sorted_trxns in groups:
        for pos, trxn in sorted_trxns:
            base_data = {
                'trxn': trxn,
                'is_main': pos == main_pos,
                'len': len(sorted_trxns),
                'group': group
            }

            yield base_data
