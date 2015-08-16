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

CURRENCIES = ('$', '£', '€')

class IterStringIO(TextIOBase):
    def __init__(self, iterable=None):
        iterable = iterable or []
        self.iter = it.chain.from_iterable(iterable)

    def _read(self, iterable, n):
        return bytearray(it.islice(iterable, None, n))

    @property
    def next_line(self):
        return it.takewhile(lambda s: s not in {'\n', '\r', '\r\n'}, self.iter)

    def write(self, iterable):
        to_chain = it.chain.from_iterable(iterable)
        self.iter = it.chain.from_iterable([self.iter, to_chain])

    def read(self, n=None):
        return self._read(self.iter, n)

    def readline(self, n=None):
        return self._read(self.next_line, n)

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
def array_search_type(needle, haystack, n=1):
    """Helps read a csv file.

    Examples:
        >>> from os import path as p
        >>> parent_dir = p.abspath(p.dirname(p.dirname(__file__)))
        >>> filepath = p.join(parent_dir, 'data', 'test.csv')
        >>> f = open(filepath, 'rU')
        >>> names = ['some_date', 'sparse_data', 'some_value', 'unicode_test']
        >>> records = _read_csv(f, 'utf-8', names)
        >>> it.islice(records, 2, 3).next()['some_date']
        u'01-Jan-15'
        >>> f.close()
    """    switch = {'numeric': 'real', 'string': 'upper'}
    func = lambda x: hasattr(item, switch[needle])
    return islice(ifilter(func, haystack), n, None)


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

 array_substitute([('one', 'two', 'three')], 'two', 2) == ('one', 2, 'three')
"""
def array_substitute(content, needle, replace):
    for item in content:
        if hasattr(item, 'upper'):
            yield replace if item == needle else item
        else:
            try:
                yield list(array_substitute(item, needle, replace))
            except TypeError:
                yield replace if item == needle else item


def mreplace(string, replacements):
    func = lambda x, y: x.replace(y[0], y[1])
    return reduce(func, replacements, string)


""" Recursively makes elements of an array xml compliant

    Args:
        content (List[str]): the content to clean

    Returns:
        (List[str]): the cleaned content

    Examples:
        >>> func((('&'), ('<'))) == (('&amp'), ('&lt'))
"""
def xmlize(content):
    replacements = [
        ('&', '&amp'), ('>', '&gt'), ('<', '&lt'), ('\n', ' '), ('\r\n', ' ')]

    for item in content:
        if hasattr(item, 'upper'):
            yield mreplace(item, replacements)
        else:
            try:
                yield list(xmlize(item, needle, replace))
            except TypeError:
                yield mreplace(item, replacements)

""" Returns a number with ordinal suffix, e.g., 1st, 2nd, 3rd.

    Args:
        num (int): a number

    Returns:
        (str): ext a number with the ordinal suffix

    Examples:
        >>> func(11) == '11th'
        >>> func(132) == '132nd'
"""
def add_ordinal(num):
    switch = {1: 'st', 2: 'nd', 3: 'rd'}
    end = 'th' if (num % 100 in {11, 12, 13}) else switch.get(num % 10, 'th')
    return '%i%s' % (num, end)


""" Converts an array to string while adding an extra string to the beginning
 and end of each element

    Args:
        content (List[str]): array to convert
        extra (str): string to add to the beginning and end of each array
            element

        delimiter (str): character to seperate each arrayelement

    Returns:
        content (str): content formatted on 1 line with the extra string added
            to the beginning and end of each array element

    Examples:
        >>> func(('one', 'two')) == "'one' 'two'"
"""
def extraImplode(content, extra = '\'', delimiter = ' '):
    if (!is_array(content))
        throw new Exception(
            'Please use an array from '._className.'->'.
            __FUNCTION__.'() line '.__LINE__
        )
    else
                return extra.implode(extra.delimiter.extra, content).
                extra # array to string

def write_file(filepath, fileobj, mode='wb', **kwargs):
"""Writes content to a named file.

