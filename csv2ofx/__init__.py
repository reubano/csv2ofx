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

import hashlib
import itertools as it

from functools import partial
from datetime import datetime as dt
from operator import itemgetter
from decimal import Decimal

from builtins import *
from six.moves import filterfalse
from meza.process import merge, group
from dateutil.parser import parse

from . import utils

__title__ = "csv2ofx"
__package_name__ = "csv2ofx"
__author__ = "Reuben Cummings"
__description__ = "converts a csv file of transactions to an ofx or qif file"
__email__ = "reubano@gmail.com"
__version__ = "0.30.0"
__license__ = "MIT"
__copyright__ = "Copyright 2015 Reuben Cummings"


# pylint: disable=invalid-name
md5 = lambda content: hashlib.md5(content.encode("utf-8")).hexdigest()


class Content(object):  # pylint: disable=too-many-instance-attributes
    """A transaction holding object"""

    def __init__(self, mapping=None, **kwargs):
        """Base content constructor
        Args:
            mapping (dict): bank mapper (see csv2ofx.mappings)
            kwargs (dict): Keyword arguments

        Kwargs:
            start (date): Date from which to begin including transactions.
            end (date): Date from which to exclude transactions.
            date_fmt (str): Transaction date format (defaults to '%m/%d/%y').
            dayfirst (bool): Interpret the first value in ambiguous dates (e.g. 01/05/09)
                as the day (ignored if `parse_fmt` is present).
            filter (func): Keep transactions for which function returns true

        Examples:
            >>> from csv2ofx.mappings.mint import mapping
            >>> Content(mapping)  #doctest: +ELLIPSIS
            <csv2ofx.Content object at 0x...>
        """
        mapping = mapping or {}

        # pylint doesn't like dynamically set attributes...
        self.amount = 0
        self.account = "N/A"
        self.parse_fmt = kwargs.get("parse_fmt")
        self.dayfirst = kwargs.get("dayfirst")
        self.filter = kwargs.get("filter")
        self.split_account = None
        self.inv_split_account = None
        self.id = None

        [self.__setattr__(k, v) for k, v in mapping.items()]

        if not hasattr(self, "is_split"):
            self.is_split = False

        if not hasattr(self, "has_header"):
            self.has_header = True

        if not callable(self.account):
            account = self.account
            self.account = lambda _: account

        self.start = kwargs.get("start") or dt(1970, 1, 1)
        self.end = kwargs.get("end") or dt.now()

    def parse_date(self, trxn):
        if self.parse_fmt:
            parsed = dt.strptime(self.get("date", trxn), self.parse_fmt)
        else:
            parsed = parse(self.get("date", trxn), dayfirst=self.dayfirst)

        return parsed

    def get(self, name, trxn=None, default=None):
        """Gets an attribute which could be either a normal attribute,
        a mapping function, or a mapping attribute

        Args:
            name (str): The attribute.
            trxn (dict): The transaction. Require if `name` is a mapping
                function (default: None).

            default (str): Value to use if `name` isn't found (default: None).

        Returns:
            (mixed): Either the value of the attribute function applied to the
                transaction, or the value of the attribute.

        Examples:
            >>> import datetime
            >>> from datetime import datetime as dt
            >>> from csv2ofx.mappings.mint import mapping
            >>>
            >>> trxn = {'Transaction Type': 'DEBIT', 'Amount': 1000.00}
            >>> start = dt(2015, 1, 1)
            >>> Content(mapping, start=start).get('start')  # normal attribute
            datetime.datetime(2015, 1, 1, 0, 0)
            >>> Content(mapping).get('amount', trxn)  # mapping function
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
            value = value or attr(trxn) if attr else default
        except TypeError:
            value = attr
        except KeyError:
            value = default

        return value

    def skip_transaction(self, trxn):
        """Determines whether a transaction should be skipped (isn't in the
        specified date range, etc.)

        Args:
            trxn (dict): The transaction.

        Returns:
            (bool): Whether or not to skip the transaction.

        Examples:
            >>> from csv2ofx.mappings.mint import mapping
            >>> from datetime import datetime as dt
            >>>
            >>> trxn = {'Date': '06/12/10', 'Amount': 1000.00}
            >>> Content(mapping, start=dt(2010, 1, 1)).skip_transaction(trxn)
            False
            >>> Content(mapping, start=dt(2013, 1, 1)).skip_transaction(trxn)
            True
        """
        keep = self.end >= self.parse_date(trxn) >= self.start
        return not (self.filter(trxn) if keep and self.filter else keep)

    def convert_amount(self, trxn):
        """Converts a string amount into a number

        Args:
            trxn (dict): The transaction.

        Returns:
            (decimal): The converted amount.

        Examples:
            >>> from decimal import Decimal
            >>> from datetime import datetime as dt
            >>> from csv2ofx.mappings.mint import mapping
            >>>
            >>> trxn = {'Date': '06/12/10', 'Amount': '$1,000'}
            >>> Content(mapping, start=dt(2010, 1, 1)).convert_amount(trxn)
            Decimal('1000.00')
            >>> trxn = {'Date': '06/12/10', 'Amount': '1.000,00€'}
            >>> Content(mapping, start=dt(2010, 1, 1)).convert_amount(trxn)
            Decimal('1000.00')
        """
        return utils.convert_amount(self.get("amount", trxn))

    def transaction_data(self, trxn):  # pylint: disable=too-many-locals
        """gets transaction data

        Args:
            trxn (dict): the transaction

        Returns:
            (dict): the QIF content

        Examples:
            >>> import datetime
            >>> from decimal import Decimal
            >>> from csv2ofx.mappings.mint import mapping
            >>> trxn = {
            ...     'Transaction Type': 'DEBIT', 'Amount': 1000.00,
            ...     'Date': '06/12/10', 'Description': 'payee',
            ...     'Original Description': 'description', 'Notes': 'notes',
            ...     'Category': 'Checking', 'Account Name': 'account'}
            >>> Content(mapping).transaction_data(trxn) == {
            ...     'account_id': 'e268443e43d93dab7ebef303bbe9642f',
            ...     'bank_id': 'e268443e43d93dab7ebef303bbe9642f',
            ...     'account': 'account',
            ...     'split_account_id': '195917574edc9b6bbeb5be9785b6a479',
            ...     'shares': Decimal('0'), 'payee': 'payee', 'currency': 'USD',
            ...     'bank': 'account', 'class': None, 'is_investment': False,
            ...     'date': datetime.datetime(2010, 6, 12, 0, 0),
            ...     'price': Decimal('0'), 'symbol': '', 'action': '',
            ...     'check_num': None, 'id': 'ee86450a47899254e2faa82dca3c2cf2',
            ...     'split_account': 'Checking', 'type': 'DEBIT',
            ...     'category': '', 'amount': Decimal('-1000.00'),
            ...     'memo': 'description notes', 'inv_split_account': None,
            ...     'x_action': ''}
            True
        """
        account = self.get("account", trxn)
        split_account = self.get("split_account", trxn)
        bank = self.get("bank", trxn, account)
        raw_amount = str(self.get("amount", trxn))
        amount = self.convert_amount(trxn)
        _type = self.get("type", trxn, "").upper()

        if _type not in {"DEBIT", "CREDIT"}:
            _type = "CREDIT" if amount > 0 else "DEBIT"

        date = self.get("date", trxn)
        payee = self.get("payee", trxn)
        desc = self.get("desc", trxn)
        notes = self.get("notes", trxn)
        memo = "%s %s" % (desc, notes) if desc and notes else desc or notes
        check_num = self.get("check_num", trxn)
        details = "".join(filter(None, [date, raw_amount, payee, memo]))
        category = self.get("category", trxn, "")
        shares = Decimal(self.get("shares", trxn, 0))
        symbol = self.get("symbol", trxn, "")
        price = Decimal(self.get("price", trxn, 0))
        invest = shares or (symbol and symbol != "N/A") or "invest" in category

        if invest:
            amount = abs(amount)
            shares = shares or (amount / price) if price else shares
            amount = amount or shares * price
            price = price or (amount / shares) if shares else price
            action = utils.get_action(category)
            x_action = utils.get_action(category, True)
        else:
            amount = -1 * abs(amount) if _type == "DEBIT" else abs(amount)
            action = ""
            x_action = ""

        return {
            "date": self.parse_date(trxn),
            "currency": self.get("currency", trxn, "USD"),
            "shares": shares,
            "symbol": symbol,
            "price": price,
            "action": action,
            "x_action": x_action,
            "category": category,
            "is_investment": invest,
            "bank": bank,
            "bank_id": self.get("bank_id", trxn, md5(bank)),
            "account": account,
            "account_id": self.get("account_id", trxn, md5(account)),
            "split_account": split_account,
            "inv_split_account": self.get("inv_split_account", trxn),
            "split_account_id": md5(split_account) if split_account else None,
            "amount": amount,
            "payee": payee,
            "memo": memo,
            "class": self.get("class", trxn),
            "id": self.get("id", trxn, check_num) or md5(details),
            "check_num": check_num,
            "type": _type,
        }

    def gen_trxns(self, groups, collapse=False):
        """Generate transactions"""
        for grp, transactions in groups:
            if self.is_split and collapse:
                # group transactions by `collapse` field and sum the amounts
                byaccount = group(transactions, collapse)
                oprtn = lambda values: sum(map(utils.convert_amount, values))
                merger = partial(merge, pred=self.amount, op=oprtn)
                trxns = [merger(dicts) for _, dicts in byaccount]
            else:
                trxns = transactions

            yield (grp, trxns)

    def clean_trxns(self, groups):
        """Clean transactions"""
        for grp, trxns in groups:
            _args = [trxns, self.convert_amount]

            # if it's split, transaction skipping is all or none
            if self.is_split and self.skip_transaction(trxns[0]):
                continue
            elif self.is_split and not utils.verify_splits(*_args):
                raise Exception("Splits do not sum to zero.")
            elif not self.is_split:
                filtered_trxns = filterfalse(self.skip_transaction, trxns)
            else:
                filtered_trxns = trxns

            if self.is_split:
                main_pos = utils.get_max_split(*_args)[0]
            else:
                main_pos = 0

            # pylint: disable=cell-var-from-loop
            keyfunc = lambda enum: enum[0] != main_pos
            sorted_trxns = sorted(enumerate(filtered_trxns), key=keyfunc)
            yield (grp, main_pos, sorted_trxns)
