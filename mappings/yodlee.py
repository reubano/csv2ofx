from operator import itemgetter

mapping = {
    'has_header': True,
    'is_split': True,
    'bank': lambda tr: tr['Account Name'].split(' - ')[0],
    'notes': lambda tr: ' / '.join(filter(None, [desc1, desc2, desc3]),
    'account': lambda tr: tr['Account Name'].split(' - ')[1:],
    'date': itemgetter('Date'),
    'tran_type': itemgetter('Transaction Type'),
    'amount': itemgetter('Amount'),
    'currency': itemgetter('Currency'),
    'desc': itemgetter('Original Description'),
    'payee': itemgetter('User Description'),
    'notes': itemgetter('Memo'),
    'split_account': itemgetter('Category'),
    'class': itemgetter('Classification'),
    'id': itemgetter('Transaction Id'),
}
