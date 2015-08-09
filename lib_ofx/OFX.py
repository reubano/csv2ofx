""" purpose: contains csv2ofx functions
"""

class OFX
	"""
	 @param 	boolean verbose	enable verbose comments
	"""
	def __init__(source='mint', csvContent=None, verbose=False)
		source = source
		csvContent = csvContent
		verbose = verbose

		# set headers
		# modify the 'custom' section to add support for other websites
		# add additional case blocks if needed
		switch(source)
			case 'mint':
				headAccount 	= 'Account Name'
				headDate 	= 'Date'
				headTranType = 'Transaction Type'
				headAmount 	= 'Amount'
				headDesc 	= 'Original Description'
				headPayee 	= 'Description'
				headNotes 	= 'Notes'
				headSplitAccount = 'Category'
				split		= False
				break

			case 'xero':
				headAccount 	= 'AccountName'
				headDate 	= 'JournalDate'
				headAmount 	= 'NetAmount'
				headPayee 	= 'Description'
				headNotes 	= 'Product'
				headClass 	= 'Resource'
				headSplitAccount = 'AccountName'
				headId 	= 'JournalNumber'
				headCheckNum = 'Reference'
				split		= TRUE
				break

			case 'yoodle':
				headAccount	= 'Account Name'
				headDate 	= 'Date'
				headTranType	= 'Transaction Type'
				headAmount 	= 'Amount'
				headDesc 	= 'Original Description'
				headPayee 	= 'User Description'
				headNotes 	= 'Memo'
				headSplitAccount = 'Category'
				headClass 	= 'Classification'
				headId 	= 'Transaction Id'
				split		= False
				break

			case 'exim':
				headAccount	= 'Account'
				headDate 	= 'Date'
				headAmount 	= 'Amount'
				headPayee 	= 'Narration'
				headId 	= 'Reference Number'
				split		= False
				break

			case 'custom':
				headAccount	= 'Account'
				headDate 	= 'Date'
				headAmount 	= 'Amount'
				headPayee 	= 'Description'
				headCheckNum = 'Num'
				headDesc 	= 'Reference'
				headSplitAccount = 'Category'
				headId 	= 'Row'
				split		= False
				break

	 		default:
				headAccount	= 'Field'
				headAccountId= 'Field'
				headDate 	= 'Field'
				headTranType = 'Field'
				headAmount 	= 'Field'
				headDesc 	= 'Field'
				headPayee 	= 'Field'
				headNotes 	= 'Field'
				headSplitAccount = 'Field'
				headClass 	= 'Field'
				headId 	= 'Field'
				headCheckNum = 'Field'
				split		= False
			} #<-- end switch -->

		if (verbose)
			fwrite(STDOUT, "className class constructor set.\n")

	""" Cleans amount values by removing commas and converting to float

	 @param array csvContent csv content

	 @return array csvContent cleaned csv content

	 @assert (array(array('Amount' => '1,000.00'))) == array(array('Amount' => 1000.00))
	"""
	def cleanAmounts(csvContent=None)
			headAmount = headAmount

			main = function (content) use (headAmount)
				# remove all non-numeric chars and convert to float
				amount = content[headAmount]
				amount = preg_replace("/[^-0-9\.]/", "", amount)
				content[headAmount] = floatval(amount)
				return content

			csvContent = csvContent ?: csvContent
			return array_map(main, csvContent)

	""" Get main accounts (if passed findAmounts, it returns the account of the
	 split matching the given amount)

	 @param array splitContent return value of makeSplits()
	 @param array findAmounts  split amounts to find

	 @return array main accounts

	 @assert (array(array(array('Account Name' => 'account1'), array('Account Name' => 'account2')), array(array('Account Name' => 'account3'), array('Account Name' => 'account4')))) == array('accounts' => array('account1', 'account3'), 'keys' => array(0, 0))
	 @assert (array(array(array('Account Name' => 'account1', 'Amount' => -200), array('Account Name' => 'account2', 'Amount' => 200)), array(array('Account Name' => 'account3', 'Amount' => 400), array('Account Name' => 'account4', 'Amount' => -400))), array(200, 400)) == array('accounts' => array('account1', 'account3'), 'keys' => array(0, 0))
	"""
	def getAccounts(splitContent, findAmounts=None)
			hAc = headAccount
			hAm = headAmount

			current = function (tr) use (hAc)
				split = current(tr)
				return split[hAc]

			cmp = function (&split, key, findAmount) use (hAm, &newKey)
				found = (abs(split[hAm]) == findAmount)
				split = found ? split : None
				newKey = (found && !isset(newKey)) ? key : newKey

			byAmount = function (tr, findAmount) use (hAc, cmp, &newKey, &keys)
				newKey = None
				array_walk(tr, cmp, findAmount)
				keys[] = newKey
				return array_filter(tr)

			accounts = findAmounts
				? array_map(byAmount, splitContent, findAmounts)
				: splitContent

			accounts = array_map(current, accounts)
			keys = isset(keys) ? keys : array_fill(0, count(accounts), 0)
			return array('accounts' => accounts, 'keys' => keys)

	""" Detects account types of given account names

	 @param array  accounts account names
	 @param array  typeList account types and matching account names
	 @param string defType	 default account type

	 @return array the resulting account types

	 @assert (array('somecash', 'checking account', 'other'), array('Bank' => array('checking', 'savings'), 'Cash' => array('cash'))) == array('Cash', 'Bank', 'n/a')
	"""
	def getAccountTypes(accounts, typeList, defType='n/a')
			search = function (list, type, account) use (&match)
				haystack = array_fill(0, count(list), account)
				newList = array_map('stripos', haystack, list)
				zero = in_array(0, newList, TRUE)
				filtered = count(array_filter(newList))
				match = (zero || filtered) ? type : match

			main = function (account) use (typeList, search, defType, &match)
				match = None
				array_walk(typeList, search, account)
				return match ?: defType

			return array_map(main, accounts)

	""" Gets split accounts

	 @param array transaction array of splits

	 @return array accounts the resulting split account names

	 @assert (array(array('Account Name' => 'Accounts Receivable', 'Amount' => 200), array('Account Name' => 'Accounts Receivable', 'Amount' => 300), array('Account Name' => 'Sales', 'Amount' => 400))) == array('Accounts Receivable', 'Sales')
	"""
	def getSplitAccounts(transaction)
			hAc = headAccount

			main = function (split) use (hAc)
				return split[hAc]

			accounts = array_map(main, transaction)
			array_shift(accounts)
			return accounts

	""" Combines splits with the same account

	 @param array content return value of makeSplits()
	 @param array collapse accounts to collapse

	 @return array content collapsed content

	 @assert (array(array(array('Account Name' => 'Accounts Receivable', 'Amount' => 200), array('Account Name' => 'Accounts Receivable', 'Amount' => 300), array('Account Name' => 'Sales', 'Amount' => 400)), array(array('Account Name' => 'Accounts Receivable', 'Amount' => 200), array('Account Name' => 'Accounts Receivable', 'Amount' => 300), array('Account Name' => 'Sales', 'Amount' => 400))), array('Accounts Receivable')) == array(array(array('Account Name' => 'Accounts Receivable', 'Amount' => 500), array('Account Name' => 'Sales', 'Amount' => 400)), array(array('Account Name' => 'Accounts Receivable', 'Amount' => 500), array('Account Name' => 'Sales', 'Amount' => 400)))
	"""
	def collapseSplits(content, collapse)
			hAm = headAmount
			hAc = headAccount

			sum = function (&split, key, &previous) use (
				&splice, collapse, hAm, hAc
			)
				found = in_array(split[hAc], collapse)

				if (found && split[hAc] == previous['act'])
					split[hAm] += previous['amt']
					splice[] = key - 1

				previous['act'] = split[hAc]
				previous['amt'] = split[hAm]

