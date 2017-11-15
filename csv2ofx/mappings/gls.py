from operator import itemgetter

mapping = {
    'has_header': True,
    'currency': 'EUR',
    'delimiter': ';',
    'bank': 'GLS Bank',
    'account': itemgetter('Kontonummer'),
    'date': lambda r: r['Buchungstag'][3:5] + '/' + r['Buchungstag'][:2] + '/' + r['Buchungstag'][-4:], # Chop up the dotted German date format and put it in ridiculous M/D/Y order
    'amount': lambda r: r['Betrag'].replace('.', '').replace(',', '.'), # locale.atof does not actually know how to deal with German separators, so we do it this way
    'desc': itemgetter('Buchungstext'),
    'payee': itemgetter('Auftraggeber/Empfänger'),
}
