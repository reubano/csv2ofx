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
	 * @assert (array(array(array('Account Name' => 'account1'), array('Account Name' => 'account2')), array(array('Account Name' => 'account3'), array('Account Name' => 'account4')))) == array('account1', 'account3')
	 **************************************************************************/
	public function getAccounts($splitContent, $findAmounts=null) {
		try {
			$account = $this->headAccount;
			$amount = $this->headAmount;

			$byCurrent = function ($transaction) use ($account) {
				$split = current($transaction);
				return $split[$account];
			}; //<-- end for loop -->

			$filter = function ($split) use ($amount) {
				return ($split[$amount] == $findAmount);
			};

			$byAmount = function ($transaction, $findAmount) use (
				$account, $filter
			) {
				return array_filter($transaction, $filter);
			}; //<-- end for loop -->

			$splitContent = $findAmounts
				? array_map($byAmount, $splitContent, findAmounts)
				: $splitContent;

			return array_map($byCurrent, $splitContent);

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
	 * @assert (array('cash', 'checking', 'unsavings'), array('Bank' => array('checking', 'savings'), 'Cash' => array('cash'))) == array('Cash', 'Bank', 'n/a')
	 **************************************************************************/
	public function getAccountTypes($accounts, $typeList, $defType='n/a') {
		try {
			$search = function ($list, $type, $account) use (&$match) {
				$match = in_array($account, $list) ? $type : $match;
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
	 * Combines splits with the same account
	 *
	 * @param array $content return value of makeSplits();
	 * @param array $collapse accounts to collapse
	 *
	 * @return array $content collapsed content;
	 *
	 * @assert (array(array(array('Account Name' => 'account1', 'Amount' => 200), array('Account Name' => 'account1', 'Amount' => 200), array('Account Name' => 'account1', 'Amount' => 200))), array('account1')) == array(array(array('Account Name' => 'account1', 'Amount' => 600)))
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

// 			$reduce = function ($i, $key) use (&$transaction) {
// 				array_splice($transaction, $key - $i, 1);
// 			};

			$main = function (&$transaction) use ($sum) {
				$previous = array('act' => null, 'amt' => 0);
				array_walk($transaction, $sum, $previous);
			};

			array_walk($content, $main);
			$splice = $splice; // closure below doesn't work without this

			$reduce = function (&$transaction) use ($splice) {
				foreach ($splice as $key => $i) {
					array_splice($transaction, $key - $i, 1);
				};
			};

			array_walk($content, $reduce);

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
	 * @assert (array(array(array('Amount' => 100), array('Amount' => -100)), array('Amount' => -300), array('Amount' => 200), array('Amount' => 100))) == true
	 **************************************************************************/
	private function verifySplits($splitContent) {
		try {
			$headAmount = $this->headAmount;

			$sum = function ($a, $b) {
				return round(sum($a[$headAmount], $b[$headAmount]), 2);
			};

			$verify = function ($transaction) use ($sum) {
				return array_reduce($transaction, $sum);
			};

			$result = array_filter($splitContent, $verify);

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
	 * @assert (array('Transaction Type' => 'debit', 'Amount' => 1000.00, 'Description' => 'payee', 'Original Description' => 'description', 'Notes' => 'notes', 'Date' => '06/12/10', 'Category' => 'Checking', 'Account Name' => 'account'), 20120610111111) == array('amount' => '-1000', 'payee' => 'payee', 'desc' => 'description notes', 'id' => '370141bf77924d568817f7864c56419a', 'checkNum' => null, 'type' => 'debit', 'splitAccount' => 'Checking', 'splitAccountId' => '195917574edc9b6bbeb5be9785b6a479')
	 **************************************************************************/
	public function getTransactionData(
		$tr, $timeStamp, $defSplitAccount='Orphan'
	) {
		try {
			$type = $tr[$this->headTranType];
			$amount = $tr[$this->headAmount];
			$amount = ($type == 'debit') ? '-'.$amount : $amount;
			$payee = isset($this->headPayee) ? $tr[$this->headPayee] : '';
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
			$desc .= $notes ? ' '.$notes : '';
			$desc .= $class ? ' '.$class : '';

			// if no id, create it using check number or md5
			// hash of the transaction details
			$id = $id ?: $checkNum;
			$id = $id ?: md5($timeStamp.$amount.$payee.$splitAccount.$desc);

			return array(
				'amount' => $amount, 'payee' => $payee, 'desc' => $desc,
				'id' => $id, 'checkNum' => $checkNum, 'type' => $type,
				'splitAccount' => $splitAccount,
				'splitAccountId' => $splitAccountId
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
	 * @return 	string	$content		the QIF content
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
	 * @assert ('type', array('payee' => 'payee', 'amount' => 100, 'checkNum' => 1, 'date' => '01/01/12')) == "!Type:type\nN1\nD01/01/12\nPpayee\nT100\n"
	 * @assert ('type', array('payee' => 'payee', 'amount' => 100, 'date' => '01/01/12')) == "!Type:type\nD01/01/12\nPpayee\nT100\n"
	 **************************************************************************/
	public function getQIFTransactionContent($accountType, $data) {
		try {
			// switch signs if source is xero
			$amount = $data['amount'];
			$newAmount = (substr($amount, 0, 1) == '-')
				? substr($amount, 1)
				: '-'.$amount;

			$amount = ($this->source == 'xero') ? $newAmount : $amount;
			$content = "!Type:$accountType\n";
			$content .= isset($data['checkNum']) ? "N$data[checkNum]\n" : '';
			$content .= "D$data[date]\nP$data[payee]\nT$amount\n";
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
	 * @assert ('account', array('desc' => 'desc', 'amount' => 100)) == "Saccount\nEdesc\n$100\n"
	 **************************************************************************/
	public function getQIFSplitContent($splitAccount, $data) {
		try {
			return "S$splitAccount\nE$data[desc]\n\$$data[amount]\n";
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
	 * @assert (20120101111111, array('type' => 'type', 'amount' => 100, 'id' => 1, 'payee' => 'payee', 'memo' => 'memo')) == "\t\t\t\t<STMTTRN>\n\t\t\t\t\t<TRNTYPE>type</TRNTYPE>\n\t\t\t\t\t<DTPOSTED>20120101111111</DTPOSTED>\n\t\t\t\t\t<TRNAMT>100</TRNAMT>\n\t\t\t\t\t<FITID>1</FITID>\n\t\t\t\t\t<CHECKNUM>1</CHECKNUM>\n\t\t\t\t\t<NAME>payee</NAME>\n\t\t\t\t\t<MEMO>memo</MEMO>\n\t\t\t\t</STMTTRN>\n"
	 **************************************************************************/
	public function getOFXTransaction($timeStamp, $data) {
		try {
			return
				"\t\t\t\t<STMTTRN>\n".
				"\t\t\t\t\t<TRNTYPE>$data[type]</TRNTYPE>\n".
				"\t\t\t\t\t<DTPOSTED>$timeStamp</DTPOSTED>\n".
				"\t\t\t\t\t<TRNAMT>$data[amount]</TRNAMT>\n".
				"\t\t\t\t\t<FITID>$data[id]</FITID>\n".
				"\t\t\t\t\t<CHECKNUM>$data[id]</CHECKNUM>\n".
				"\t\t\t\t\t<NAME>$data[payee]</NAME>\n".
				"\t\t\t\t\t<MEMO>$data[memo]</MEMO>\n".
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
	 * @assert ('USD', 20120101111111, 1, 'account', 'type', array('splitAccountId' => 2, 'splitAccount' => 'split_account', 'amount' => 100)) == "\t<INTRARS>\n\t\t<CURDEF>USD</CURDEF>\n\t\t<SRVRTID>20120101111111</SRVRTID>\n\t\t<XFERINFO>\n\t\t\t<BANKACCTFROM>\n\t\t\t\t<BANKID>1</BANKID>\n\t\t\t\t<ACCTID>account</ACCTID>\n\t\t\t\t<ACCTTYPE>type</ACCTTYPE>\n\t\t\t</BANKACCTFROM>\n\t\t\t<BANKACCTTO>\n\t\t\t\t<BANKID>2</BANKID>\n\t\t\t\t<ACCTID>split_account</ACCTID>\n\t\t\t\t<ACCTTYPE>type</ACCTTYPE>\n\t\t\t</BANKACCTTO>\n\t\t\t<TRNAMT>100</TRNAMT>\n\t\t</XFERINFO>\n\t\t<DTPOSTED>20120101111111</DTPOSTED>\n\t</INTRARS>\n"
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
				"\t\t\t\t<BANKID>$data[splitAccountId]</BANKID>\n".
				"\t\t\t\t<ACCTID>$data[splitAccount]</ACCTID>\n".
				"\t\t\t\t<ACCTTYPE>$accountType</ACCTTYPE>\n".
				"\t\t\t</BANKACCTTO>\n".
				"\t\t\t<TRNAMT>$data[amount]</TRNAMT>\n".
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