# 			reduce = function (i, num) use (&transaction)
# 				array_splice(transaction, num - i, 1)
#
			main = function (&transaction) use (sum, &splice)
				previous = array('act' => None, 'amt' => 0)
				array_walk(transaction, sum, previous)
# 				splice ? array_walk(splice, reduce) : ''

				if (splice)
					foreach (splice as num => i)
						array_splice(transaction, num - i, 1)

				splice = None

			array_walk(content, main)
			return content

	""" Returns the split in a transaction with the largest absolute value

	 @param array splitContent return value of makeSplits()
	 @param array collapse	  accounts to collapse

	 @return array splitContent collapsed content

	 @assert (array(array(array('Amount' => 350), array('Amount' => -400)), array(array('Amount' => 100), array('Amount' => -400), array('Amount' => 300)))) == array(400, 400)
	"""
	def getMaxSplitAmounts(splitContent)
			hAmount = headAmount

			maxAbs = function (a, b) use (hAmount)
				return max(abs(a), abs(b[hAmount]))

			reduce = function (item) use (maxAbs)
				return array_reduce(item, maxAbs)

			return array_map(reduce, splitContent)

	""" Verifies that the splits of each transaction sum to 0

	 @param array splitContent return value of makeSplits()

	 @return 	boolean	true on success

	 @assert (array(array(array('Amount' => 100), array('Amount' => -100)), array(array('Amount' => -300), array('Amount' => 200), array('Amount' => 100)))) == true
	"""
	def verifySplits(splitContent)
			hAm = headAmount

			sum = function (a, b) use (hAm)
				return round((a + b[hAm]), 2)

			filter = function (tr) use (sum)
				return array_reduce(tr, sum)

			result = array_filter(splitContent, filter)

			if (result)
				throw new Exception('Invalid split of '.result.' at '.
					'transaction '.result.' from '.className.'->'.
					__FUNCTION__.'() line '.__LINE__
				)
			else
				return true


	""" @param array csvContent csv content

	 @return 	array	splitContent	csv content organized by transaction

	 @assert (array(array('Amount' => 1,000.00, 'Date' => '06/12/10', 'Category' => 'Checking', 'Account Name' => 'account1'), array('Amount' => 1,000.00, 'Date' => '06/12/10', 'Category' => 'Checking', 'Account Name' => 'account2'))) == array(array(array('Amount' => 1,000.00, 'Date' => '06/12/10', 'Category' => 'Checking', 'Account Name' => 'account1')), array(array('Amount' => 1,000.00, 'Date' => '06/12/10', 'Category' => 'Checking', 'Account Name' => 'account2')))
	"""
	def makeSplits(csvContent=None)
			headId = isset(headId) ? headId : None

			main = function (content, key) use (&splitContent, headId)
				id = headId ? content[headId] : key
				splitContent[id][] = content

			csvContent = csvContent ?: csvContent
			array_walk(csvContent, main)
			return splitContent

	""" Sets QIF format transaction variables

	 @param 	array 	tr		   		 the transaction
	 @param 	string 	timeStamp 		 the time stamp
	 @param 	string 	defSplitAccount the default split account

	 @return 	array	the QIF content

	 @assert (array('Transaction Type' => 'debit', 'Amount' => 1000.00, 'Date' => '06/12/10', 'Description' => 'payee', 'Original Description' => 'description', 'Notes' => 'notes', 'Category' => 'Checking', 'Account Name' => 'account')) == array('Amount' => '-1000', 'Payee' => 'payee', 'Date' => '06/12/10', 'Desc' => 'description notes', 'Id' => '4fe86d9de995225b174fb3116ca6b1f4', 'CheckNum' => None, 'Type' => 'debit', 'SplitAccount' => 'Checking', 'SplitAccountId' => '195917574edc9b6bbeb5be9785b6a479')
	"""
	def getTransactionData(tr, defSplitAccount='Orphan')
			amount = tr[headAmount]
			type = isset(headTranType) ? tr[headTranType] : None
			amount = (type == 'debit') ? '-'.amount : amount
			date = date('m/d/y', strtotime(tr[headDate]))
			payee = isset(headPayee) ? tr[headPayee] : None
			desc = isset(headDesc) ? tr[headDesc] : None
			notes = isset(headNotes) ? tr[headNotes] : None
			class = isset(headClass) ? tr[headClass] : None
			id = isset(headId) ? tr[headId] : None

			checkNum = isset(headCheckNum)
				? tr[headCheckNum]
				: None

			splitAccount = isset(headSplitAccount)
				? tr[headSplitAccount]
				: defSplitAccount

			splitAccountId = md5(splitAccount)

			# qif doesn't support notes or class so add them to description
			sep = desc ? ' ' : ''
			desc .= notes ? sep.notes : None
			sep = desc ? ' ' : ''
			desc .= class ? sep.class : None

			# if no id, create it using check number or md5
			# hash of the transaction details
			id = id ?: checkNum
			id = id ?: md5(date.amount.payee.splitAccount.desc)

			return array(
				'Amount' => amount, 'Payee' => payee, 'Date' => date,
				'Desc' => desc, 'Id' => id, 'CheckNum' => checkNum,
				'Type' => type, 'SplitAccount' => splitAccount,
				'SplitAccountId' => splitAccountId
			)


	""" Gets QIF format account content

	 @param 	string 	account		the account
	 @param 	string 	accountType	the account types
	 @return 	string	the QIF content

	 @assert ('account', 'type') == "!Account\nNaccount\nTtype\n^\n"
	"""
	def getQIFAccountHeader(account, accountType)
			return "!Account\nNaccount\nTaccountType\n^\n"

	""" Gets QIF format transaction content

	 @param 	string 	accountType	the account types
	 @return 	string	content		the QIF content

	 @assert ('type', array('Payee' => 'payee', 'Amount' => 100, 'CheckNum' => 1, 'Date' => '01/01/12')) == "!Type:type\nN1\nD01/01/12\nPpayee\nT100\n"
	 @assert ('type', array('Payee' => 'payee', 'Amount' => 100, 'Date' => '01/01/12')) == "!Type:type\nD01/01/12\nPpayee\nT100\n"
	"""
	def getQIFTransactionContent(accountType, data)
			# switch signs if source is xero
			amt = data['Amount']
