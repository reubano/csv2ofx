# coding: utf-8

from __future__ import (
    absolute_import, division, print_function, unicode_literals)

from operator import itemgetter


def date_func(trxn):
    tag = trxn['Datum']

    # Chop up the ISO date and put it in ridiculous M/D/Y order
    return '{}/{}/{}'.format(tag[1], tag[2], tag[0])

mapping = {
    'has_header': True,
    'currency': itemgetter('Munt'),
    # 'delimiter': ';',
    'bank': 'Rabobank',
    'account': itemgetter('IBAN/BBAN'),
    'id': itemgetter('Volgnr'),
    'date': date_func,
    'amount': lambda r: r['Bedrag'].replace(',', '.'),
    'desc': lambda r: ' '.join(
        r['Omschrijving-{}'.format(n)] for n in range(1, 4)),
    'payee': itemgetter('Naam tegenpartij'),
}
