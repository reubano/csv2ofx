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

from io import TextIOBase
from operator import itemgetter


class IterStringIO(TextIOBase):
    def __init__(self, iterable=None):
        iterable = iterable or []
        not_newline = lambda s: s not in {'\n', '\r', '\r\n'}
        self.iter = self._chain(iterable)
        self.next_line = it.takewhile(not_newline, self.iter)

    def _chain(self, iterable):
        return it.chain.from_iterable(it.ifilter(None, iterable))

    def _read(self, iterable, n):
        tmp = it.islice(iterable, None, n)
        # return bytearray(tmp)
        return ''.join(tmp)

    def write(self, iterable):
        self.iter = it.chain.from_iterable([self.iter, self._chain(iterable)])

    def read(self, n=pow(10, 10)):
        return self._read(self.iter, n)

    def readline(self, n=pow(10, 10)):
        return self._read(self.next_line, n)


def array_search_type(needle, haystack, n=1):
    """ Searches an array for the nth occurrence of a given value
     type and returns the corresponding key if successful.

        Args:
            needle (str): the type of element to find (i.e. 'numeric' or 'string')
            haystack (List[str]): the array to search

        Returns:
            (List[str]): array of the key(s) of the found element(s)

        Examples:
            >>> func('string', ('one', '2w', '3a'), 3) == (2)
            >>> func('numeric', ('1', 2, 3), 3) == (2)
            >>> func('numeric', ('one', 2, 3), 2) == (2)
    """
    switch = {'numeric': 'real', 'string': 'upper'}
    func = lambda x: hasattr(item, switch[needle])
    return islice(ifilter(func, haystack), n, None)


def array_substitute(content, needle, replace):
    """ Recursively replaces all occurrences of needle with replace on
     elements in an array

    Args:
        content (List[str]): the array to perform the replacement on
        needle (str): the value being searched for (an array may
                            be used to designate multiple needles)
        replace (str): the replacement value that replaces needle
                            (an array may be used to designate multiple
                            replacements)


    Returns:
        newContent (List[str]): new array with replaced values

    Examples:
        >>> array_substitute([('one', 'two', 'three')], 'two', 2) == ('one', 2, 'three')
    """
    for item in content:
        if hasattr(item, 'upper'):
            yield replace if item == needle else item
        else:
            try:
                yield list(array_substitute(item, needle, replace))
            except TypeError:
                yield replace if item == needle else item


def add_ordinal(num):
    """ Returns a number with ordinal suffix, e.g., 1st, 2nd, 3rd.

    Args:
        num (int): a number

    Returns:
        (str): ext a number with the ordinal suffix

    Examples:
        >>> func(11) == '11th'
        >>> func(132) == '132nd'
    """
    switch = {1: 'st', 2: 'nd', 3: 'rd'}
    end = 'th' if (num % 100 in {11, 12, 13}) else switch.get(num % 10, 'th')
    return '%i%s' % (num, end)


def filter_join(items, char=''):
    return char.join(filter(None, items))


def write_file(filepath, content, mode='wb', **kwargs):
    """Writes content to a named file.

    Args:
        filepath (str): The path of the file or file like object to write to.
        content (obj): File like object or iterable response data.
        **kwargs: Keyword arguments.

    Kwargs:
        mode (Optional[str]): The file open mode (default: 'wb').
        chunksize (Optional[int]): Number of bytes to write at a time (default:
            None, i.e., all).
        length (Optional[int]): Length of content (default: 0).
        bar_len (Optional[int]): Length of progress bar (default: 50).

    Returns:
        int: bytes written if chunksize else 0

    Examples:
        >>> import requests
        >>> filepath = get_temp_filepath(delete=True)
        >>> r = requests.get('http://google.com')
        >>> write_file(filepath, r.iter_content)
        10000000000
    """
    def _write_file(f, content, **kwargs):
        chunksize = kwargs.get('chunksize')
        length = int(kwargs.get('length') or 0)
        bar_len = kwargs.get('bar_len', 50)
        progress = 0

        # try:
        chunks = (chunk for chunk in content.read(chunksize))
        # except AttributeError:
        #     chunksize = chunksize or pow(10, 10)
        #     chunks = (chunk for chunk in content(chunksize))

        for chunk in chunks:
            f.write(chunk)
            progress += chunksize or 0

            if length:
                bars = min(int(bar_len * progress / length), bar_len)
                print('\r[%s%s]' % ('=' * bars, ' ' * (bar_len - bars)))
                sys.stdout.flush()

        return progress

    if hasattr(filepath, 'read'):
        return _write_file(filepath, content, **kwargs)
    else:
        with open(filepath, mode) as f:
            return _write_file(f, content, **kwargs)



