# coding: utf-8

from __future__ import absolute_import

from operator import itemgetter

mapping = {
    'has_header': True,
    'currency': 'EUR',
    'delimiter': ';',
    'bank': 'GLS Bank',
    'account': itemgetter('Kontonummer'),

    # Chop up the dotted German date format and put it in ridiculous M/D/Y order
    'date': lambda r:
        r['Buchungstag'][3:5] + '/' + r['Buchungstag'][:2] + '/' +
        r['Buchungstag'][-4:],

    # locale.atof does not actually know how to deal with German separators.
    # So we do it the crude way
    'amount': lambda r: r['Betrag'].replace('.', '').replace(',', '.'),
    'desc': itemgetter('Buchungstext'),
    # Unicode marker required for python2.7
    'payee': itemgetter(u'Auftraggeber/Empfänger'),
}