# 			newAmt = (substr(amt, 0, 1) == '-') ? substr(amt, 1) : '-'.amt
# 			amt = (source == 'xero') ? newAmt : amt
			content = "!Type:accountType\n"
			content .= isset(data['CheckNum']) ? "Ndata[CheckNum]\n" : ''
			content .= "Ddata[Date]\nPdata[Payee]\nTamt\n"
			return content

	""" Gets QIF format split content

	 @return 	string the QIF content

	 @assert ('account', array('Desc' => 'desc', 'Amount' => 100)) == "Saccount\nEdesc\n100\n"
	"""
	def getQIFSplitContent(splitAccount, data)
			# switch signs if source is xero
			amt = data['Amount']
			newAmt = (substr(amt, 0, 1) == '-') ? substr(amt, 1) : '-'.amt
			amt = (source == 'xero') ? newAmt : amt
			return "SsplitAccount\nEdata[Desc]\n\amt\n"

	""" Gets QIF transaction footer

	 @return 	string the QIF content

	 @assert () == "^\n"
	"""
	def getQIFTransactionFooter()
			return "^\n"

	""" Gets OFX format transaction content

	 @param 	string timeStamp	the time in mmddyy_hhmmss format
	 @return 	string the OFX content

	 @assert (20120101111111) == "<OFX>\n\t<SIGNONMSGSRSV1>\n\t\t<SONRS>\n\t\t\t<STATUS>\n\t\t\t\t<CODE>0</CODE>\n\t\t\t\t<SEVERITY>INFO</SEVERITY>\n\t\t\t</STATUS>\n\t\t\t<DTSERVER>20120101111111</DTSERVER>\n\t\t\t<LANGUAGE>ENG</LANGUAGE>\n\t\t</SONRS>\n\t</SIGNONMSGSRSV1>\n"
	"""
	def getOFXHeader(timeStamp, language='ENG')
			return
				"<OFX>\n".
				"\t<SIGNONMSGSRSV1>\n".
				"\t\t<SONRS>\n".
				"\t\t\t<STATUS>\n".
				"\t\t\t\t<CODE>0</CODE>\n".
				"\t\t\t\t<SEVERITY>INFO</SEVERITY>\n".
				"\t\t\t</STATUS>\n".
				"\t\t\t<DTSERVER>timeStamp</DTSERVER>\n".
				"\t\t\t<LANGUAGE>language</LANGUAGE>\n".
				"\t\t</SONRS>\n".
				"\t</SIGNONMSGSRSV1>\n"


	""" Gets OFX format transaction content

	 @param 	string timeStamp	the time in mmddyy_hhmmss format
	 @return 	string the OFX content

	 @assert () == "\t<BANKMSGSRSV1>\n\t\t<INTRATRNRS>\n\t\t\t<TRNUID></TRNUID>\n\t\t\t<STATUS>\n\t\t\t\t<CODE>0</CODE>\n\t\t\t\t<SEVERITY>INFO</SEVERITY>\n\t\t\t</STATUS>\n"
	"""
	def getOFXResponseStart(respType='INTRATRNRS')
			return
				"\t<BANKMSGSRSV1>\n".
				"\t\t<respType>\n".
				"\t\t\t<TRNUID></TRNUID>\n".
				"\t\t\t<STATUS>\n".
				"\t\t\t\t<CODE>0</CODE>\n".
				"\t\t\t\t<SEVERITY>INFO</SEVERITY>\n".
				"\t\t\t</STATUS>\n"

	""" Gets OFX format transaction account start content

	 @return 	string the OFX content

	 @assert ('USD', 1, 'account', 'type', 20120101, 20120101) == "\t\t\t<STMTRS>\n\t\t\t\t<CURDEF>USD</CURDEF>\n\t\t\t\t<BANKACCTFROM>\n\t\t\t\t\t<BANKID>1</BANKID>\n\t\t\t\t\t<ACCTID>account</ACCTID>\n\t\t\t\t\t<ACCTTYPE>type</ACCTTYPE>\n\t\t\t\t</BANKACCTFROM>\n\t\t\t\t<BANKTRANLIST>\n\t\t\t\t\t<DTSTART>20120101</DTSTART>\n\t\t\t\t\t<DTEND>20120101</DTEND>\n"
	"""
	def getOFXTransactionAccountStart(
		currency, accountId, account, accountType, startDate, endDate
	)
			return
				"\t\t\t<STMTRS>\n".
				"\t\t\t\t<CURDEF>currency</CURDEF>\n".
				"\t\t\t\t<BANKACCTFROM>\n".
				"\t\t\t\t\t<BANKID>accountId</BANKID>\n".
				"\t\t\t\t\t<ACCTID>account</ACCTID>\n".
				"\t\t\t\t\t<ACCTTYPE>accountType</ACCTTYPE>\n".
				"\t\t\t\t</BANKACCTFROM>\n".
				"\t\t\t\t<BANKTRANLIST>\n".
				"\t\t\t\t\t<DTSTART>startDate</DTSTART>\n".
				"\t\t\t\t\t<DTEND>endDate</DTEND>\n"

	""" Gets OFX format transaction content

	 @return 	string the OFX content

	 @assert (20120101111111, array('Type' => 'type', 'Amount' => 100, 'Id' => 1, 'CheckNum' => 1, 'Payee' => 'payee', 'Desc' => 'memo')) == "\t\t\t\t\t<STMTTRN>\n\t\t\t\t\t\t<TRNTYPE>type</TRNTYPE>\n\t\t\t\t\t\t<DTPOSTED>20120101111111</DTPOSTED>\n\t\t\t\t\t\t<TRNAMT>100</TRNAMT>\n\t\t\t\t\t\t<FITID>1</FITID>\n\t\t\t\t\t\t<CHECKNUM>1</CHECKNUM>\n\t\t\t\t\t\t<NAME>payee</NAME>\n\t\t\t\t\t\t<MEMO>memo</MEMO>\n\t\t\t\t\t</STMTTRN>\n"
	"""
	def getOFXTransaction(timeStamp, data)
			return
				"\t\t\t\t\t<STMTTRN>\n".
				"\t\t\t\t\t\t<TRNTYPE>data[Type]</TRNTYPE>\n".
				"\t\t\t\t\t\t<DTPOSTED>timeStamp</DTPOSTED>\n".
				"\t\t\t\t\t\t<TRNAMT>data[Amount]</TRNAMT>\n".
				"\t\t\t\t\t\t<FITID>data[Id]</FITID>\n".
				"\t\t\t\t\t\t<CHECKNUM>data[CheckNum]</CHECKNUM>\n".
				"\t\t\t\t\t\t<NAME>data[Payee]</NAME>\n".
				"\t\t\t\t\t\t<MEMO>data[Desc]</MEMO>\n".
				"\t\t\t\t\t</STMTTRN>\n"

	""" Gets OFX format transaction account end content

	 @return 	string the OFX content

	 @assert (150, 20120101111111) == "\t\t\t\t</BANKTRANLIST>\n\t\t\t\t<LEDGERBAL>\n\t\t\t\t\t<BALAMT>150</BALAMT>\n\t\t\t\t\t<DTASOF>20120101111111</DTASOF>\n\t\t\t\t</LEDGERBAL>\n\t\t\t</STMTRS>\n"
	"""
	def getOFXTransactionAccountEnd(balance=None, timeStamp=None)
			return
				"\t\t\t\t</BANKTRANLIST>\n".
				"\t\t\t\t<LEDGERBAL>\n".
				"\t\t\t\t\t<BALAMT>balance</BALAMT>\n".
				"\t\t\t\t\t<DTASOF>timeStamp</DTASOF>\n".
				"\t\t\t\t</LEDGERBAL>\n".
				"\t\t\t</STMTRS>\n"

	""" Gets OFX transfer start

	 @param 	string accountType	the account types
	 @return 	string the QIF content

	 @assert ('USD', 20120101111111, 1, 'account', 'type', array('SplitAccountId' => 2, 'SplitAccount' => 'split_account', 'Amount' => 100)) == "\t\t\t<INTRARS>\n\t\t\t\t<CURDEF>USD</CURDEF>\n\t\t\t\t<SRVRTID>20120101111111</SRVRTID>\n\t\t\t\t<XFERINFO>\n\t\t\t\t\t<BANKACCTFROM>\n\t\t\t\t\t\t<BANKID>1</BANKID>\n\t\t\t\t\t\t<ACCTID>account</ACCTID>\n\t\t\t\t\t\t<ACCTTYPE>type</ACCTTYPE>\n\t\t\t\t\t</BANKACCTFROM>\n\t\t\t\t\t<BANKACCTTO>\n\t\t\t\t\t\t<BANKID>2</BANKID>\n\t\t\t\t\t\t<ACCTID>split_account</ACCTID>\n\t\t\t\t\t\t<ACCTTYPE>type</ACCTTYPE>\n\t\t\t\t\t</BANKACCTTO>\n\t\t\t\t\t<TRNAMT>100</TRNAMT>\n\t\t\t\t</XFERINFO>\n\t\t\t\t<DTPOSTED>20120101111111</DTPOSTED>\n\t\t\t</INTRARS>\n"
	"""
	def getOFXTransfer(
		currency, timeStamp, accountId, account, accountType, data
	)
			return
				"\t\t\t<INTRARS>\n". # Begin transfer response
				"\t\t\t\t<CURDEF>currency</CURDEF>\n".
				"\t\t\t\t<SRVRTID>timeStamp</SRVRTID>\n".
				"\t\t\t\t<XFERINFO>\n". # Begin transfer aggregate
				"\t\t\t\t\t<BANKACCTFROM>\n".
				"\t\t\t\t\t\t<BANKID>accountId</BANKID>\n".
				"\t\t\t\t\t\t<ACCTID>account</ACCTID>\n".
				"\t\t\t\t\t\t<ACCTTYPE>accountType</ACCTTYPE>\n".
				"\t\t\t\t\t</BANKACCTFROM>\n".
				"\t\t\t\t\t<BANKACCTTO>\n".
				"\t\t\t\t\t\t<BANKID>data[SplitAccountId]</BANKID>\n".
				"\t\t\t\t\t\t<ACCTID>data[SplitAccount]</ACCTID>\n".
				"\t\t\t\t\t\t<ACCTTYPE>accountType</ACCTTYPE>\n".
				"\t\t\t\t\t</BANKACCTTO>\n".
				"\t\t\t\t\t<TRNAMT>data[Amount]</TRNAMT>\n".
				"\t\t\t\t</XFERINFO>\n". # End transfer aggregate
				"\t\t\t\t<DTPOSTED>timeStamp</DTPOSTED>\n".
				"\t\t\t</INTRARS>\n" # End transfer response

	""" Gets OFX transfer footer

	 @return 	string the OFX content

	 @assert () == "\t\t</INTRATRNRS>\n\t</BANKMSGSRSV1>\n</OFX>"
	"""
	def getOFXResponseEnd(respType='INTRATRNRS')
			# need to make variables reference
			return "\t\t</respType>\n\t</BANKMSGSRSV1>\n</OFX>" # End response
	} #<-- end class -->
