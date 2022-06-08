#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
# pylint: disable=no-self-use

"""
csv2ofx.qif
~~~~~~~~~~~

Provides methods for generating qif content

Examples:
    literal blocks::

        python example_google.py

Attributes:
    ENCODING (str): Default file encoding.
"""
from builtins import *
from meza.fntools import chunk
from meza.process import group

from . import Content, utils

DEF_DATE_FMT = "%m/%d/%Y"


class QIF(Content):
    """A QIF object"""

    def __init__(self, mapping=None, date_fmt=DEF_DATE_FMT, **kwargs):
        """QIF constructor
        Args:
            mapping (dict): bank mapper (see csv2ofx.mappings)
            kwargs (dict): Keyword arguments

        Kwargs:
            def_type (str): Default account type.
            start (date): Date from which to begin including transactions.
            end (date): Date from which to exclude transactions.
            date_fmt (str): Transaction date output format (defaults to '%m/%d/%y').

        Examples:
            >>> from csv2ofx.mappings.mint import mapping
            >>> QIF(mapping)  #doctest: +ELLIPSIS
            <csv2ofx.qif.QIF object at 0x...>
        """
        self.date_fmt = date_fmt

        super(QIF, self).__init__(mapping, date_fmt=date_fmt, **kwargs)
        self.def_type = kwargs.get("def_type")
        self.prev_account = None
        self.prev_group = None
        self.account_types = {
            "Invst": ("roth", "ira", "401k", "vanguard"),
            "Bank": ("checking", "savings", "market", "income"),
            "Oth A": ("receivable",),
            "Oth L": ("payable",),
            "CCard": ("visa", "master", "express", "discover", "platinum"),
            "Cash": ("cash", "expenses"),
        }

    def header(self, **kwargs):  # pylint: disable=unused-argument
        """Get the QIF header"""
        return None

    def transaction_data(self, tr):
        """gets QIF transaction data

        Args:
            tr (dict): the transaction

        Returns:
            (dict): the QIF transaction data

        Examples:
            >>> from datetime import datetime as dt
            >>> from decimal import Decimal
            >>> from csv2ofx.mappings.mint import mapping
            >>> tr = {
            ...     'Transaction Type': 'DEBIT', 'Amount': 1000.00,
            ...     'Date': '06/12/10', 'Description': 'payee',
            ...     'Original Description': 'description', 'Notes': 'notes',
            ...     'Category': 'Checking', 'Account Name': 'account'}
            >>> QIF(mapping, def_type='Bank').transaction_data(tr) == {
            ...     'account_id': 'e268443e43d93dab7ebef303bbe9642f',
            ...     'account': 'account', 'currency': 'USD',
            ...     'account_type': 'Bank', 'shares': Decimal('0'),
            ...     'is_investment': False, 'bank': 'account',
            ...     'split_memo': 'description notes', 'split_account_id': None,
            ...     'class': None, 'amount': Decimal('-1000.00'),
            ...     'memo': 'description notes',
            ...     'id': 'ee86450a47899254e2faa82dca3c2cf2',
            ...     'split_account': 'Checking',
            ...     'split_account_id': '195917574edc9b6bbeb5be9785b6a479',
            ...     'action': '', 'payee': 'payee',
            ...     'date': dt(2010, 6, 12, 0, 0), 'category': '',
            ...     'bank_id': 'e268443e43d93dab7ebef303bbe9642f',
            ...     'price': Decimal('0'), 'symbol': '', 'check_num': None,
            ...     'inv_split_account': None, 'x_action': '', 'type': 'DEBIT'}
            True
        """
        data = super(QIF, self).transaction_data(tr)
        args = [self.account_types, self.def_type]
        memo = data.get("memo")
        _class = data.get("class")

        if memo and _class:
            split_memo = "%s %s" % (memo, _class)
        else:
            split_memo = memo or _class

        new_data = {
            "account_type": utils.get_account_type(data["account"], *args),
            "split_memo": split_memo,
        }

        data.update(new_data)
        return data

    def account_start(self, **kwargs):
        """Gets QIF format account content

        Args:
            kwargs (dict): Output from `transaction_data`.

        Kwargs:
            account (str): The account name.
            account_type (str): The account type. One of ['Bank', 'Oth A',
                'Oth L', 'CCard', 'Cash', 'Invst'] (required).

        Returns:
             (str): the QIF content

        Examples:
            >>> kwargs = {'account': 'account', 'account_type': 'Bank'}
            >>> start = '!AccountNaccountTBank^'
            >>> result = QIF().account_start(**kwargs)
            >>> start == result.replace('\\n', '').replace('\\t', '')
            True
        """
        return "!Account\nN%(account)s\nT%(account_type)s\n^\n" % kwargs

    def transaction_start(self, account_type=None, **kwargs):
        """Gets QIF format transaction start content

        Args:
            account_type (str): the transaction account type
            kwargs (dict): Output from `transaction_data`.

        Returns:
            (str): content the QIF content

        Examples:
            >>> result = QIF().transaction_start(account_type='Bank')
            >>> '!Type:Bank' == result.replace('\\n', '').replace('\\t', '')
            True
        """
        return "!Type:%s\n" % account_type

    def transaction(self, **kwargs):
        """Gets QIF format transaction content

        Args:
            kwargs (dict): Output from `transaction_data`.

        Kwargs:
            date (date): the transaction date (required)
            amount (number): the transaction amount (required)
            payee (number): the transaction amount (required)
            date_fmt (str): the transaction date format (defaults to '%m/%d/%Y')
            memo (str): the transaction memo
            class (str): the transaction classification
            check_num (str): a unique transaction identifier

        Returns:
            (str): content the QIF content

        Examples:
            >>> from datetime import datetime as dt
            >>> kwargs = {
            ...     'payee': 'payee', 'amount': 100, 'check_num': 1,
            ...     'date': dt(2012, 1, 1)}
            >>> trxn = 'N1D01/01/2012PpayeeT100.00'
            >>> result = QIF().transaction(**kwargs)
            >>> trxn == result.replace('\\n', '').replace('\\t', '')
            True
        """
        date_fmt = kwargs.get("date_fmt", self.date_fmt)
        kwargs.update({"time_stamp": kwargs["date"].strftime("%m/%d/%Y")})
        is_investment = kwargs.get("is_investment")
        is_transaction = not is_investment

        if self.is_split:
            kwargs.update({"amount": kwargs["amount"] * -1})

        if is_transaction and kwargs.get("check_num"):
            content = "N%(check_num)s\n" % kwargs
        else:
            content = ""

        content += "D%(time_stamp)s\n" % kwargs

        if is_investment:
            if kwargs.get("inv_split_account"):
                content += "N%(x_action)s\n" % kwargs
            else:
                content += "N%(action)s\n" % kwargs

            content += "Y%(symbol)s\n" % kwargs
            content += "I%(price)s\n" % kwargs
            content += "Q%(shares)s\n" % kwargs
            content += "Cc\n"
        else:
            content += "P%(payee)s\n" % kwargs if kwargs.get("payee") else ""
            content += "L%(class)s\n" % kwargs if kwargs.get("class") else ""

        content += "M%(memo)s\n" % kwargs if kwargs.get("memo") else ""

        if is_investment and kwargs.get("commission"):
            content += "O%(commission)s\n" % kwargs

        content += "T%(amount)0.2f\n" % kwargs
        return content

    def split_content(self, **kwargs):
        """Gets QIF format split content

        Args:
            kwargs (dict): Output from `transaction_data`.

        Kwargs:
            split_account (str): Account to use as the transfer recipient.
                (useful in cases when the transaction data isn't already split)

            inv_split_account (str): Account to use as the investment transfer
                recipient. (useful in cases when the transaction data isn't
                already split)

            account (str): A unique account identifier (required if neither
                `split_account` nor `inv_split_account` is given).

            split_memo (str): the transaction split memo

        Returns:
            (str): the QIF content

        Examples:
            >>> kwargs =  {
            ...     'account': 'account', 'split_memo': 'memo', 'amount': 100}
            >>> split = 'SaccountEmemo$100.00'
            >>> result = QIF().split_content(**kwargs)
            >>> split == result.replace('\\n', '').replace('\\t', '')
            True
        """
        is_investment = kwargs.get("is_investment")
        is_transaction = not is_investment

        if is_investment and kwargs.get("inv_split_account"):
            content = "L%(inv_split_account)s\n" % kwargs
        elif is_investment and self.is_split:
            content = "L%(account)s\n" % kwargs
        elif is_transaction and kwargs.get("split_account"):
            content = "S%(split_account)s\n" % kwargs
        elif is_transaction:
            content = "S%(account)s\n" % kwargs
        else:
            content = ""

        if content and kwargs.get("split_memo"):
            content += "E%(split_memo)s\n" % kwargs

        content += "$%(amount)0.2f\n" % kwargs if content else ""
        return content

    def transaction_end(self):
        """Gets QIF transaction end

        Returns:
            (str): the QIF transaction end

        Examples:
            >>> result = QIF().transaction_end()
            >>> result.replace('\\n', '').replace('\\t', '') == '^'
            True
        """
        return "^\n"

    def footer(self, **kwargs):  # pylint: disable=unused-argument
        """Gets QIF transaction footer.

        Returns:
            (str): the QIF footer

        Examples:
            >>> QIF().footer() == ''
            True
        """
        return self.transaction_end() if self.is_split else ""

    def gen_body(self, data):
        """Generate the QIF body"""
        split_account = self.split_account or self.inv_split_account

        for datum in data:
            trxn_data = self.transaction_data(datum["trxn"])
            account = self.account(datum["trxn"])
            grp = datum["group"]

            if self.prev_group and self.prev_group != grp and self.is_split:
                yield self.transaction_end()

            if datum["is_main"] and self.prev_account != account:
                yield self.account_start(**trxn_data)
                yield self.transaction_start(**trxn_data)

            if (self.is_split and datum["is_main"]) or not self.is_split:
                yield self.transaction(**trxn_data)
                self.prev_account = account

            if (self.is_split and not datum["is_main"]) or split_account:
                yield self.split_content(**trxn_data)

            if not self.is_split:
                yield self.transaction_end()

            self.prev_group = grp

    def gen_groups(self, records, chunksize=None):
        """Generate the QIF groups"""
        for chnk in chunk(records, chunksize):
            keyfunc = self.id if self.is_split else self.account

            for gee in group(chnk, keyfunc):
                yield gee
