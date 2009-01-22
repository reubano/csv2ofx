
# mapping tells the next functions where to get the data for each row
# each key in a mapping must return a function that takes
# the current row and the SimpleCSVGrid object
# the function must return the OFX data for that field.

# NOTE I thought about simply having a dicionary from key fields to column numbers
# but that was not flexible enough to combine column data dynamically
# in order to get custom data from the CSV file.
# (example Memo/Description/BankID/Account id in the yodlee data)

from csvutils import *


def yodlee_dscr(row,grid):
    " use user description for payee 1st, the original description"
    od=fromCSVCol(row,grid,'Original Description')
    ud=fromCSVCol(row,grid,'User Description')
    if len(ud)>0:
        return "%s - %s" % (od,ud)
    return od

def yodlee_memo(row,grid):
    memo=fromCSVCol(row,grid,'Memo') # sometimes None
    cat=fromCSVCol(row,grid,'Category')
    cls=fromCSVCol(row,grid,'Classification')
    if len(memo)>0:
        return "%s - %s - %s" % ( memo, cat, cls)
    return "%s - %s" % ( cat, cls )

def toOFXDate(date):
    return datetime.strptime(date,'%m/%d/%y').strftime('%Y%m%d')

yodlee = {
    'BANKID':lambda row,grid: fromCSVCol(row,grid,'Account Name').split(' - ')[0],
    'ACCTID':lambda row,grid: fromCSVCol(row,grid,'Account Name').split(' - ')[-1], 
    'DTPOSTED':lambda row,grid: toOFXDate(fromCSVCol(row,grid,'Date')),
    'TRNAMT':lambda row,grid: fromCSVCol(row,grid,'Amount'),
    'FITID':lambda row,grid: fromCSVCol(row,grid,'Transaction Id'),
    'PAYEE':lambda row,grid: yodlee_dscr(row,grid),
    'MEMO':lambda row,grid: yodlee_memo(row,grid),
    'CURDEF':lambda row,grid: fromCSVCol(row,grid,'Currency'),
    'CHECKNUM':lambda row,grid: fromCSVCol(row,grid,'Transaction Id') 
}

cu = {
    'BANKID':lambda row,grid: 'Credit Union',
    'ACCTID':lambda row,grid: 'My Account',
    'DTPOSTED':lambda row,grid: toOFXDate(fromCSVCol(row,grid,'Date')),
    'TRNAMT':lambda row,grid: fromCSVCol(row,grid,'Amount').replace('$',''),
    'FITID':lambda row,grid: row,
    'PAYEE':lambda row,grid: fromCSVCol(row,grid,'Description'),
    'MEMO':lambda row,grid: fromCSVCol(row,grid,'Comments'),
    'CURDEF':lambda row,grid: 'USD',
    'CHECKNUM':lambda row,grid: fromCSVCol(row,grid,'Check Number')
}



all_mappings = {'Yodlee':yodlee, 'Credit Union':cu}
