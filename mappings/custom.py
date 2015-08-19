from operator import itemgetter

mapping = {
    'has_header': True,
    'is_split': False,
    'bank': 'Bank Name',
    'currency': 'USD',
    'delimiter': ',',
    'account': itemgetter('Field'),
    'account_id': itemgetter('Field'),
    'date': itemgetter('Field'),
    'tran_type': itemgetter('Field'),
    'amount': itemgetter('Field'),
    'balance': itemgetter('Field'),
    'desc': itemgetter('Field'),
    'payee': itemgetter('Field'),
    'notes': itemgetter('Field'),
    'split_account': itemgetter('Field'),
    'class': itemgetter('Field'),
    'id': itemgetter('Field'),
    'check_num': itemgetter('Field'),
}
