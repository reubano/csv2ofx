# coding: utf-8

from __future__ import (
    absolute_import, division, print_function, unicode_literals)

from operator import itemgetter


def date_func(trxn):
    tag = trxn['Buchungstag']
    return '{}/{}/{}'.format(tag[3:5], tag[:2], tag[-4:])

mapping = {
    'has_header': True,
    'currency': 'EUR',
    'delimiter': ';',
    'bank': 'GLS Bank',
    'account': itemgetter('Kontonummer'),

    # Chop up the dotted German date format and put it in ridiculous M/D/Y order
    'date': date_func,

    # locale.atof does not actually know how to deal with German separators.
    # So we do it the crude way
    'amount': lambda r: r['Betrag'].replace('.', '').replace(',', '.'),
    'desc': itemgetter('Buchungstext'),
    'payee': itemgetter('Auftraggeber/Empfänger'),
}