Args:
    filepath (str): The path of the file to write to.
    fileobj (obj): File like object or iterable response data.
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
    chunksize = kwargs.get('chunksize')
    length = int(kwargs.get('length') or 0)
    bar_len = kwargs.get('bar_len', 50)

    with open(filepath, mode) as f:
        progress = 0

        try:
            chunks = (chunk for chunk in fileobj.read(chunksize))
        except AttributeError:
            chunksize = chunksize or pow(10, 10)
            chunks = (chunk for chunk in fileobj(chunksize))

        for chunk in chunks:
            f.write(chunk)
            progress += chunksize or 0

            if length:
                bars = min(int(bar_len * progress / length), bar_len)
                print('\r[%s%s]' % ('=' * bars, ' ' * (bar_len - bars)))
                sys.stdout.flush()

    return progress


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

def getAccounts(splitContent, head_amount, findAmounts=None):
    """ Get main accounts (if passed findAmounts, it returns the account of the
     split matching the given amount)

    Args:
        splitContent (List[str]): return value of makeSplits()
        findAmounts (List[str]): split amounts to find

    Returns:
        (List[str]): main accounts

    Examples:
        >>> getAccounts(({'Account Name': 'account1'}, {'Account Name': 'account2'}), ({'Account Name': 'account3'}, {'Account Name': 'account4'})) == ('account1', 'account3')
        >>> getAccounts(({'Account Name': 'account1', 'amount': -200}, {'Account Name': 'account2', 'amount': 200}), ({'Account Name': 'account3', 'amount': 400}, {'Account Name': 'account4', 'amount': -400})), (200, 400)) == ('account1', 'account3')
    """
    func = lambda x, y: abs(x[head_amount]) == y
    findAmounts = findAmounts or []

    for splits, amount in izip_longest(splitContent, findAmounts):
        for split in splits:
            if not findAmounts or (findAmounts and func(split, amount)):
                yield split[head_account]
                break



def getAccountTypes(accounts, type_list, def_type='n/a'):
    """ Detects account types of given account names

    Args:
        accounts (List[str]):  account names
        type_list (List[str]):  account types and matching account names
        def_type (str):  default account type

    Returns:
        (List[str]): the resulting account types

    Examples:
        >>> (('somecash', 'checking account', 'other'), {'Bank': ('checking', 'savings'), 'Cash': ('cash',)}) == ('Cash', 'Bank', 'n/a')
    """
    for account in accounts:
        for key, values in type_list.items():
            if any(v in account for v in values):
                yield key
                break
        else:
            yield def_type


def getSplitAccounts(transaction, head_account):
    """ Gets split accounts

    Args:
        transaction (List[str]): array of splits

    Returns:
        (List[str]): the resulting split account names

    Examples:
        >>> (({'Account Name': 'Accounts Receivable', 'amount': 200}, {'Account Name': 'Accounts Receivable', 'amount': 300}, {'Account Name': 'Sales', 'amount': 400})) == {'Accounts Receivable', 'Sales'}
    """
    accounts = [split[head_account] for split in transaction]
    return accounts[1:]

def collapseSplits(content, head_account, head_amount):
    """ Combines splits with the same account

    Args:
        content (List[str]): return value of makeSplits()

    Returns:
        (List[str]): collapsed content

    Examples:
        >>> (({'Account Name': 'Accounts Receivable', 'amount': 200}, {'Account Name': 'Accounts Receivable', 'amount': 300}, {'Account Name': 'Sales', 'amount': 400}), ({'Account Name': 'Accounts Receivable', 'amount': 200}, {'Account Name': 'Accounts Receivable', 'amount': 300}, {'Account Name': 'Sales', 'amount': 400})) == (({'Account Name': 'Accounts Receivable', 'amount': 500}, {'Account Name': 'Sales', 'amount': 400}), ({'Account Name': 'Accounts Receivable', 'amount': 500}, {'Account Name': 'Sales', 'amount': 400}))
    """
    keyfunc = itemgetter(head_account)

    def gen_splits(sorted_splits):
        for account, group in it.groupby(sorted_splits, keyfunc):
            split = group.next()
            add_amount = sum(g[head_amount] for g in group)
            split.update({head_amount: split[head_amount] + add_amount})
            yield split

    for splits in content:
        yield list(gen_splits(sorted(splits, key=keyfunc)))


