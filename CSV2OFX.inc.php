<?php
/*******************************************************************************
 * purpose: contains csv2ofx functions
 ******************************************************************************/

// include files
$thisProjectDir	= dirname(__FILE__);
require_once $thisProjectDir.'/lib_general/MyArray.php';

//<-- begin class -->
class CSV2OFX {
	protected $className = __CLASS__;	// class name
	protected $verbose;
	protected $source;
	public $split;
	public $newContent;
	public $accounts = array();
	public $mainAccounts;
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
	public $headTranId;
	public $headCheckNum;
	public $tranCheckNum;
	public $tranType;
	public $tranNotes;
	public $tranId;
	public $tranIds = array();
	public $tranDate;
	public $tranDate2;
	public $tranPayee;
	public $tranClass;
	public $tranSplitAccount;
	public $tranSplitAccountId;
	public $tranAmount;
	public $tranDesc;
	public $defSplitAccount = 'Orphan';

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
				$this->headTranId 	= 'JournalNumber';
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
				$this->headTranId 	= 'Transaction Id';
				$this->split		= FALSE;
				break;

			case 'exim':
				$this->headAccount	= 'Account';
				$this->headDate 	= 'Date';
				$this->headAmount 	= 'Amount';
				$this->headPayee 	= 'Narration';
				$this->headTranId 	= 'Reference Number';
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
				$this->headTranId 	= 'Row';
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
				$this->headTranId 	= 'Field';
				$this->headCheckNum = 'Field';
				$this->split		= FALSE;
			} //<-- end switch -->

		if ($this->verbose) {
			fwrite(STDOUT, "$this->className class constructor set.\n");
		} //<-- end if -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Set amount values
	 *
	 * @param 	array 	$accountTypeList	list of possible account types
	 * @param 	string 	$defAccountType		default account type
	 **************************************************************************/
	public function setAmounts() {
		try {
			foreach ($this->csvContent as $key => $content) {
				$amount = $content[$this->headAmount];
				$amount = floatval(preg_replace("[^-0-9\.]","", $amount));
				$this->csvContent[$key][$this->headAmount] = $amount;
			} //<-- end for loop -->
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Set account names and types
	 *
	 * @param 	array 	$accountTypeList	list of possible account types
	 * @param 	string 	$defAccountType		default account type
	 **************************************************************************/
	public function getAccounts($accountTypeList, $defAccountType) {
		try {
			if ($this->split) {
				$this->accounts = array_unique($this->mainAccounts);
			} else {
				foreach ($this->newContent as $content) {
					$this->accounts[] = $content[0][$this->headAccount];
				} //<-- end for loop -->

				$this->accounts = array_unique($this->accounts);
			}

			sort($this->accounts);

			$accountTypes = self::_getAccountTypes(
				$accountTypeList, $defAccountType
			);

			$this->accounts = array_combine($this->accounts, $accountTypes);
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Detects account types from account list
	 *
	 * @param 	array 	$accountTypeList	list of possible account types
	 * @param 	string 	$defAccountType		default account type
	 * @return 	array	$accountTypes		the resulting account types
	 * @throws 	Exception if $tags is empty
	 **************************************************************************/
	private function _getAccountTypes($accountTypeList, $defAccountType) {
			try {
			$accountTypes = array();

			foreach ($this->accounts as $account) {
				foreach ($accountTypeList as $accountType => $searchList) {
					foreach ($searchList as $searchTerm) {
						$found = stripos($account, $searchTerm);

						if ($found !== false) {
						 	$accountTypes[] = $accountType;
						 	// stop searching and move to next account
						 	continue 3;
						} //<-- end if -->
					} //<-- end for loop through search terms -->
				} //<-- end for loop through account types -->

				// if no matches found, apply default account type
				$accountTypes[] = $defAccountType;
			} //<-- end for loop through accounts -->

			return $accountTypes;
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.
				'->'.__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Gets transaction IDs
	 *
	 * @return 	array	$this->tranIds		the transaction IDs
	 **************************************************************************/
	public function setTranIds() {
		try {
			foreach ($this->csvContent as $content) {
				$this->tranIds[] = $content[$this->headTranId];
			} //<-- end for loop -->

			$this->tranIds = array_unique($this->tranIds);
			sort($this->tranIds);

			return $this->tranIds;
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Combines similiar splits from the same account
	 *
	 * @param 	array 	$collapse			accounts to collapse
	 **************************************************************************/
	public function collapseSplits($collapse) {
		if (!($this->newContent)) {
			throw new Exception('$newContent not set! Run verifySplits() from '.
				$this->className.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				foreach ($this->newContent as $id => $transaction) {
					$previousAccount = '';
					$previousAmount = 0;
					$splice = array();

					// loop over splits (by reference bc we are changing $split
					// in place)
					foreach ($transaction as $key => &$split) {
						if (in_array($split[$this->headAccount], $collapse)
							&& $split[$this->headAccount] == $previousAccount
						) {
							$split[$this->headAmount] += $previousAmount;
							$splice[] = $key - 1;
						} //<-- end if -->

						$previousAccount = $split[$this->headAccount];
						$previousAmount = $split[$this->headAmount];
					} //<-- end loop through splits -->

					foreach ($splice as $i => $key) {
						array_splice($transaction, $key - $i, 1);
					}

					$this->newContent[$id] = $transaction;
				} //<-- end loop through transactions -->

				self::_verifySplits();
			} catch (Exception $e) {
				throw new Exception($e->getMessage().' from '.$this->className.
					'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->




	/**
	 ***************************************************************************
	 * Sorts splits by a given field
	 *
	 * @param 	array 	$field	field to sort splits by
	 **************************************************************************/
	public function sortSplits($field) {
		if (!($this->newContent)) {
			throw new Exception('$newContent not set! Run verifySplits() from '.
				$this->className.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				foreach ($this->newContent as $id => &$transaction) {
					$transaction = myarray::arraySortBySubValue(
						$transaction, 'AccountName'
					);
				}
			} catch (Exception $e) {
				throw new Exception($e->getMessage().' from '.$this->className.
					'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Verifies that the splits of each transaction sum to 0
	 *
	 * @return 	array	$this->newContent	csv content organized by transaction
	 **************************************************************************/
	private function _verifySplits() {
		try {
			foreach ($this->newContent as $id => $transaction) {
				$sum = 0;

				foreach ($transaction as $split) {
					$amount = $split[$this->headAmount];
					$sum += $amount;
				} //<-- end foreach -->

				if (round(abs($sum), 2) > 0) {
					throw new Exception('Invalid split of '.$sum.' at '.
						'transaction '.$id.' from '.$this->className.'->'.
						__FUNCTION__.'() line '.__LINE__
					);
				} //<-- end if -->
			} //<-- end foreach -->

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
	 * @return 	array	$this->newContent	csv content organized by transaction
	 **************************************************************************/
	public function makeSplits() {
		try {
			foreach ($this->csvContent as $key => $transaction) {
					$this->newContent[$key][] = $transaction;
			} //<-- end foreach -->

			return $this->newContent;
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.
				'->'.__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************


	/**
	 ***************************************************************************
	 * Sets QIF format transaction variables
	 *
	 * @param 	string 	$transaction	the account
	 * @param 	string 	$timestamp		the account types
	 * @return 	string	$content		the QIF content
	 **************************************************************************/
	public function setTransactionData($transaction, $timestamp) {
		try {
			$this->tranDate = date("m/d/Y", $timestamp);
			$this->dateStamp = date("Ymd", $timestamp);
			$this->tranAmount = $transaction[$this->headAmount];

			if ($this->headTranType) {
				$this->tranType = $transaction[$this->headTranType];

				if ($this->tranType == 'debit') {
					$this->tranAmount = '-'.$this->tranAmount;
				}
			}

			if ($this->headPayee) {
				$this->tranPayee = $transaction[$this->headPayee];
			} else {
				$this->tranPayee = '';
			}

			if ($this->headSplitAccount) {
				$this->tranSplitAccount = $transaction[$this->headSplitAccount];
			} else {
				$this->tranSplitAccount = $this->defSplitAccount;
			}

			if ($this->headDesc) {
				$this->tranDesc = $transaction[$this->headDesc];
			}

			if ($this->headNotes) {
				$this->tranNotes = $transaction[$this->headNotes];
			}

			if ($this->headClass) {
				$this->tranClass = $transaction[$this->headClass];
			}

			if ($this->headTranId) {
				$this->tranId = $transaction[$this->headTranId];
			}

			if ($this->headCheckNum) {
				$this->tranCheckNum = $transaction[$this->headCheckNum];
			}

			if ($this->headCheckNum) {
				$this->tranCheckNum = $transaction[$this->headCheckNum];
			}

			// if no id, create it using check number or md5
			// hash of the transaction details
			if (!$this->tranId) {
				if ($this->tranCheckNum) {
					$this->tranId = $this->tranCheckNum;
				} else {
					$hashCombo = $this->tranDate.$this->tranAmount.
						$this->tranPayee.$this->tranSplitAccount.
						$this->tranDesc;
					$this->tranId = md5($hashCombo);
				} //<-- end if -->
			} //<-- end if -->

			// create category id using an md5 hash of the category
			if ($this->tranSplitAccount) {
				$this->tranSplitAccountId = md5($this->tranSplitAccount);
			}

			if ($this->tranNotes) {
				$this->tranDesc = $this->tranDesc.'/'.$this->tranNotes;
			}

			if ($this->tranClass) {
				$this->tranDesc = $this->tranDesc.'/'.$this->tranClass;
			}
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
	 * @return 	string	$content		the QIF content
	 *
	 * @assert ('account', 'type') == "!Account\nN$account\nT$type\n^\n"
	 **************************************************************************/
	public function getQIFTransactionHeader($account, $accountType) {
		try {
			return
				"!Account\n".
				"N$account\n".
				"T$accountType\n".
				"^\n";
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
	 * @assert ('type', '01/01/12', 'payee', 100, 1) == "!Type:type\nN1\nD01/01/12\nPpayee\nT100\n"
	 * @assert ('type', '01/01/12', 'payee', 100) == "!Type:type\nD01/01/12\nPpayee\nT100\n"
	 **************************************************************************/
	public function getQIFTransactionContent(
		$accountType, $tranDate, $tranPayee, $tranAmount, $tranCheckNum=null
	) {
		try {
			$content = "!Type:$accountType\n";

			if ($tranCheckNum) {
				$content .= "N$tranCheckNum\n";
			}

			$content .=
				"D$tranDate\n".
				"P$tranPayee\n";

			if ($this->source == 'xero') {
				// switch signs
				if (substr($tranAmount, 0, 1) == '-') {
					$tranAmount = substr($tranAmount, 1);
				} else {
					$tranAmount = '-'.$tranAmount;
				}
			}

			$content .= "T$tranAmount\n";

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
	 * @assert ('account', 'desc', 100) == "Saccount\nEdesc\n$100\n"
	 **************************************************************************/
	public function getQIFSplitContent(
		$tranSplitAccount, $tranDesc, $tranAmount
	) {
		try {
			return "S$tranSplitAccount\n".
				"E$tranDesc\n".
				'$'."$tranAmount\n";
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
			// need to make variables reference $this->
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
	 * @assert (20120101111111, 'ENG') == "<OFX>\n\t<SIGNONMSGSRSV1>\n\t\t<SONRS>\n\t\t\t<STATUS>\n\t\t\t\t<CODE>0</CODE>\n\t\t\t\t<SEVERITY>INFO</SEVERITY>\n\t\t\t</STATUS>\n\t\t\t<DTSERVER>20120101111111</DTSERVER>\n\t\t\t<LANGUAGE>ENG</LANGUAGE>\n\t\t</SONRS>\n\t</SIGNONMSGSRSV1>\n\t<BANKMSGSRSV1><STMTTRNRS>\n\t\t<TRNUID>20120101111111</TRNUID>\n\t\t<STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS>\n"
	 **************************************************************************/
	public function getOFXTransactionHeader($timeStamp, $language) {
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
	 * @assert ('type', 20120101111111, 100, 1, 'payee', 'memo') == "\t\t\t\t<STMTTRN>\n\t\t\t\t\t<TRNTYPE>type</TRNTYPE>\n\t\t\t\t\t<DTPOSTED>20120101111111</DTPOSTED>\n\t\t\t\t\t<TRNAMT>100</TRNAMT>\n\t\t\t\t\t<FITID>1</FITID>\n\t\t\t\t\t<CHECKNUM>1</CHECKNUM>\n\t\t\t\t\t<NAME>payee</NAME>\n\t\t\t\t\t<MEMO>memo</MEMO>\n\t\t\t\t</STMTTRN>\n"
	 **************************************************************************/
	public function getOFXTransaction(
		$tranType, $timeStamp, $tranAmount, $tranId, $tranPayee, $tranMemo
	) {
		try {
			return
				"\t\t\t\t<STMTTRN>\n".
				"\t\t\t\t\t<TRNTYPE>$tranType</TRNTYPE>\n".
				"\t\t\t\t\t<DTPOSTED>$timeStamp</DTPOSTED>\n".
				"\t\t\t\t\t<TRNAMT>$tranAmount</TRNAMT>\n".
				"\t\t\t\t\t<FITID>$tranId</FITID>\n".
				"\t\t\t\t\t<CHECKNUM>$tranId</CHECKNUM>\n".
				"\t\t\t\t\t<NAME>$tranPayee</NAME>\n".
				"\t\t\t\t\t<MEMO>$tranMemo</MEMO>\n".
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
	 * @assert ('USD', 20120101111111, 1, 'account', 'type', 2, 'split_account', 'def_type', 100) == "\t<INTRARS>\n\t\t<CURDEF>USD</CURDEF>\n\t\t<SRVRTID>20120101111111</SRVRTID>\n\t\t<XFERINFO>\n\t\t\t<BANKACCTFROM>\n\t\t\t\t<BANKID>1</BANKID>\n\t\t\t\t<ACCTID>account</ACCTID>\n\t\t\t\t<ACCTTYPE>type</ACCTTYPE>\n\t\t\t</BANKACCTFROM>\n\t\t\t<BANKACCTTO>\n\t\t\t\t<BANKID>2</BANKID>\n\t\t\t\t<ACCTID>split_account</ACCTID>\n\t\t\t\t<ACCTTYPE>'def_type'</ACCTTYPE>\n\t\t\t</BANKACCTTO>\n\t\t\t<TRNAMT>100</TRNAMT>\n\t\t</XFERINFO>\n\t\t<DTPOSTED>20120101111111</DTPOSTED>\n\t</INTRARS>\n"
	 **************************************************************************/
	public function getOFXTransfer(
		$currency, $timeStamp, $accountId, $account, $accountType,
		$tranSplitAccountId, $tranSplitAccount, $tranAccountType, $tranAmount
	) {
		try {
			return
				"\t<INTRARS>\n". // Begin transfer response
				"\t\t<CURDEF>$currency</CURDEF>\n".
				"\t\t<SRVRTID>$timestamp</SRVRTID>\n".
				"\t\t<XFERINFO>\n". // Begin transfer aggregate
				"\t\t\t<BANKACCTFROM>\n".
				"\t\t\t\t<BANKID>$accountId</BANKID>\n".
				"\t\t\t\t<ACCTID>$account</ACCTID>\n".
				"\t\t\t\t<ACCTTYPE>$accountType</ACCTTYPE>\n".
				"\t\t\t</BANKACCTFROM>\n".
				"\t\t\t<BANKACCTTO>\n".
				"\t\t\t\t<BANKID>$tranSplitAccountId</BANKID>\n".
				"\t\t\t\t<ACCTID>$tranSplitAccount</ACCTID>\n".
				"\t\t\t\t<ACCTTYPE>$tranAccountType</ACCTTYPE>\n".
				"\t\t\t</BANKACCTTO>\n".
				"\t\t\t<TRNAMT>$tranAmount</TRNAMT>\n".
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
