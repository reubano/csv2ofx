<?php
/*******************************************************************************
 * purpose: contains csv2ofx functions
 ******************************************************************************/

//<-- begin class -->
class OFX {
	protected $className = __CLASS__;	// class name
	protected $verbose;
	protected $source;
	public $split;
	public $newContent;
	public $accounts = array();
	public $csvContent;
	public $headAccount;
	public $headAccountId;
	public $headDate;
	public $headTranType;
	public $headAmount;
	public $headDesc;
	public $headPayee;
	public $headNotes;
	public $headSplitAccount;
	public $headClass;
	public $headId;
	public $headCheckNum;

	/**
	 ***************************************************************************
	 * The class constructor
	 *
	 * @param 	boolean $verbose	enable verbose comments
	 **************************************************************************/
	function __construct($source='mint', $csvContent=null, $verbose=FALSE) {
		$this->source = $source;
		$this->csvContent = $csvContent;
		$this->verbose = $verbose;

		// set headers
		// modify the 'custom' section to add support for other websites
		// add additional case blocks if needed
		switch($this->source) {
			case 'mint':
				$this->headAccount 	= 'Account Name';
				$this->headDate 	= 'Date';
				$this->headTranType = 'Transaction Type';
				$this->headAmount 	= 'Amount';
				$this->headDesc 	= 'Original Description';
				$this->headPayee 	= 'Description';
				$this->headNotes 	= 'Notes';
				$this->headSplitAccount = 'Category';
				$this->split		= FALSE;
				break;

			case 'xero':
				$this->headAccount 	= 'AccountName';
				$this->headDate 	= 'JournalDate';
				$this->headAmount 	= 'NetAmount';
				$this->headPayee 	= 'Description';
				$this->headNotes 	= 'Product';
				$this->headClass 	= 'Resource';
				$this->headSplitAccount = 'AccountName';
				$this->headId 	= 'JournalNumber';
				$this->headCheckNum = 'Reference';
				$this->split		= TRUE;
				break;

			case 'yoodle':
				$this->headAccount	= 'Account Name';
				$this->headDate 	= 'Date';
				$this->headTranType	= 'Transaction Type';
				$this->headAmount 	= 'Amount';
				$this->headDesc 	= 'Original Description';
				$this->headPayee 	= 'User Description';
				$this->headNotes 	= 'Memo';
				$this->headSplitAccount = 'Category';
				$this->headClass 	= 'Classification';
				$this->headId 	= 'Transaction Id';
				$this->split		= FALSE;
				break;

			case 'exim':
				$this->headAccount	= 'Account';
				$this->headDate 	= 'Date';
				$this->headAmount 	= 'Amount';
				$this->headPayee 	= 'Narration';
				$this->headId 	= 'Reference Number';
				$this->split		= FALSE;
				break;

			case 'custom':
				$this->headAccount	= 'Account';
				$this->headDate 	= 'Date';
				$this->headAmount 	= 'Amount';
				$this->headPayee 	= 'Description';
				$this->headCheckNum = 'Num';
				$this->headDesc 	= 'Reference';
				$this->headSplitAccount = 'Category';
				$this->headId 	= 'Row';
				$this->split		= FALSE;
				break;

	 		default:
				$this->headAccount	= 'Field';
				$this->headAccountId= 'Field';
				$this->headDate 	= 'Field';
				$this->headTranType = 'Field';
				$this->headAmount 	= 'Field';
				$this->headDesc 	= 'Field';
				$this->headPayee 	= 'Field';
				$this->headNotes 	= 'Field';
				$this->headSplitAccount = 'Field';
				$this->headClass 	= 'Field';
				$this->headId 	= 'Field';
				$this->headCheckNum = 'Field';
				$this->split		= FALSE;
			} //<-- end switch -->

		if ($this->verbose) {
			fwrite(STDOUT, "$this->className class constructor set.\n");
		} //<-- end if -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Cleans amount values by removing commas and converting to float
	 *
	 * @param array $csvContent csv content
	 *
	 * @return array $csvContent cleaned csv content
	 *
	 * @assert (array(array('Amount' => '$1,000.00'))) == array(array('Amount' => 1000.00))
	 **************************************************************************/
	public function cleanAmounts($csvContent=null) {
		try {
			$headAmount = $this->headAmount;

			$main = function ($content) use ($headAmount) {
				// remove all non-numeric chars and convert to float
				$amount = $content[$headAmount];
				$amount = preg_replace("/[^-0-9\.]/", "", $amount);
				$content[$headAmount] = floatval($amount);
				return $content;
			};

			$csvContent = $csvContent ?: $this->csvContent;
			return array_map($main, $csvContent);
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Get main accounts (if passed $findAmounts, it returns the account of the
	 * split matching the given amount)
	 *
	 * @param array $splitContent return value of makeSplits();
	 * @param array $findAmounts  split amounts to find
	 *
	 * @return array main accounts
	 *
	 * @assert (array(array(array('Account Name' => 'account1'), array('Account Name' => 'account2')), array(array('Account Name' => 'account3'), array('Account Name' => 'account4')))) == array('accounts' => array('account1', 'account3'), 'keys' => array(0, 0))
	 * @assert (array(array(array('Account Name' => 'account1', 'Amount' => -200), array('Account Name' => 'account2', 'Amount' => 200)), array(array('Account Name' => 'account3', 'Amount' => 400), array('Account Name' => 'account4', 'Amount' => -400))), array(200, 400)) == array('accounts' => array('account1', 'account3'), 'keys' => array(0, 0))
	 **************************************************************************/
	public function getAccounts($splitContent, $findAmounts=null) {
		try {
			$hAc = $this->headAccount;
			$hAm = $this->headAmount;

			$current = function ($tr) use ($hAc) {
				$split = current($tr);
				return $split[$hAc];
			}; //<-- end for loop -->

			$cmp = function (&$split, $key, $findAmount) use ($hAm, &$newKey) {
				$found = (abs($split[$hAm]) == $findAmount);
				$split = $found ? $split : null;
				$newKey = ($found && !isset($newKey)) ? $key : $newKey;
			};

			$byAmount = function ($tr, $findAmount) use ($hAc, $cmp, &$newKey, &$keys) {
				$newKey = null;
				array_walk($tr, $cmp, $findAmount);
				$keys[] = $newKey;
				return array_filter($tr);
			}; //<-- end for loop -->

			$accounts = $findAmounts
				? array_map($byAmount, $splitContent, $findAmounts)
				: $splitContent;

			$accounts = array_map($current, $accounts);
			$keys = isset($keys) ? $keys : array_fill(0, count($accounts), 0);
			return array('accounts' => $accounts, 'keys' => $keys);
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Detects account types of given account names
	 *
	 * @param array  $accounts account names
	 * @param array  $typeList account types and matching account names
	 * @param string $defType	 default account type
	 *
	 * @return array the resulting account types
	 *
	 * @assert (array('somecash', 'checking account', 'other'), array('Bank' => array('checking', 'savings'), 'Cash' => array('cash'))) == array('Cash', 'Bank', 'n/a')
	 **************************************************************************/
	public function getAccountTypes($accounts, $typeList, $defType='n/a') {
		try {
			$search = function ($list, $type, $account) use (&$match) {
				$haystack = array_fill(0, count($list), $account);
				$newList = array_map('stripos', $haystack, $list);
				$zero = in_array(0, $newList, TRUE);
				$filtered = count(array_filter($newList));
				$match = ($zero || $filtered) ? $type : $match;
			};

			$main = function ($account) use ($typeList, $search, $defType, &$match) {
				$match = null;
				array_walk($typeList, $search, $account);
				return $match ?: $defType;
			}; //<-- end for loop -->

			return array_map($main, $accounts);
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.
				'->'.__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Gets split accounts
	 *
	 * @param array $transaction array of splits;
	 *
	 * @return array $accounts the resulting split account names
	 *
	 * @assert (array(array('Account Name' => 'Accounts Receivable', 'Amount' => 200), array('Account Name' => 'Accounts Receivable', 'Amount' => 300), array('Account Name' => 'Sales', 'Amount' => 400))) == array('Accounts Receivable', 'Sales')
	 **************************************************************************/
	public function getSplitAccounts($transaction) {
		try {
			$hAc = $this->headAccount;

			$main = function ($split) use ($hAc) {
				return $split[$hAc];
			}; //<-- end for loop -->

			$accounts = array_map($main, $transaction);
			array_shift($accounts);
			return $accounts;
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.
				'->'.__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Combines splits with the same account
	 *
	 * @param array $content return value of makeSplits();
	 * @param array $collapse accounts to collapse
	 *
	 * @return array $content collapsed content;
	 *
	 * @assert (array(array(array('Account Name' => 'Accounts Receivable', 'Amount' => 200), array('Account Name' => 'Accounts Receivable', 'Amount' => 300), array('Account Name' => 'Sales', 'Amount' => 400)), array(array('Account Name' => 'Accounts Receivable', 'Amount' => 200), array('Account Name' => 'Accounts Receivable', 'Amount' => 300), array('Account Name' => 'Sales', 'Amount' => 400))), array('Accounts Receivable')) == array(array(array('Account Name' => 'Accounts Receivable', 'Amount' => 500), array('Account Name' => 'Sales', 'Amount' => 400)), array(array('Account Name' => 'Accounts Receivable', 'Amount' => 500), array('Account Name' => 'Sales', 'Amount' => 400)))
	 **************************************************************************/
	public function collapseSplits($content, $collapse) {
		try {
			$hAm = $this->headAmount;
			$hAc = $this->headAccount;

			$sum = function (&$split, $key, &$previous) use (
				&$splice, $collapse, $hAm, $hAc
			) {
				$found = in_array($split[$hAc], $collapse);

				if ($found && $split[$hAc] == $previous['act']) {
					$split[$hAm] += $previous['amt'];
					$splice[] = $key - 1;
				} //<-- end if -->

				$previous['act'] = $split[$hAc];
				$previous['amt'] = $split[$hAm];
			};

// 			$reduce = function ($i, $num) use (&$transaction) {
// 				array_splice($transaction, $num - $i, 1);
// 			};

			$main = function (&$transaction) use ($sum, &$splice) {
				$previous = array('act' => null, 'amt' => 0);
				array_walk($transaction, $sum, $previous);
// 				$splice ? array_walk($splice, $reduce) : '';

				if ($splice) {
					foreach ($splice as $num => $i) {
						array_splice($transaction, $num - $i, 1);
					};
				}

				$splice = null;
			};

			array_walk($content, $main);
			return $content;
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.
				'->'.__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Returns the split in a transaction with the largest absolute value
	 *
	 * @param array $splitContent return value of makeSplits();
	 * @param array $collapse	  accounts to collapse
	 *
	 * @return array $splitContent collapsed content;
	 *
	 * @assert (array(array(array('Amount' => 350), array('Amount' => -400)), array(array('Amount' => 100), array('Amount' => -400), array('Amount' => 300)))) == array(400, 400)
	 **************************************************************************/
	public function getMaxSplitAmounts($splitContent) {
		try {
			$hAmount = $this->headAmount;

			$maxAbs = function ($a, $b) use ($hAmount) {
				return max(abs($a), abs($b[$hAmount]));
			};

			$reduce = function ($item) use ($maxAbs) {
				return array_reduce($item, $maxAbs);
			};

			return array_map($reduce, $splitContent);
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.
				'->'.__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Verifies that the splits of each transaction sum to 0
	 *
	 * @param array $splitContent return value of makeSplits();
	 *
	 * @return 	boolean	true on success
	 *
	 * @assert (array(array(array('Amount' => 100), array('Amount' => -100)), array(array('Amount' => -300), array('Amount' => 200), array('Amount' => 100)))) == true
	 **************************************************************************/
	public function verifySplits($splitContent) {
		try {
			$hAm = $this->headAmount;

			$sum = function ($a, $b) use ($hAm) {
				return round(($a + $b[$hAm]), 2);
			};

			$filter = function ($tr) use ($sum) {
				return array_reduce($tr, $sum);
			};

			$result = array_filter($splitContent, $filter);

			if ($result) {
				throw new Exception('Invalid split of '.$result.' at '.
					'transaction '.$result.' from '.$this->className.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} else {
				return true;
			}; //<-- end if -->

		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.
				'->'.__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * @param array $csvContent csv content
	 *
	 * @return 	array	$splitContent	csv content organized by transaction
	 *
	 * @assert (array(array('Amount' => 1,000.00, 'Date' => '06/12/10', 'Category' => 'Checking', 'Account Name' => 'account1'), array('Amount' => 1,000.00, 'Date' => '06/12/10', 'Category' => 'Checking', 'Account Name' => 'account2'))) == array(array(array('Amount' => 1,000.00, 'Date' => '06/12/10', 'Category' => 'Checking', 'Account Name' => 'account1')), array(array('Amount' => 1,000.00, 'Date' => '06/12/10', 'Category' => 'Checking', 'Account Name' => 'account2')))
	 **************************************************************************/
	public function makeSplits($csvContent=null) {
		try {
			$headId = isset($this->headId) ? $this->headId : null;

			$main = function ($content, $key) use (&$splitContent, $headId) {
				$id = $headId ? $content[$headId] : $key;
				$splitContent[$id][] = $content;
			};

			$csvContent = $csvContent ?: $this->csvContent;
			array_walk($csvContent, $main);
			return $splitContent;
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.
				'->'.__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Sets QIF format transaction variables
	 *
	 * @param 	array 	$tr		   		 the transaction
	 * @param 	string 	$timeStamp 		 the time stamp
	 * @param 	string 	$defSplitAccount the default split account
	 *
	 * @return 	array	the QIF content
	 *
	 * @assert (array('Transaction Type' => 'debit', 'Amount' => 1000.00, 'Date' => '06/12/10', 'Description' => 'payee', 'Original Description' => 'description', 'Notes' => 'notes', 'Category' => 'Checking', 'Account Name' => 'account')) == array('Amount' => '-1000', 'Payee' => 'payee', 'Date' => '06/12/10', 'Desc' => 'description notes', 'Id' => '4fe86d9de995225b174fb3116ca6b1f4', 'CheckNum' => null, 'Type' => 'debit', 'SplitAccount' => 'Checking', 'SplitAccountId' => '195917574edc9b6bbeb5be9785b6a479')
	 **************************************************************************/
	public function getTransactionData($tr, $defSplitAccount='Orphan') {
		try {
			$amount = $tr[$this->headAmount];
			$type = isset($this->headTranType) ? $tr[$this->headTranType] : null;
			$amount = ($type == 'debit') ? '-'.$amount : $amount;
			$date = date('m/d/y', strtotime($tr[$this->headDate]));
			$payee = isset($this->headPayee) ? $tr[$this->headPayee] : null;
			$desc = isset($this->headDesc) ? $tr[$this->headDesc] : null;
			$notes = isset($this->headNotes) ? $tr[$this->headNotes] : null;
			$class = isset($this->headClass) ? $tr[$this->headClass] : null;
			$id = isset($this->headId) ? $tr[$this->headId] : null;

			$checkNum = isset($this->headCheckNum)
				? $tr[$this->headCheckNum]
				: null;

			$splitAccount = isset($this->headSplitAccount)
				? $tr[$this->headSplitAccount]
				: $defSplitAccount;

			$splitAccountId = md5($splitAccount);

			// qif doesn't support notes or class so add them to description
			$sep = $desc ? ' ' : '';
			$desc .= $notes ? $sep.$notes : null;
			$sep = $desc ? ' ' : '';
			$desc .= $class ? $sep.$class : null;

			// if no id, create it using check number or md5
			// hash of the transaction details
			$id = $id ?: $checkNum;
			$id = $id ?: md5($date.$amount.$payee.$splitAccount.$desc);

			return array(
				'Amount' => $amount, 'Payee' => $payee, 'Date' => $date,
				'Desc' => $desc, 'Id' => $id, 'CheckNum' => $checkNum,
				'Type' => $type, 'SplitAccount' => $splitAccount,
				'SplitAccountId' => $splitAccountId
			);

		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Gets QIF format account content
	 *
	 * @param 	string 	$account		the account
	 * @param 	string 	$accountType	the account types
	 * @return 	string	the QIF content
	 *
	 * @assert ('account', 'type') == "!Account\nNaccount\nTtype\n^\n"
	 **************************************************************************/
	public function getQIFTransactionHeader($account, $accountType) {
		try {
			return "!Account\nN$account\nT$accountType\n^\n";
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Gets QIF format transaction content
	 *
	 * @param 	string 	$accountType	the account types
	 * @return 	string	$content		the QIF content
	 *
	 * @assert ('type', array('Payee' => 'payee', 'Amount' => 100, 'CheckNum' => 1, 'Date' => '01/01/12')) == "!Type:type\nN1\nD01/01/12\nPpayee\nT100\n"
	 * @assert ('type', array('Payee' => 'payee', 'Amount' => 100, 'Date' => '01/01/12')) == "!Type:type\nD01/01/12\nPpayee\nT100\n"
	 **************************************************************************/
	public function getQIFTransactionContent($accountType, $data) {
		try {
			// switch signs if source is xero
			$amt = $data['Amount'];
// 			$newAmt = (substr($amt, 0, 1) == '-') ? substr($amt, 1) : '-'.$amt;
// 			$amt = ($this->source == 'xero') ? $newAmt : $amt;
			$content = "!Type:$accountType\n";
			$content .= isset($data['CheckNum']) ? "N$data[CheckNum]\n" : '';
			$content .= "D$data[Date]\nP$data[Payee]\nT$amt\n";
			return $content;
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Gets QIF format split content
	 *
	 * @return 	string the QIF content
	 *
	 * @assert ('account', array('Desc' => 'desc', 'Amount' => 100)) == "Saccount\nEdesc\n$100\n"
	 **************************************************************************/
	public function getQIFSplitContent($splitAccount, $data) {
		try {
			// switch signs if source is xero
			$amt = $data['Amount'];
			$newAmt = (substr($amt, 0, 1) == '-') ? substr($amt, 1) : '-'.$amt;
			$amt = ($this->source == 'xero') ? $newAmt : $amt;
			return "S$splitAccount\nE$data[Desc]\n\$$amt\n";
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Gets QIF transaction footer
	 *
	 * @return 	string the QIF content
	 *
	 * @assert () == "^\n"
	 **************************************************************************/
	public function getQIFTransactionFooter() {
		try {
			return "^\n";
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Gets OFX format transaction content
	 *
	 * @param 	string $timeStamp	the time in mmddyy_hhmmss format
	 * @return 	string the OFX content
	 *
	 * @assert (20120101111111) == "<OFX>\n\t<SIGNONMSGSRSV1>\n\t\t<SONRS>\n\t\t\t<STATUS>\n\t\t\t\t<CODE>0</CODE>\n\t\t\t\t<SEVERITY>INFO</SEVERITY>\n\t\t\t</STATUS>\n\t\t\t<DTSERVER>20120101111111</DTSERVER>\n\t\t\t<LANGUAGE>ENG</LANGUAGE>\n\t\t</SONRS>\n\t</SIGNONMSGSRSV1>\n\t<BANKMSGSRSV1><STMTTRNRS>\n\t\t<TRNUID>20120101111111</TRNUID>\n\t\t<STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS>\n"
	 **************************************************************************/
	public function getOFXTransactionHeader($timeStamp, $language='ENG') {
		try {
			return
				"<OFX>\n".
				"\t<SIGNONMSGSRSV1>\n".
				"\t\t<SONRS>\n".
				"\t\t\t<STATUS>\n".
				"\t\t\t\t<CODE>0</CODE>\n".
				"\t\t\t\t<SEVERITY>INFO</SEVERITY>\n".
				"\t\t\t</STATUS>\n".
				"\t\t\t<DTSERVER>$timeStamp</DTSERVER>\n".
				"\t\t\t<LANGUAGE>$language</LANGUAGE>\n".
				"\t\t</SONRS>\n".
				"\t</SIGNONMSGSRSV1>\n".
				"\t<BANKMSGSRSV1><STMTTRNRS>\n".
				"\t\t<TRNUID>$timeStamp</TRNUID>\n".
				"\t\t<STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS>".
				"\n";
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Gets OFX format transaction account start content
	 *
	 * @return 	string the OFX content
	 *
	 * @assert ('USD', 1, 'account', 'type', 20120101) == "\t<STMTRS>\n\t\t<CURDEF>USD</CURDEF>\n\t\t<BANKACCTFROM>\n\t\t\t<BANKID>1</BANKID>\n\t\t\t<ACCTID>account</ACCTID>\n\t\t\t<ACCTTYPE>type</ACCTTYPE>\n\t\t</BANKACCTFROM>\n\t\t<BANKTRANLIST>\n\t\t\t<DTSTART>20120101</DTSTART>\n\t\t\t<DTEND>20120101</DTEND>\n"
	 **************************************************************************/
	public function getOFXTransactionAccountStart(
		$currency, $accountId, $account, $accountType, $dateStamp
	) {
		try {
			return
				"\t<STMTRS>\n".
				"\t\t<CURDEF>$currency</CURDEF>\n".
				"\t\t<BANKACCTFROM>\n".
				"\t\t\t<BANKID>$accountId</BANKID>\n".
				"\t\t\t<ACCTID>$account</ACCTID>\n".
				"\t\t\t<ACCTTYPE>$accountType</ACCTTYPE>\n".
				"\t\t</BANKACCTFROM>\n".
				"\t\t<BANKTRANLIST>\n".
				"\t\t\t<DTSTART>$dateStamp</DTSTART>\n".
				"\t\t\t<DTEND>$dateStamp</DTEND>\n";
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Gets OFX format transaction content
	 *
	 * @return 	string the OFX content
	 *
	 * @assert (20120101111111, array('Type' => 'type', 'Amount' => 100, 'Id' => 1, 'Payee' => 'payee', 'Memo' => 'memo')) == "\t\t\t\t<STMTTRN>\n\t\t\t\t\t<TRNTYPE>type</TRNTYPE>\n\t\t\t\t\t<DTPOSTED>20120101111111</DTPOSTED>\n\t\t\t\t\t<TRNAMT>100</TRNAMT>\n\t\t\t\t\t<FITID>1</FITID>\n\t\t\t\t\t<CHECKNUM>1</CHECKNUM>\n\t\t\t\t\t<NAME>payee</NAME>\n\t\t\t\t\t<MEMO>memo</MEMO>\n\t\t\t\t</STMTTRN>\n"
	 **************************************************************************/
	public function getOFXTransaction($timeStamp, $data) {
		try {
			return
				"\t\t\t\t<STMTTRN>\n".
				"\t\t\t\t\t<TRNTYPE>$data[Type]</TRNTYPE>\n".
				"\t\t\t\t\t<DTPOSTED>$timeStamp</DTPOSTED>\n".
				"\t\t\t\t\t<TRNAMT>$data[Amount]</TRNAMT>\n".
				"\t\t\t\t\t<FITID>$data[Id]</FITID>\n".
				"\t\t\t\t\t<CHECKNUM>$data[Id]</CHECKNUM>\n".
				"\t\t\t\t\t<NAME>$data[Payee]</NAME>\n".
				"\t\t\t\t\t<MEMO>$data[Memo]</MEMO>\n".
				"\t\t\t\t</STMTTRN>\n";
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Gets OFX format transaction account end content
	 *
	 * @return 	string the OFX content
	 *
	 * @assert (20120101111111) == "\t\t</BANKTRANLIST>\n\t\t<LEDGERBAL>\n\t\t\t<BALAMT>0</BALAMT>\n\t\t\t<DTASOF>20120101111111</DTASOF>\n\t\t</LEDGERBAL>\n\t</STMTRS>\n"
	 **************************************************************************/
	public function getOFXTransactionAccountEnd($timeStamp) {
		try {
			return
				"\t\t</BANKTRANLIST>\n".
				"\t\t<LEDGERBAL>\n".
				"\t\t\t<BALAMT>0</BALAMT>\n".
				"\t\t\t<DTASOF>$timeStamp</DTASOF>\n".
				"\t\t</LEDGERBAL>\n".
				"\t</STMTRS>\n";
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Gets OFX transfer footer
	 *
	 * @return 	string the OFX content
	 *
	 * @assert () == '</STMTTRNRS></BANKMSGSRSV1></OFX>'
	 **************************************************************************/
	public function getOFXTransactionFooter() {
		try {
			// need to make variables reference $this->
			return '</STMTTRNRS></BANKMSGSRSV1></OFX>';
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Gets OFX transfer header
	 *
	 * @param 	string $timeStamp	the time in mmddyy_hhmmss format
	 * @return 	string the OFX content
	 *
	 * @assert ('20120101_111111') == "<OFX>\n\t<SIGNONMSGSRSV1>\n\t\t<SONRS></SONRS>\n\t</SIGNONMSGSRSV1>\n\t<BANKMSGSRSV1><INTRATRNRS>\n\t\t<TRNUID>20120101_111111</TRNUID>\n\t\t<STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS>\n"
	 **************************************************************************/
	public function getOFXTransferHeader($timeStamp) {
		try {
			return
				"<OFX>\n".
				"\t<SIGNONMSGSRSV1>\n".
				"\t\t<SONRS></SONRS>\n".
				"\t</SIGNONMSGSRSV1>\n".
				"\t<BANKMSGSRSV1><INTRATRNRS>\n". // Begin response
				"\t\t<TRNUID>$timeStamp</TRNUID>\n".
				"\t\t<STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS>".
				"\n";
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Gets OFX transfer start
	 *
	 * @param 	string $accountType	the account types
	 * @return 	string the QIF content
	 *
	 * @assert ('USD', 20120101111111, 1, 'account', 'type', array('SplitAccountId' => 2, 'SplitAccount' => 'split_account', 'Amount' => 100)) == "\t<INTRARS>\n\t\t<CURDEF>USD</CURDEF>\n\t\t<SRVRTID>20120101111111</SRVRTID>\n\t\t<XFERINFO>\n\t\t\t<BANKACCTFROM>\n\t\t\t\t<BANKID>1</BANKID>\n\t\t\t\t<ACCTID>account</ACCTID>\n\t\t\t\t<ACCTTYPE>type</ACCTTYPE>\n\t\t\t</BANKACCTFROM>\n\t\t\t<BANKACCTTO>\n\t\t\t\t<BANKID>2</BANKID>\n\t\t\t\t<ACCTID>split_account</ACCTID>\n\t\t\t\t<ACCTTYPE>type</ACCTTYPE>\n\t\t\t</BANKACCTTO>\n\t\t\t<TRNAMT>100</TRNAMT>\n\t\t</XFERINFO>\n\t\t<DTPOSTED>20120101111111</DTPOSTED>\n\t</INTRARS>\n"
	 **************************************************************************/
	public function getOFXTransfer(
		$currency, $timeStamp, $accountId, $account, $accountType, $data
	) {
		try {
			return
				"\t<INTRARS>\n". // Begin transfer response
				"\t\t<CURDEF>$currency</CURDEF>\n".
				"\t\t<SRVRTID>$timeStamp</SRVRTID>\n".
				"\t\t<XFERINFO>\n". // Begin transfer aggregate
				"\t\t\t<BANKACCTFROM>\n".
				"\t\t\t\t<BANKID>$accountId</BANKID>\n".
				"\t\t\t\t<ACCTID>$account</ACCTID>\n".
				"\t\t\t\t<ACCTTYPE>$accountType</ACCTTYPE>\n".
				"\t\t\t</BANKACCTFROM>\n".
				"\t\t\t<BANKACCTTO>\n".
				"\t\t\t\t<BANKID>$data[SplitAccountId]</BANKID>\n".
				"\t\t\t\t<ACCTID>$data[SplitAccount]</ACCTID>\n".
				"\t\t\t\t<ACCTTYPE>$accountType</ACCTTYPE>\n".
				"\t\t\t</BANKACCTTO>\n".
				"\t\t\t<TRNAMT>$data[Amount]</TRNAMT>\n".
				"\t\t</XFERINFO>\n". // End transfer aggregate
				"\t\t<DTPOSTED>$timeStamp</DTPOSTED>\n".
				"\t</INTRARS>\n"; // End transfer response
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Gets OFX transfer footer
	 *
	 * @return 	string the OFX content
	 *
	 * @assert () == '</INTRATRNRS></BANKMSGSRSV1></OFX>'
	 **************************************************************************/
	public function getOFXTransferFooter() {
		try {
			// need to make variables reference $this->
			return '</INTRATRNRS></BANKMSGSRSV1></OFX>'; // End response
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->
} //<-- end class -->
