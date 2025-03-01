from operator import itemgetter

mapping = {
    'has_header': True,
    'filter': lambda tr: True if tr.get('Status') == 'Posted' else False,
    'is_split': False,
    'bank': 'Charles Schwab Bank, N.A.',
    'bank_id': '121202211',
    'account_id': '12345',  # Change to your actual account number if desired
    'currency': 'USD',
    'account': 'Charles Schwab Checking',
    'date': itemgetter('Date'),
    'check_num': itemgetter('CheckNumber'),
    'payee': itemgetter('Description'),
    'desc': itemgetter('Description'),
    'type': lambda tr: 'debit' if tr.get('Withdrawal') != '' else 'credit',
    'amount': lambda tr: tr.get('Deposit') or tr.get('Withdrawal'),
    'balance': itemgetter('RunningBalance'),
}
