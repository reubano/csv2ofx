from operator import itemgetter

mapping = {
    'is_split': False,
    'has_header': True,
    'account': itemgetter('Account Name'),
    'date': itemgetter('Date'),
    'tran_type': itemgetter('Transaction Type'),
    'amount': itemgetter('Amount'),
    'desc': itemgetter('Original Description'),
    'payee': itemgetter('Description'),
    'notes': itemgetter('Notes'),
    'split_account': itemgetter('Category'),
}
