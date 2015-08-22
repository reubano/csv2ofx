from operator import itemgetter

mapping = {
    'has_header': True,
    'bank': lambda tr: tr['Account'].split(' - ')[0],
    'split_account': itemgetter('?'),
    'account': lambda tr: tr['Account'].split(' - ')[1:],
    'currency': itemgetter('Currency'),
    'class': itemgetter('Projects'),
    'check_num': itemgetter('Num'),
    'tran_type': lambda tr: 'debit' if tr.get('Debit') else 'credit',
    'amount': itemgetter('Amount'),
    'notes': itemgetter('Memo'),
    'date': itemgetter('Date'),
    'desc': itemgetter('Category'),
    'payee': itemgetter('Payee'),
}
