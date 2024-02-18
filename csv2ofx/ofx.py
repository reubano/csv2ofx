#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
# pylint: disable=no-self-use

"""
csv2ofx.ofx
~~~~~~~~~~~

Provides methods for generating OFX content

Examples:
    literal blocks::

        python example_google.py

Attributes:
    ENCODING (str): Default file encoding.
"""
from datetime import datetime as dt

from builtins import *
from meza.fntools import chunk, xmlize
from meza.process import group

from . import BalanceError, Content, utils


class OFX(Content):
    """An OFX object"""

    def __init__(self, mapping=None, **kwargs):
        """OFX constructor
        Args:
            mapping (dict): bank mapper (see csv2ofx.mappings)
            kwargs (dict): Keyword arguments

        Kwargs:
            def_type (str): Default account type.
            start (date): Date from which to begin including transactions.
            end (date): Date from which to exclude transactions.

        Examples:
            >>> from csv2ofx.mappings.mint import mapping
            >>> OFX(mapping)  # doctest: +ELLIPSIS
            <csv2ofx.ofx.OFX object at 0x...>
        """
        # TODO: Add timezone info  # pylint: disable=fixme
        super(OFX, self).__init__(mapping, **kwargs)
        self.resp_type = "INTRATRNRS" if self.split_account else "STMTTRNRS"
        self.def_type = kwargs.get("def_type")
        self.prev_group = None
        self.first_trxn = None
        self.last_trxn = None
        self.latest_trxn = None
        self.latest_date_count = 0
        self.dates_ascending = 0
        self.dates_descending = 0
        self.balances_ascending = 0
        self.balances_descending = 0
        self.account_types = {
            "CHECKING": ("checking", "income", "receivable", "payable"),
            "SAVINGS": ("savings",),
            "MONEYMRKT": ("market", "cash", "expenses"),
            "CREDITLINE": ("visa", "master", "express", "discover"),
        }

    def header(self, **kwargs):
        """ Gets OFX format transaction content

        Kwargs:
            date (datetime): The datetime (default: `datetime.now()`).
            language (str:) The ISO formatted language (defaul: ENG).

        Returns:
            (str): the OFX content

        Examples:
            >>> kwargs = {'date': dt(2012, 1, 15)}
            >>> header = 'DATA:OFXSGMLENCODING:UTF-8<OFX><SIGNONMSGSRSV1>\
<SONRS><STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS><DTSERVER>\
20120115000000</DTSERVER><LANGUAGE>ENG</LANGUAGE></SONRS></SIGNONMSGSRSV1>\
<BANKMSGSRSV1><STMTTRNRS><TRNUID></TRNUID><STATUS><CODE>0</CODE><SEVERITY>INFO\
</SEVERITY></STATUS>'
            >>> result = OFX().header(**kwargs)
            >>> result = list(result)[0]
            >>> header == result.replace('\\n', '').replace('\\t', '')
            True
            >>> msmoneyargs = { 'ms_money': True }
            >>> header = 'OFXHEADER:100DATA:OFXSGMLVERSION:102SECURITY:NONE\
ENCODING:USASCIICHARSET:1252COMPRESSION:NONEOLDFILEUID:NONENEWFILEUID:NONE\
<OFX><SIGNONMSGSRSV1>\
<SONRS><STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS><DTSERVER>\
20120115000000</DTSERVER><LANGUAGE>ENG</LANGUAGE></SONRS></SIGNONMSGSRSV1>\
<BANKMSGSRSV1><STMTTRNRS><TRNUID>1</TRNUID><STATUS><CODE>0</CODE><SEVERITY>INFO\
</SEVERITY></STATUS>'
            >>> result = OFX(msmoneyargs).header(**kwargs)
            >>> result = list(result)[0]
            >>> header == result.replace('\\n', '').replace('\\t', '')
            True
        """
        kwargs.setdefault("language", "ENG")

        # yyyymmddhhmmss
        time_stamp = kwargs.get("date", dt.now()).strftime("%Y%m%d%H%M%S")

        content = ""
        if self.ms_money:
            content += "OFXHEADER:100\n"
        content += "DATA:OFXSGML\n"
        if self.ms_money:
            content += "VERSION:102\n"
            content += "SECURITY:NONE\n"
            content += "ENCODING:USASCII\n"
            content += "CHARSET:1252\n"
            content += "COMPRESSION:NONE\n"
            content += "OLDFILEUID:NONE\n"
            content += "NEWFILEUID:NONE\n"
        else:
            content += "ENCODING:UTF-8\n"
        content += "<OFX>\n"
        content += "\t<SIGNONMSGSRSV1>\n"
        content += "\t\t<SONRS>\n"
        content += "\t\t\t<STATUS>\n"
        content += "\t\t\t\t<CODE>0</CODE>\n"
        content += "\t\t\t\t<SEVERITY>INFO</SEVERITY>\n"
        content += "\t\t\t</STATUS>\n"
        content += "\t\t\t<DTSERVER>%s</DTSERVER>\n" % time_stamp
        content += "\t\t\t<LANGUAGE>%(language)s</LANGUAGE>\n" % kwargs
        content += "\t\t</SONRS>\n"
        content += "\t</SIGNONMSGSRSV1>\n"
        content += "\t<BANKMSGSRSV1>\n"
        content += "\t\t<%s>\n" % self.resp_type
        if self.ms_money:
            content += "\t\t\t<TRNUID>1</TRNUID>\n"
        else:
            content += "\t\t\t<TRNUID></TRNUID>\n"
        content += "\t\t\t<STATUS>\n"
        content += "\t\t\t\t<CODE>0</CODE>\n"
        content += "\t\t\t\t<SEVERITY>INFO</SEVERITY>\n"
        content += "\t\t\t</STATUS>\n"
        yield content

    def transaction_data(self, trxn):
        """gets OFX transaction data

        Args:
            trxn (dict): the transaction

        Returns:
            (dict): the OFX transaction data

        Examples:
            >>> import datetime
            >>> from csv2ofx.mappings.mint import mapping
            >>> from decimal import Decimal
            >>> trxn = {
            ...     'Transaction Type': 'DEBIT', 'Amount': 1000.00,
            ...     'Date': '06/12/10', 'Description': 'payee',
            ...     'Original Description': 'description', 'Notes': 'notes',
            ...     'Category': 'Checking', 'Account Name': 'account'}
            >>> OFX(mapping, def_type='CHECKING').transaction_data(trxn) == {
            ...     'account_id': 'e268443e43d93dab7ebef303bbe9642f',
            ...     'account': 'account', 'currency': 'USD',
            ...     'account_type': 'CHECKING', 'shares': Decimal('0'),
            ...     'is_investment': False, 'bank': 'account',
            ...     'split_account_type': 'CHECKING',
            ...     'split_account_id': '195917574edc9b6bbeb5be9785b6a479',
            ...     'class': None, 'amount': Decimal('-1000.00'),
            ...     'memo': 'description notes',
            ...     'id': 'ee86450a47899254e2faa82dca3c2cf2',
            ...     'split_account': 'Checking', 'action': '', 'payee': 'payee',
            ...     'date': dt(2010, 6, 12, 0, 0), 'category': '',
            ...     'bank_id': 'e268443e43d93dab7ebef303bbe9642f',
            ...     'price': Decimal('0'), 'symbol': '', 'check_num': None,
            ...     'inv_split_account': None, 'x_action': '', 'type': 'DEBIT',
            ...     'balance': None}
            True
        """
        data = super(OFX, self).transaction_data(trxn)
        args = [self.account_types, self.def_type]
        split = data["split_account"]
        sa_type = utils.get_account_type(split, *args) if split else None
        memo = data.get("memo")
        _class = data.get("class")
        memo = "%s %s" % (memo, _class) if memo and _class else memo or _class
        payee = data.get("payee")
        date = data.get("date")
        if self.ms_money:
            payee = payee[:32] if len(payee) > 32 else payee
            if date.strftime("%H%M%S") == "000000":
                # Per MS Money OFX Troubleshooting guide:
                # "Microsoft recommends that servers either send server time in
                # full datetime format or send dates with a datetime format that
                # equates to Noon GMT, such as CCYYMMDD120000. With this format,
                # Money displays the expected date for almost any time in the
                # world. In the example above, a <DTPOSTED>20000505120000 would
                # always display as 5/5/00 anywhere the world except for the
                # center of the Pacific Ocean."
                date = date.replace(hour=12)

        new_data = {
            "account_type": utils.get_account_type(data["account"], *args),
            "split_account_type": sa_type,
            "memo": memo,
            "payee": payee,
            "date": date,
        }

        data.update(new_data)
        return data

    def account_start(self, **kwargs):
        """ Gets OFX format transaction account start content

        Args:
            kwargs (dict): Output from `transaction_data`.

        Kwargs:
            currency (str): The ISO formatted currency (required).
            bank_id (str): A unique bank identifier (required).
            account_id (str): A unique account identifier (required).
            account_type (str): The account type. One of [
                'CHECKING', 'SAVINGS', 'MONEYMRKT', 'CREDITLINE'] (required).

        Returns:
            (str): the OFX content

        Examples:
            >>> kwargs = {'start': dt(2012, 1, 1), 'end': dt(2012, 2, 1)}
            >>> akwargs = {'currency': 'USD', 'bank_id': 1, 'account_id': 1, \
'account_type': 'CHECKING'}
            >>> start = '<STMTRS><CURDEF>USD</CURDEF><BANKACCTFROM><BANKID>1\
</BANKID><ACCTID>1</ACCTID><ACCTTYPE>CHECKING</ACCTTYPE></BANKACCTFROM>\
<BANKTRANLIST><DTSTART>20120101</DTSTART><DTEND>20120201</DTEND>'
            >>> result = OFX(**kwargs).account_start(**akwargs)
            >>> start == result.replace('\\n', '').replace('\\t', '')
            True
        """
        if self.ms_money:
            # Per MS Money OFX Troubleshooting guide:
            # "Microsoft recommends that servers either send server time in
            # full datetime format or send dates with a datetime format that
            # equates to Noon GMT, such as CCYYMMDD120000. With this format,
            # Money displays the expected date for almost any time in the
            # world. In the example above, a <DTPOSTED>20000505120000 would
            # always display as 5/5/00 anywhere the world except for the
            # center of the Pacific Ocean."
            kwargs.update(
                {
                    "start_date": self.start.strftime("%Y%m%d120000"),
                    "end_date": self.end.strftime("%Y%m%d120000"),
                }
            )
        else:
            kwargs.update(
                {
                    "start_date": self.start.strftime("%Y%m%d"),
                    "end_date": self.end.strftime("%Y%m%d"),
                }
            )

        content = "\t\t\t<STMTRS>\n"
        content += "\t\t\t\t<CURDEF>%(currency)s</CURDEF>\n" % kwargs
        content += "\t\t\t\t<BANKACCTFROM>\n"
        content += "\t\t\t\t\t<BANKID>%(bank_id)s</BANKID>\n" % kwargs
        content += "\t\t\t\t\t<ACCTID>%(account_id)s</ACCTID>\n" % kwargs
        content += "\t\t\t\t\t<ACCTTYPE>%(account_type)s</ACCTTYPE>\n" % kwargs
        content += "\t\t\t\t</BANKACCTFROM>\n"
        content += "\t\t\t\t<BANKTRANLIST>\n"
        content += "\t\t\t\t\t<DTSTART>%(start_date)s</DTSTART>\n" % kwargs
        content += "\t\t\t\t\t<DTEND>%(end_date)s</DTEND>\n" % kwargs
        return content

    def transaction(self, **kwargs):
        """ Gets OFX format transaction content

        Args:
            kwargs (dict): Output from `transaction_data`.

        Kwargs:
            date (datetime): the transaction date (required)
            type (str): the transaction type (required)
            amount (number): the transaction amount (required)
            id (str): the transaction id (required)
            check_num (str): the check num
            payee (str): the payee (required)
            memo (str): the transaction memo

        Returns:
            (str): the OFX content

        Examples:
            >>> kwargs = {'date': dt(2012, 1, 15), 'type': 'DEBIT', \
'amount': 100, 'id': 1, 'check_num': 1, 'payee': 'payee', 'memo': 'memo'}
            >>> trxn = '<STMTTRN><TRNTYPE>DEBIT</TRNTYPE><DTPOSTED>\
20120115000000</DTPOSTED><TRNAMT>100.00</TRNAMT><FITID>1</FITID><CHECKNUM>1\
</CHECKNUM><NAME>payee</NAME><MEMO>memo</MEMO></STMTTRN>'
            >>> result = OFX().transaction(**kwargs)
            >>> trxn == result.replace('\\n', '').replace('\\t', '')
            True
        """
        time_stamp = kwargs["date"].strftime("%Y%m%d%H%M%S")  # yyyymmddhhmmss

        content = "\t\t\t\t\t<STMTTRN>\n"
        content += "\t\t\t\t\t\t<TRNTYPE>%(type)s</TRNTYPE>\n" % kwargs
        content += "\t\t\t\t\t\t<DTPOSTED>%s</DTPOSTED>\n" % time_stamp
        content += "\t\t\t\t\t\t<TRNAMT>%(amount)0.2f</TRNAMT>\n" % kwargs
        content += "\t\t\t\t\t\t<FITID>%(id)s</FITID>\n" % kwargs

        if (self.ms_money and kwargs.get("check_num")) or \
           (not self.ms_money and kwargs.get("check_num") is not None):
            extra = "\t\t\t\t\t\t<CHECKNUM>%(check_num)s</CHECKNUM>\n"
            content += extra % kwargs

        if kwargs.get("payee") is not None:
            content += "\t\t\t\t\t\t<NAME>%(payee)s</NAME>\n" % kwargs

        if kwargs.get("memo"):
            content += "\t\t\t\t\t\t<MEMO>%(memo)s</MEMO>\n" % kwargs

        content += "\t\t\t\t\t</STMTTRN>\n"
        return content

    def account_end(self, **kwargs):
        """ Gets OFX format transaction account end content

        Kwargs:
            date (datetime): the transaction date (required)
            balance (number): the account balance

        Returns:
            (str): the OFX content

        Examples:
            >>> kwargs = {'balance': 150, 'date': dt(2012, 1, 15)}
            >>> end = '</BANKTRANLIST><LEDGERBAL><BALAMT>150.00</BALAMT>\
<DTASOF>20120115000000</DTASOF></LEDGERBAL></STMTRS>'
            >>> result = OFX().account_end(**kwargs)
            >>> end == result.replace('\\n', '').replace('\\t', '')
            True
        """
        time_stamp = kwargs["date"].strftime("%Y%m%d%H%M%S")  # yyyymmddhhmmss
        content = "\t\t\t\t</BANKTRANLIST>\n"

        # Use the following ranked rules to guess at transaction order:
        # 1. If the transaction with the latest date is the only transcation
        #    with that date, use the balance on that transaction and don't
        #    worry about transaction order.
        # 2. If dates are both ascending and descending, don't get ending
        #    balance from transactions.
        # 3. If dates are ascending, use the last transaction.
        # 4. If dates are descending, use the first transaction.
        # 5. If more balances are consistent with ascending order, use the
        #    last transaction.
        # 6. If more balances are consistent with descending order, use the
        #    first transaction.
        # 7. Don't get ending balance from transactions.
        if self.latest_date_count == 1:                                 # (1)
            endbaltrxn = self.latest_trxn
        elif self.dates_ascending and self.dates_descending:            # (2)
            reason = "transactions have both ascending and descending dates"
            endbaltrxn = None
        elif self.dates_ascending:                                      # (3)
            endbaltrxn = self.last_trxn
        elif self.dates_descending:                                     # (4)
            endbaltrxn = self.first_trxn
        elif self.balances_ascending > self.balances_descending:        # (5)
            endbaltrxn = self.last_trxn
        elif self.balances_descending > self.balances_ascending:        # (6)
            endbaltrxn = self.first_trxn
        else:                                                           # (7)
            reason = "not enough information to determine ending balance"
            endbaltrxn = None

        balamt = kwargs.get("balance")
        if balamt is None and endbaltrxn is not None:
            # No balance specified in kwargs.  Get from transaction instead.
            balamt = endbaltrxn.get('balance')
            time_stamp = endbaltrxn['date'].strftime("%Y%m%d%H%M%S")

        if balamt is not None:
            content += "\t\t\t\t<LEDGERBAL>\n"
            content += "\t\t\t\t\t<BALAMT>%0.2f</BALAMT>\n" % balamt
            content += "\t\t\t\t\t<DTASOF>%s</DTASOF>\n" % time_stamp
            content += "\t\t\t\t</LEDGERBAL>\n"
        elif self.ms_money:
            # MS Money import fails if <LEDGERBAL> is missing
            raise BalanceError("Ending balance not specified and %s" % reason)

        content += "\t\t\t</STMTRS>\n"
        return content

    def transfer(self, **kwargs):
        """ Gets OFX transfer start

        Args:
            kwargs (dict): Output from `transaction_data`.

        Kwargs:
            account_type (str): The account type. One of [
                'CHECKING', 'SAVINGS', 'MONEYMRKT', 'CREDITLINE']
            currency (str): The ISO formatted currency (required).
            id (str):
            amount (number): the transaction amount (required)
            bank_id (str): A unique bank identifier (required).
            account_id (str): A unique account identifier (required).
            account_type (str): The account type. One of [
                'CHECKING', 'SAVINGS', 'MONEYMRKT', 'CREDITLINE'] (required).

        Returns:
            (str): the start of an OFX transfer

        Examples:
            >>> kwargs = {'currency': 'USD', 'date': dt(2012, 1, 15), \
'bank_id': 1, 'account_id': 1, 'account_type': 'CHECKING', 'amount': 100, \
'id': 'jbaevf'}
            >>> trxn = '<INTRARS><CURDEF>USD</CURDEF><SRVRTID>jbaevf</SRVRTID>\
<XFERINFO><TRNAMT>100.00</TRNAMT><BANKACCTFROM><BANKID>1</BANKID><ACCTID>1\
</ACCTID><ACCTTYPE>CHECKING</ACCTTYPE></BANKACCTFROM>'
            >>> result = OFX().transfer(**kwargs)
            >>> trxn == result.replace('\\n', '').replace('\\t', '')
            True
        """
        content = "\t\t\t<INTRARS>\n"
        content += "\t\t\t\t<CURDEF>%(currency)s</CURDEF>\n" % kwargs
        content += "\t\t\t\t<SRVRTID>%(id)s</SRVRTID>\n" % kwargs
        content += "\t\t\t\t<XFERINFO>\n"
        content += "\t\t\t\t\t<TRNAMT>%(amount)0.2f</TRNAMT>\n" % kwargs
        content += "\t\t\t\t\t<BANKACCTFROM>\n"
        content += "\t\t\t\t\t\t<BANKID>%(bank_id)s</BANKID>\n" % kwargs
        content += "\t\t\t\t\t\t<ACCTID>%(account_id)s</ACCTID>\n" % kwargs
        content += "\t\t\t\t\t\t<ACCTTYPE>%(account_type)s" % kwargs
        content += "</ACCTTYPE>\n"
        content += "\t\t\t\t\t</BANKACCTFROM>\n"
        return content

    def split_content(self, **kwargs):
        """ Gets OFX split content

        Args:
            kwargs (dict): Output from `transaction_data`.

        Kwargs:
            split_account (str): Account to use as the transfer recipient.
                (useful in cases when the transaction data isn't already split)

            bank_id (str): A unique bank identifier (required).

            split_account_id (str): A unique account identifier (required if a
                `split_account` is given).

            split_account_type (str): The account type. One of [
                'CHECKING', 'SAVINGS', 'MONEYMRKT', 'CREDITLINE'] (required if
                a `split_account` is given).

            account_id (str): A unique account identifier (required if a
                `split_account` isn't given).

            account_type (str): The account type. One of [
                'CHECKING', 'SAVINGS', 'MONEYMRKT', 'CREDITLINE'] (required if
                a `split_account` isn't given).

        Returns:
            (str): the OFX split content

        Examples:
            >>> kwargs = {'bank_id': 1, 'split_account': 'Checking', \
'split_account_id': 2, 'split_account_type': 'CHECKING', 'amount': 100 , \
'id': 'jbaevf'}
            >>> split = '<BANKACCTTO><BANKID>1</BANKID><ACCTID>2</ACCTID>\
<ACCTTYPE>CHECKING</ACCTTYPE></BANKACCTTO>'
            >>> result = OFX().split_content(**kwargs)
            >>> split == result.replace('\\n', '').replace('\\t', '')
            True
            >>> kwargs = {'bank_id': 1, 'account': 'Checking', 'account_id': \
3, 'account_type': 'CHECKING', 'amount': 100 , 'id': 'jbaevf'}
            >>> split = '<BANKACCTTO><BANKID>1</BANKID><ACCTID>3</ACCTID>\
<ACCTTYPE>CHECKING</ACCTTYPE></BANKACCTTO>'
            >>> result = OFX().split_content(**kwargs)
            >>> split == result.replace('\\n', '').replace('\\t', '')
            True
        """
        content = "\t\t\t\t\t<BANKACCTTO>\n"
        content += "\t\t\t\t\t\t<BANKID>%(bank_id)s</BANKID>\n" % kwargs

        if kwargs.get("split_account"):
            content += "\t\t\t\t\t\t<ACCTID>%(split_account_id)s" % kwargs
        else:
            content += "\t\t\t\t\t\t<ACCTID>%(account_id)s" % kwargs

        content += "</ACCTID>\n"

        if kwargs.get("split_account"):
            content += "\t\t\t\t\t\t<ACCTTYPE>%(split_account_type)s" % kwargs
        else:
            content += "\t\t\t\t\t\t<ACCTTYPE>%(account_type)s" % kwargs

        content += "</ACCTTYPE>\n"
        content += "\t\t\t\t\t</BANKACCTTO>\n"
        return content

    # pylint: disable=unused-argument
    def transfer_end(self, date=None, **kwargs):
        """Gets OFX transfer end

        Args:
            date (datetime): the transfer date (required)

        Returns:
            (str): the end of an OFX transfer

        Examples:
            >>> end = '</XFERINFO><DTPOSTED>20120115000000</DTPOSTED></INTRARS>'
            >>> result = OFX().transfer_end(dt(2012, 1, 15))
            >>> end == result.replace('\\n', '').replace('\\t', '')
            True
        """
        time_stamp = date.strftime("%Y%m%d%H%M%S")  # yyyymmddhhmmss
        content = "\t\t\t\t</XFERINFO>\n"
        content += "\t\t\t\t<DTPOSTED>%s</DTPOSTED>\n" % time_stamp
        content += "\t\t\t</INTRARS>\n"
        return content

    def footer(self, **kwargs):
        """Gets OFX transfer end

        Kwargs:
            date (datetime): The datetime (default: `datetime.now()`).

        Returns:
            (str): the OFX content

        Examples:
            >>> ft = '</BANKTRANLIST></STMTRS></STMTTRNRS></BANKMSGSRSV1></OFX>'
            >>> result = OFX().footer(date=dt(2012, 1, 15))
            >>> result = list(result)[0]
            >>> ft == result.replace('\\n', '').replace('\\t', '')
            True
        """
        kwargs.setdefault("date", dt.now())

        if self.is_split:
            content = self.transfer_end(**kwargs)
        elif not self.split_account:
            content = self.account_end(**kwargs)
        else:
            content = ""

        content += "\t\t</%s>\n\t</BANKMSGSRSV1>\n</OFX>\n" % self.resp_type
        yield content

    def gen_body(self, data):  # noqa: C901
        """Generate the OFX body"""
        for datum in data:
            grp = datum["group"]

            if self.is_split and datum["len"] > 2:
                # OFX doesn't support more than 2 splits
                raise TypeError("Group %s has too many splits.\n" % grp)

            trxn_data = self.transaction_data(datum["trxn"])
            split_like = self.is_split or self.split_account
            full_split = self.is_split and self.split_account
            new_group = self.prev_group and self.prev_group != grp

            if new_group and full_split:
                yield self.transfer_end(**trxn_data)
            elif new_group and not split_like:
                yield self.account_end(**trxn_data)

            if self.split_account:
                yield self.transfer(**trxn_data)
                yield self.split_content(**trxn_data)
                yield self.transfer_end(**trxn_data)
            elif self.is_split and datum["is_main"]:
                yield self.transfer(**trxn_data)
            elif self.is_split:
                yield self.split_content(**trxn_data)
            elif datum["is_main"]:
                self.calc_balances(trxn_data)
                yield self.account_start(**trxn_data)
                yield self.transaction(**trxn_data)
            else:
                self.calc_balances(trxn_data)
                yield self.transaction(**trxn_data)

            self.prev_group = grp

    def calc_balances(self, trxn):
        """Analyzes pairs of transactions to help determine the correct ending
        balance to use in <LEDGERBAL> block.

        Args:
            trxn (dict): the transaction
        """
        if trxn.get("balance") is None:
            return

        self.update_first_trxn(trxn)
        self.update_latest_trxn(trxn)

        # See if transactions have a consistent ascending/descending order
        if self.last_trxn is not None:
            self.check_date_order(trxn)
            self.check_balance_order(trxn)

        # Now we have a new last transaction (this one)
        self.update_last_trxn(trxn)

    def update_first_trxn(self, trxn):
        """Ending balance will be here if transactions in descending order"""
        if self.first_trxn is None:
            self.first_trxn = trxn

    def update_latest_trxn(self, trxn):
        """See if we can find one transaction with the latest date

        Args:
            trxn (dict): the transaction

        Examples:
            >>> ofx = OFX()
            >>> trxn1 = { 'date': dt(2010, 6, 12, 0, 0) }
            >>> trxn2 = { 'date': dt(2010, 6, 12, 0, 0) }
            >>> trxn3 = { 'date': dt(2010, 6, 13, 0, 0) }
            >>> ofx.update_latest_trxn(trxn1)
            >>> ofx.latest_trxn['date'] == dt(2010, 6, 12, 0, 0)
            True
            >>> ofx.latest_date_count
            1
            >>> ofx.update_latest_trxn(trxn2)
            >>> ofx.latest_trxn['date'] == dt(2010, 6, 12, 0, 0)
            True
            >>> ofx.latest_date_count
            2
            >>> ofx.update_latest_trxn(trxn3)
            >>> ofx.latest_trxn['date'] == dt(2010, 6, 13, 0, 0)
            True
            >>> ofx.latest_date_count
            1
        """
        if self.latest_trxn is None:
            self.latest_trxn = trxn
            self.latest_date_count = 1
        elif trxn['date'] > self.latest_trxn['date']:
            self.latest_trxn = trxn
            self.latest_date_count = 1
        elif trxn['date'] == self.latest_trxn['date']:
            self.latest_date_count += 1

    def check_date_order(self, trxn):
        """See if dates have a consistent ascending/descending order

        Args:
            trxn (dict): the transaction

        Examples:
            >>> ofx = OFX()
            >>> trxn1 = { 'date': dt(2010, 6, 12, 0, 0) }
            >>> trxn2 = { 'date': dt(2010, 6, 12, 0, 0) }
            >>> trxn3 = { 'date': dt(2010, 6, 13, 0, 0) }
            >>> trxn4 = { 'date': dt(2010, 6, 11, 0, 0) }
            >>> ofx.update_last_trxn(trxn1)
            >>> ofx.check_date_order(trxn2)
            >>> ofx.dates_ascending
            0
            >>> ofx.dates_descending
            0
            >>> ofx.update_last_trxn(trxn2)
            >>> ofx.check_date_order(trxn3)
            >>> ofx.dates_ascending
            1
            >>> ofx.dates_descending
            0
            >>> ofx.update_last_trxn(trxn3)
            >>> ofx.check_date_order(trxn4)
            >>> ofx.dates_ascending
            1
            >>> ofx.dates_descending
            1
        """
        if trxn['date'] > self.last_trxn['date']:
            # Dates are consistent with ascending transaction order
            self.dates_ascending += 1
        elif trxn['date'] < self.last_trxn['date']:
            # Dates are consistent with descending transaction order
            self.dates_descending += 1

    def check_balance_order(self, trxn):
        """See if balances are consistent with ascending/descending order

        Args:
            trxn (dict): the transaction

        Examples:
            >>> ofx = OFX()
            >>> trxn1 = { 'amount': 10, 'balance': 100 }
            >>> trxn2 = { 'amount': 10, 'balance': 100 }
            >>> trxn3 = { 'amount': 10, 'balance': 110 }
            >>> trxn4 = { 'amount': 10, 'balance': 100 }
            >>> trxn5 = { 'amount': -10, 'balance': 90 }
            >>> ofx.update_last_trxn(trxn1)
            >>> ofx.check_balance_order(trxn2)
            >>> ofx.balances_ascending
            0
            >>> ofx.balances_descending
            0
            >>> ofx.update_last_trxn(trxn2)
            >>> ofx.check_balance_order(trxn3)
            >>> ofx.balances_ascending
            1
            >>> ofx.balances_descending
            0
            >>> ofx.update_last_trxn(trxn3)
            >>> ofx.check_balance_order(trxn4)
            >>> ofx.balances_ascending
            1
            >>> ofx.balances_descending
            1
            >>> ofx.update_last_trxn(trxn4)
            >>> ofx.check_balance_order(trxn5)
            >>> ofx.balances_ascending
            2
            >>> ofx.balances_descending
            2
        """
        # Note: Both of these could be true for a given transaction pair
        if self.last_trxn["balance"] + trxn['amount'] == \
                trxn['balance']:
            # Balances appear consistent with ascending transaction order
            self.balances_ascending += 1
        if trxn.get("balance") + self.last_trxn['amount'] == \
                self.last_trxn['balance']:
            # Balances appear consistent with descending transaction order
            self.balances_descending += 1

    def update_last_trxn(self, trxn):
        """Ending balance will be here if transactions are in ascending order"""
        self.last_trxn = trxn

    def gen_groups(self, records, chunksize=None):
        """Generate the OFX groups"""
        for chnk in chunk(records, chunksize):
            cleansed = [{k: next(xmlize([v])) for k, v in c.items()} for c in chnk]
            keyfunc = self.id if self.is_split else self.account

            for gee in group(cleansed, keyfunc):
                yield gee
