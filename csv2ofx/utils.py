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

import sys
import itertools as it

from io import TextIOBase
from operator import itemgetter
from tabutils import process


class IterStringIO(TextIOBase):
    """A lazy StringIO that lets you read/write a generator of strings.
    Add SO entry
    """

    def __init__(self, iterable=None):
        """ IterStringIO constructor
        Args:
            iterable (dict): bank mapper (see csv2ofx.mappings)

        Examples:
            >>> from StringIO import StringIO
            >>> iter_content = iter('Hello World')
            >>> StringIO(iter_content).getvalue()  #doctest: +ELLIPSIS
            '<iterator object at 0x...>'
            >>> iter_sio = IterStringIO(iter_content)
            >>> iter_sio.read(5)
            u'Hello'
            >>> iter_sio.write(iter('ly person'))
            >>> iter_sio.read(8)
            u' Worldly'
        """
        iterable = iterable or []
        not_newline = lambda s: s not in {'\n', '\r', '\r\n'}
        self.iter = self._chain(iterable)
        self.next_line = it.takewhile(not_newline, self.iter)

    def _chain(self, iterable):
        iterable = iterable or []
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
            needle (str): the type of element to find (i.e. 'numeric'
                or 'string')
            haystack (List[str]): the array to search

        Returns:
            (List[str]): array of the key(s) of the found element(s)

        Examples:
            >>> array_search_type('string', ('one', '2w', '3a'), 3).next()
            u'3a'
            >>> array_search_type('numeric', ('1', 2, 3), 3).next()
            Traceback (most recent call last):
            StopIteration
            >>> array_search_type('numeric', ('one', 2, 3), 2).next()
            3
    """
    switch = {'numeric': 'real', 'string': 'upper'}
    func = lambda x: hasattr(x, switch[needle])
    return it.islice(it.ifilter(func, haystack), n - 1, None)


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
        >>> array_substitute([('one', 'two', 'three')], 'two', 2).next()
        [u'one', 2, u'three']
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
        >>> add_ordinal(11)
        u'11th'
        >>> add_ordinal(132)
        u'132nd'
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
        >>> from StringIO import StringIO
        >>> from tempfile import NamedTemporaryFile
        >>> tmpfile = NamedTemporaryFile(delete='True')
        >>> write_file(tmpfile.name, StringIO('Hello World'))
        11
        >>> tmpfile = NamedTemporaryFile(delete='True')
        >>> write_file(tmpfile.name, IterStringIO(iter('Hello World')))
        11
    """
    def _write_file(f, content, **kwargs):
        chunksize = kwargs.get('chunksize')
        length = int(kwargs.get('length') or 0)
        bar_len = kwargs.get('bar_len', 50)
        progress = 0

        if chunksize:
            try:
                chunks = (chunk for chunk in content.read(chunksize))
            except AttributeError:
                chunks = (chunk for chunk in content(chunksize))
        else:
            try:
                chunks = [content.read()]
            except AttributeError:
                chunks = [content()]

            chunksize = len(chunks[0])

        for chunk in chunks:
            f.write(chunk)
            progress += chunksize

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
    """
    _type = def_type

    for key, values in account_types.items():
        if any(v in account.lower() for v in values):
            _type = key
            break

    return _type


def convert_amount(raw):
    try:
        after_comma = process.afterish(raw, exclude='.')
        after_decimal = process.afterish(raw, '.', ',')
    except AttributeError:
        # We don't have a string
        after_comma = 0
        after_decimal = 0

    if after_comma in {-1, 0, 3} and after_decimal in {-1, 0, 1, 2}:
        amount = process.decimalize(raw)
    elif after_comma in {-1, 0, 1, 2} and after_decimal in {-1, 0, 3}:
        kwargs = {'thousand_sep': '.', 'decimal_sep': ','}
        amount = process.decimalize(raw, **kwargs)
    else:
        print('after_comma', after_comma)
        print('after_decimal', after_decimal)
        raise TypeError('Invalid number format for `%s`.' % raw)

    return amount


def merge_dicts(keyfunc, op, dicts):
    """Merges a list of dicts by a specified binary operator on the specified
       key.

    # http://codereview.stackexchange.com/a/85822/71049
    Args:
        splits (dict): return value of group_transactions()

    Returns:
        (List[str]): collapsed content

    Examples:
        >>> splits = [{'account': 'Accounts Receivable', 'amount': 200}, \
{'account': 'Accounts Receivable', 'amount': 300}, {'account': 'Accounts \
Receivable', 'amount': 300}]
        >>> merge_dicts(itemgetter('amount'), sum, splits)
        {u'account': u'Accounts Receivable', u'amount': 800}
    """
    def reducer(x, y):
        get_value = lambda k, v: op([x[k], y[k]]) if keyfunc(x) == v else x[k]
        return {k: get_value(k, v) for k, v in x.items()}

    return reduce(reducer, dicts)


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
