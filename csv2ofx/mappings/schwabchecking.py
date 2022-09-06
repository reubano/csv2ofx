from __future__ import (
    absolute_import, division, print_function, unicode_literals)

from operator import itemgetter

# Schwab Bank includes three lines of text in their CSV which otherwise break
# date parsing.  Filtering by lines with no "Type" (and faking out the date for
# those lines) avoids the problem.

# Note: Ideally, we could get account_id from the first line of the CSV.

mapping = {
    'first_row': 1,
    'has_header': True,
    'filter': lambda tr: tr.get('Type'),
    'is_split': False,
    'bank': 'Charles Schwab Bank, N.A.',
    'bank_id': '121202211',
    'account_id': '12345',  # Change to your actual account number if desired
    'currency': 'USD',
    'account': 'Charles Schwab Checking',
    'date': lambda tr: tr.get('Date') if tr.get('Type') else "1-1-1970",
    'check_num': itemgetter('Check #'),
    'payee': itemgetter('Description'),
    'desc': itemgetter('Description'),
    'type': lambda tr: 'debit' if tr.get('Withdrawal (-)') != '' else 'credit',
    'amount': lambda tr: tr.get('Deposit (+)') or tr.get('Withdrawal (-)'),
    'balance': itemgetter('RunningBalance'),
}
