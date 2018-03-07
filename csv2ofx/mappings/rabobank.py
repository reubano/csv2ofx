# coding: utf-8

from __future__ import absolute_import

from operator import itemgetter

mapping = {
    'has_header': True,
    'currency': itemgetter('Munt'),
    # 'delimiter': ';',
    'bank': 'Rabobank',
    'account': itemgetter('IBAN/BBAN'),
    'id': itemgetter('Volgnr'),

    # Chop up the ISO date and put it in ridiculous M/D/Y order
    'date': lambda r:
        r['Datum'].split('-')[1] + '/' + r['Datum'].split('-')[2] + '/' +
        r['Datum'].split('-')[0],
        
    'amount': lambda r: r['Bedrag'].replace(',', '.'),
    'desc': lambda r: ' '.join([r['Omschrijving-1'], r['Omschrijving-2'], r['Omschrijving-3']]),
    'payee': itemgetter('Naam tegenpartij'),
}