def getMaxSplitAmounts(splitContent, head_amount):
    """ Returns the split in a transaction with the largest absolute value

    Args:
        splitContent (List[str]): return value of makeSplits()
        collapse (bool): collapse accounts

    Returns:
        (List[str]): splitContent collapsed content

    Examples:
        >>> ((({'amount': 350}, {'amount': -400}), ({'amount': 100}, {'amount': -400}, {'amount': 300}))) == (400, 400)
    """
    maxAbs = lambda a, b: max(abs(a), abs(b))
    amounts = ([a[head_amount] for a in split] for split in splitContent)
    return [reduce(maxAbs, item) for item in amounts]


def verifySplits(splitContent, head_amount):
    """ Verifies that the splits of each transaction sum to 0

    Args:
       splitContent (List[str]): return value of makeSplits()

    Returns:
        (bool): true on success

    Examples:
        >>> ((({'amount': 100}, {'amount': -100}), ({'amount': -300}, {'amount': 200}, {'amount': 100}))) == true
    """
    amounts = ([a[head_amount] for a in split] for split in splitContent)
    return not any(sum(item) for item in amounts)


def makeSplits(csv_content, head_id):
    """
    Args:
        csv_content (List[str]): csv content

    Returns:
        (List[str]): csv content organized by transaction

    Examples:
        >>> (({'amount': '1,000.00', 'Date': '06/12/10', 'Category': 'Checking', 'Account Name': 'account1'}, {'amount': '1,000.00', 'Date': '06/12/10', 'Category': 'Checking', 'Account Name': 'account2'})) == (({'amount': '1,000.00', 'Date': '06/12/10', 'Category': 'Checking', 'Account Name': 'account1'}), ({'amount': '1,000.00', 'Date': '06/12/10', 'Category': 'Checking', 'Account Name': 'account2'}))
    """
    for content in csv_content:
        splitContent[content[head_id]] = content

    splitContent = {}
    [{splitContent: [content[head_id]]} for content in csv_content]
    return splitContent
    # TODO: fixme


def decimalize(string, thousand_sep=',', decimal_sep='.', precision=2):
    """
    >>> decimalize('$123.45')
    123.45
    >>> decimalize('123€')
    123.00
    >>> decimalize('2,123.45')
    2123.45
    >>> decimalize('2.123,45', '.', ',')
    2123.45
    >>> decimalize('spam')
    TypeError
    """
    currencies = it.izip(CURRENCIES, it.repeat(''))
    seperators = [(thousand_sep, ''), (decimal_sep, '.')]
    stripped = mreplace(string, it.chain(currencies, seperators))
    return float(stripped)


def is_numeric_like(string, seperators=('.', ',')):
    """
    >>> is_numeric_like('$123.45')
    True
    >>> is_numeric_like('123€')
    True
    >>> is_numeric_like('2,123.45')
    True
    >>> is_numeric_like('2.123,45')
    True
    >>> is_numeric_like('10e5')
    True
    >>> is_numeric_like('spam')
    False
    """
    replacements = it.izip(it.chain(CURRENCIES, seperators), it.repeat(''))
    stripped = mreplace(string, replacements)

    try:
        return float(stripped)
    except (ValueError, TypeError):
        return False


def afterish(string, char):
    """Number of digits after a given character.

    >>> afterish('123.45', '.')
    2
    >>> afterish('1001.', '.')
    0
    >>> afterish('1001', '.')
    -1
    >>> afterish('1,001', ',')
    3
    >>> afterish('2,100,001.00', ',')
    3
    >>> afterish('eggs', '.')
    TypeError

    """
    numeric_like = is_numeric_like(string)

    elif numeric_like and char in string:
        after = len(string) - string.rfind(char) - 1
    elif numeric_like:
        after = -1
    else:
        raise TypeError('Not able to convert %s to a number' % string)

    return after
