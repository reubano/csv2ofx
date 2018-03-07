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
    'type': itemgetter('Buchungstext'),
    'desc': lambda r: ' '.join([r['VWZ1'], r['VWZ2'], r['VWZ3'], r['VWZ4'], r['VWZ5'], r['VWZ6'], r['VWZ7'], r['VWZ8'], r['VWZ9'], r['VWZ10'], r['VWZ11'], r['VWZ12'], r['VWZ13'], r['VWZ14']]),
    # Unicode marker required for python2.7
    'payee': itemgetter(u'Auftraggeber/Empfänger'),
}
