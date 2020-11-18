from __future__ import (
    absolute_import, division, print_function, unicode_literals)

from operator import itemgetter
import json
import hashlib


def date_func(trxn):
    tag = trxn['Buchungstag']
    # Chop up the ISO date and put it in ridiculous M/D/Y order
    return '{}/{}/{}'.format(tag[3:5], tag[:2], "20" + tag[-2:])

mapping = {
    'has_header': True,
    'is_split': False,
    'bank': 'Sparkasse',
    'currency': 'EUR',
    'delimiter': ';',
    'account': itemgetter('Auftragskonto'),
    # 'type': 'debit',
    'date': date_func,
    'amount': lambda r: r['Betrag'].replace('.', '').replace(',', '.'),
    'desc': itemgetter('Buchungstext'),
    'notes': itemgetter('Verwendungszweck'),
    'payee': itemgetter('Beguenstigter/Zahlungspflichtiger'),
    # 'desc': itemgetter('Payment reference'),
    # 'class': itemgetter('Category'),
    # 'id': gen_transaction_id,
    # 'check_num': itemgetter('Field'),
}