def chunk(iterable, chunksize=0, start=0, stop=None):
    """Groups data into fixed-length chunks.
    http://stackoverflow.com/a/22919323/408556

    Args:
        iterable (iterable): Content to group into chunks.
        chunksize (Optional[int]): Number of chunks to include in a group (
            default: 0, i.e., all).

        start (Optional[int]): Starting item (zero indexed, default: 0).
        stop (Optional[int]): Ending item (zero indexed).

    Returns:
        Iter[List]: Chunked content.

    Examples:
        >>> chunk([1, 2, 3, 4, 5, 6], 2, 1).next()
        [2, 3]
    """
    i = it.islice(iter(iterable), start, stop)

    if chunksize:
        generator = (list(it.islice(i, chunksize)) for _ in it.count())
        chunked = it.takewhile(bool, generator)
    else:
        chunked = [list(i)]

    return chunked


def get_account_type(account, account_types, def_type='n/a'):
    """ Detects account types of given account names

    Args:
        accounts (List[str]):  account names
        account_types (dict):  account types and matching account names
        def_type (str):  default account type

    Returns:
        (List[str]): the resulting account types

    Examples:
        >>> (('somecash', 'checking account', 'other'), {'Bank': ('checking', 'savings'), 'Cash': ('cash',)}) == ('Cash', 'Bank', 'n/a')
    """
    _type = def_type

    for key, values in account_types.items():
        if any(v in account for v in values):
            _type = key
            break

    return _type


def merge_dicts(keyfunc, op, dicts):
    """Merges a list of dicts by a specified binary operator on the specified
       key.

    # http://codereview.stackexchange.com/a/85822/71049
    Args:
        splits (dict): return value of group_transactions()

    Yields:
        (List[str]): collapsed content

    Examples:
        >>> splits = {1: [{'account': 'Accounts Receivable', 'amount': 200}, {'account': 'Accounts Receivable', 'amount': 300}, {'account': 'Sales', 'amount': -500}], 2: [{'account': 'Accounts Receivable', 'amount': 300}, {'account': 'Accounts Receivable', 'amount': 300}, {'account': 'Sales', 'amount': -600}]}
        >>> collapse_splits(splits, itemgetter('account'), itemgetter('amount'))
        (({'account': 'Accounts Receivable', 'amount': 500}, {'account': 'Sales', 'amount': 400}), ({'account': 'Accounts Receivable', 'amount': 500}, {'account': 'Sales', 'amount': 400}))
    """
    def reducer(x, y):
        get_value = lambda k, v: op(x[k], y[k]) if keyfunc(x) == v else x[k]
        return {k: get_value(k, v) for k, v in x.items()}

    return reduce(reducer, dicts)


def get_max_split(splits, keyfunc):
    """ Returns the split in a transaction with the largest absolute value

    Args:
        splits (dict): return value of group_transactions()
        collapse (bool): collapse accounts

    Returns:
        (List[str]): splits collapsed content

    Examples:
        >>> ((({'amount': 350}, {'amount': -400}), ({'amount': 100}, {'amount': -400}, {'amount': 300}))) == (400, 400)
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
        >>> splits = {1: [{'amount': 100}, {'amount': -100}], 2: [{'amount': -300}, {'amount': 200}, {'amount': 100}]}
        >>> verify_splits(splits, itemgetter('amount'))
    """
    return not sum(map(keyfunc, splits))


def group_transactions(transactions, keyfunc):
    """Groups transactions by account

    Args:
        transactions (List[dict]): csv content
        keyfunc (func):
    Returns:
        (List[dict]): csv content organized by transaction

    Examples:
        >>> (({'amount': '1,000.00', 'Date': '06/12/10', 'Category': 'Checking', 'account': 'account1'}, {'amount': '1,000.00', 'Date': '06/12/10', 'Category': 'Checking', 'account': 'account2'})) == (({'amount': '1,000.00', 'Date': '06/12/10', 'Category': 'Checking', 'account': 'account1'}), ({'amount': '1,000.00', 'Date': '06/12/10', 'Category': 'Checking', 'account': 'account2'}))
    """
    sorted_transactions = sorted(transactions, key=keyfunc)

    for account, group in it.groupby(sorted_transactions, keyfunc):
        yield (account, list(group))
