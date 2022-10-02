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

from builtins import *
from meza.fntools import get_separators
from meza.convert import to_decimal
from collections import OrderedDict

# NOTE: Because we are testing for substrings, the order we iterate
# over this dictionary matters (so place strings like "reinvest"
# above substrings like "invest")
ACTION_TYPES = OrderedDict(
    [
        ("ShrsIn", ("deposit",)),
        ("ShrsOut", ("withdraw",)),
        ("ReinvDiv", ("reinvest",)),
        (
            "Buy",
            (
                "buy",
                "invest",
            ),
        ),
        ("Div", ("dividend",)),
        ("Int", ("interest",)),
        ("Sell", ("sell",)),
        ("StkSplit", ("split",)),
    ]
)

TRANSFERABLE = {"Buy", "Div", "Int", "Sell"}


def get_account_type(account, account_types, def_type="n/a"):
    """Detect the account type of a given account

    Args:
        account (str): The account name
        account_types (dict): The account types with matching account names.
        def_type (str): The default account type.

    Returns:
        (str): The resulting account type.

    Examples:
        >>> get_account_type('somecash', {'Cash': ('cash',)}) == 'Cash'
        True
        >>> get_account_type('account', {'Cash': ('cash',)}) == 'n/a'
        True
    """
    _type = def_type

    for key, values in account_types.items():
        if any(v in account.lower() for v in values):
            _type = key
            break

    return _type


def get_action(category, transfer=False, def_action="ShrsIn"):
    """Detect the investment action of a given category

    Args:
        category (str): The transaction category.
        transfer (bool): Is the transaction an account transfer? (default:
            False)
        def_type (str): The default action.

    Returns:
        (str): The resulting action.

    Examples:
        >>> get_action('dividend & cap gains') == 'Div'
        True
        >>> get_action('buy', True) == 'BuyX'
        True
        >>> get_action('invest') == 'Buy'
        True
        >>> get_action('reinvest') == 'ReinvDiv'
        True
    """
    _type = def_action

    for key, values in ACTION_TYPES.items():
        if any(v in category.lower() for v in values):
            _type = key
            break

    if transfer and _type in TRANSFERABLE:
        return "%sX" % _type
    else:
        return _type


def convert_amount(content):
    """Convert number to a decimal amount

    Examples:
        >>> convert_amount('$1,000')
        Decimal('1000.00')
        >>> convert_amount('$1,000.00')
        Decimal('1000.00')
        >>> convert_amount('$1000,00')
        Decimal('1000.00')
        >>> convert_amount('$1.000,00')
        Decimal('1000.00')
    """
    return to_decimal(content, **get_separators(content))


def get_max_split(splits, keyfunc):
    """Returns the split in a transaction with the largest absolute value

    Args:
        splits (List[dict]): return value of group_transactions()
        keyfunc (func): key function

    Returns:
        (Tuple[str]): splits collapsed content

    Examples:
        >>> from operator import itemgetter
        >>> splits = [{'amount': 350}, {'amount': -450}, {'amount': 100}]
        >>> get_max_split(splits, itemgetter('amount')) == (1, {'amount': -450})
        True
        >>> splits = [{'amount': 350}, {'amount': -350}]
        >>> get_max_split(splits, itemgetter('amount')) == (0, {'amount': 350})
        True
    """
    maxfunc = lambda enum: abs(keyfunc(enum[1]))
    return max(enumerate(splits), key=maxfunc)


def verify_splits(splits, keyfunc):
    """Verifies that the splits of each transaction sum to 0

    Args:
       splits (dict): return value of group_transactions()
       keyfunc (func): function that returns the transaction amount

    Returns:
        (bool): true on success

    Examples:
        >>> from operator import itemgetter
        >>> splits = [{'amount': 100}, {'amount': -150}, {'amount': 50}]
        >>> verify_splits(splits, itemgetter('amount'))
        True
        >>> splits = [{'amount': 200}, {'amount': -150}, {'amount': 50}]
        >>> verify_splits(splits, itemgetter('amount'))
        False
    """
    return not sum(map(keyfunc, splits))


def gen_data(groups):
    """Generate the transaction data"""
    for group, main_pos, sorted_trxns in groups:
        for pos, trxn in sorted_trxns:
            base_data = {
                "trxn": trxn,
                "is_main": pos == main_pos,
                "len": len(sorted_trxns),
                "group": group,
            }

            yield base_data
