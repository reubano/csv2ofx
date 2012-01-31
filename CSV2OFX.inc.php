<?php
/*******************************************************************************
 * purpose: contains csv2ofx functions
 ******************************************************************************/

// include files
$thisProjectDir	= dirname(__FILE__);
require_once $thisProjectDir.'/lib_general/General.inc.php';

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
	
	/*************************************************************************** 
	 * The class constructor
	 *
	 * @param 	boolean $verbose	enable verbose comments
	 **************************************************************************/
	function __construct($source, $csvContent, $verbose = FALSE) {
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
				$this->headDesc 	= 'Description';
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

	/*************************************************************************** 
	 * Set amount values
	 *
	 * @param 	array 	$accountTypeList	list of possible account types
	 * @param 	string 	$defAccountType		default account type
	 **************************************************************************/
	public function setAmounts() {
		try {		
			foreach ($this->csvContent as $key => $content) {	
				$amount = $content[$this->headAmount];
				$amount = floatval(ereg_replace("[^-0-9\.]","",$amount));
				$this->csvContent[$key][$this->headAmount] = $amount;
			} //<-- end for loop -->				
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/*************************************************************************** 
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

	/*************************************************************************** 
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

	/*************************************************************************** 
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

	/*************************************************************************** 
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

	/*************************************************************************** 
	 * Organizes the splits of each transaction so that the main transaction is
	 * listed first
	 **************************************************************************/
	public function organizeSplits() {
		if (!($this->newContent)) {
			throw new Exception('$newContent not set! Run verifySplits() from '.
				$this->className.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {				
				foreach ($this->newContent as $id => $transaction) {
					$max = 0;
					$this->mainAccounts[$id] = 'none';
					
					foreach ($transaction as $key => $split) {
						$amount = $split[$this->headAmount];
						$absAmount = abs($amount);
						
						if ($absAmount > $max) {
							$this->mainAccounts[$id] = 
								$split[$this->headAccount];
							$mainKeys[$id] = $key;
							$max = $absAmount;
						} //<-- end if -->
					} //<-- end foreach -->
					
					if ($this->mainAccounts[$id] == 'none') {
						throw new Exception('Main account not found at '.
							'transaction '.$id.' from '.$this->className.'->'
							.__FUNCTION__.'() line '.__LINE__
						);
					}
				
					if ($mainKeys[$id] != 0) {		
						general::arrayMove($transaction, $mainKeys[$id]);
						$this->newContent[$id] = $transaction;
					} //<-- end if -->
				} //<-- end foreach -->

			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.$this->className.
					'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/*************************************************************************** 
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
					general::arraySortBySubValue($transaction, 'AccountName');
				}
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.$this->className.
					'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/*************************************************************************** 
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

	/*************************************************************************** 
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
	
	/*************************************************************************** 
	 * Verifies that the splits of each transaction sum to 0
	 *
	 * @return 	array	$this->newContent	csv content organized by transaction
	 **************************************************************************/
	public function verifySplits() {
		if (!($this->tranIds)) {
			throw new Exception('$tranIds not set! Run setTranIds() from '.
				$this->className.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				foreach ($this->tranIds as $id) {
					$sum = 0;
					
					foreach ($this->csvContent as $transaction) {
						if ($transaction[$this->headTranId] == $id) {
							$this->newContent[$id][] = $transaction;
							$amount = $transaction[$this->headAmount];
							$sum += $amount;
						} //<-- end if -->
					} //<-- end foreach -->
					
					if (round(abs($sum), 2) > 0) {
						throw new Exception('Invalid split of '.$sum.' at '.
							'transaction '.$id.' from '.$this->className.'->'.
							__FUNCTION__.'() line '.__LINE__
						);
					} //<-- end if -->
				} //<-- end foreach -->

				return $this->newContent;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.$this->className.
					'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->


	/*************************************************************************** 
	 * Sets QIF format transaction variables
	 *
	 * @param 	string 	$transaction	the account
	 * @param 	string 	$timestamp		the account types
	 * @return 	string	$content		the QIF content
	 **************************************************************************/
	public function setTransactionData($transaction, $timestamp) {
		try {
			$this->tranDate = date("m/d/y", $timestamp);
			$this->tranDate2 = date("Ymd", $timestamp); 
			$this->tranAmount = $transaction[$this->headAmount];
			
			if ($this->source != 'xero') {
				$this->tranType = $transaction[$this->headTranType];
				
				if ($this->tranType == 'debit') {
					$this->tranAmount = '-'.$this->tranAmount;
				}
			}
			
			$this->tranDesc = $transaction[$this->headDesc];
			$this->tranPayee = $transaction[$this->headPayee];
			$this->tranNotes = $transaction[$this->headNotes];
			$this->tranSplitAccount = $transaction[$this->headSplitAccount];
						
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

	/*************************************************************************** 
	 * Gets QIF format account content
	 *
	 * @param 	string 	$account		the account
	 * @param 	string 	$accountType	the account types
	 * @return 	string	$content		the QIF content
	 **************************************************************************/
	public function getQIFTransactionHeader($account, $accountType) {
		try {
			$content =
				"!Account\n".
				"N$account\n".
				"T$accountType\n".
				"^\n";
			
			return $content;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Gets QIF format transaction content
	 *
	 * @param 	string 	$accountType	the account types
	 * @return 	string	$content		the QIF content
	 **************************************************************************/
	public function getQIFTransactionContent($accountType) {
		try {			
			$content = "!Type:$accountType\n";
			
			if ($this->tranCheckNum) {
				$content .= "N$this->tranCheckNum\n";
			}

			$content .=
				"D$this->tranDate\n".
				"P$this->tranPayee\n";
			
			if ($this->split) {
				$content .= "T$this->tranAmount\n";
			} else {
				if (substr($this->tranAmount, 0, 1) == '-') {
					$tranAmount = substr($this->tranAmount, 1);
				} else {
					$tranAmount = '-'.$this->tranAmount;
				}
				
				$content .= "T$tranAmount\n";
			}
			
			return $content;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->					

	/*************************************************************************** 
	 * Gets QIF format split content
	 *
	 * @return 	string	$content		the QIF content
	 **************************************************************************/
	public function getQIFSplitContent() {
		try {			
			$content = "S$this->tranSplitAccount\n".
				"E$this->tranDesc\n".
				'$'."$this->tranAmount\n";			
			
			return $content;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Gets QIF transaction footer
	 *
	 * @return 	string	$content		the QIF content
	 **************************************************************************/
	public function getQIFTransactionFooter() {
		try {
			// need to make variables reference $this->					
			$content = "^\n";
			return $content;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->
	
	/*************************************************************************** 
	 * Gets OFX format transaction content
	 *
	 * @param 	string 	$timeStamp	the time in mmddyy_hhmmss format
	 * @return 	string	$content	the OFX content
	 **************************************************************************/
	public function getOFXTransactionHeader($timeStamp) {
		try {
			$content =
				"<OFX>\n".
				"\t<SIGNONMSGSRSV1>\n".
				"\t\t<SONRS>\n".
				"\t\t\t<STATUS>\n".
				"\t\t\t\t<CODE>0</CODE>\n".
				"\t\t\t\t<SEVERITY>INFO</SEVERITY>\n".
				"\t\t\t</STATUS>\n".
				"\t\t\t<DTSERVER>$today</DTSERVER>\n".
				"\t\t\t<LANGUAGE>$language</LANGUAGE>\n".
				"\t\t</SONRS>\n".
				"\t</SIGNONMSGSRSV1>\n".
				"\t<BANKMSGSRSV1><STMTTRNRS>\n".
				"\t\t<TRNUID>$timestamp</TRNUID>\n".
				"\t\t<STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS>".
				"\n";
			
			return $content;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Gets OFX format transaction account start content
	 *
	 * @return 	string	$content	the OFX content
	 **************************************************************************/
	public function getOFXTransactionAccountStart() {
		try {
			$content =
				"\t<STMTRS>\n".
				"\t\t<CURDEF>$currency</CURDEF>\n".
				"\t\t<BANKACCTFROM>\n".
				"\t\t\t<BANKID>$accountId</BANKID>\n".
				"\t\t\t<ACCTID>$account</ACCTID>\n".
				"\t\t\t<ACCTTYPE>$accountType</ACCTTYPE>\n".
				"\t\t</BANKACCTFROM>\n".
				"\t\t<BANKTRANLIST>\n".
				"\t\t\t<DTSTART>$today</DTSTART>\n".
				"\t\t\t<DTEND>$today</DTEND>\n";
			
			return $content;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Gets OFX format transaction content
	 *
	 * @return 	string	$content	the OFX content
	 **************************************************************************/
	public function getOFXTransaction() {
		try {
			$content =
				"\t\t\t\t<STMTTRN>\n".
				"\t\t\t\t\t<TRNTYPE>$defTranType</TRNTYPE>\n".
				"\t\t\t\t\t<DTPOSTED>$tranDate2</DTPOSTED>\n".
				"\t\t\t\t\t<TRNAMT>$tranAmount</TRNAMT>\n".
				"\t\t\t\t\t<FITID>$tranId</FITID>\n".
				"\t\t\t\t\t<CHECKNUM>$tranId</CHECKNUM>\n".
				"\t\t\t\t\t<NAME>$tranPayee</NAME>\n".
				"\t\t\t\t\t<MEMO>$tranMemo</MEMO>\n".
				"\t\t\t\t</STMTTRN>\n";

			return $content;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->
	
	/*************************************************************************** 
	 * Gets OFX format transaction account end content
	 *
	 * @return 	string	$content	the OFX content
	 **************************************************************************/
	public function getOFXTransactionAccountEnd() {
		try {
			$content =
				"\t\t</BANKTRANLIST>\n".
				"\t\t<LEDGERBAL>\n".
				"\t\t\t<BALAMT>0</BALAMT>\n".
				"\t\t\t<DTASOF>$today</DTASOF>\n".
				"\t\t</LEDGERBAL>\n".
				"\t</STMTRS>\n";
			
			return $content;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Gets OFX transfer footer
	 *
	 * @return 	string	$content		the OFX content
	 **************************************************************************/
	public function getOFXTransactionFooter() {
		try {
			// need to make variables reference $this->					
			$content = '</STMTTRNRS></BANKMSGSRSV1></OFX>';
			return $content;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->
	
	/*************************************************************************** 
	 * Gets OFX transfer header
	 *
	 * @param 	string 	$timeStamp	the time in mmddyy_hhmmss format
	 * @return 	string	$content	the OFX content
	 **************************************************************************/
	public function getOFXTransferHeader($timeStamp) {
		try {
			$content =
				"<OFX>\n".
				"\t<SIGNONMSGSRSV1>\n".
				"\t\t<SONRS></SONRS>\n".
				"\t</SIGNONMSGSRSV1>\n".
				"\t<BANKMSGSRSV1><INTRATRNRS>\n". // Begin response
				"\t\t<TRNUID>$timeStamp</TRNUID>\n".
				"\t\t<STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS>".
				"\n";
			
			return $content;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->
	
	/*************************************************************************** 
	 * Gets OFX transfer start
	 *
	 * @param 	string 	$accountType	the account types
	 * @return 	string	$content		the QIF content
	 **************************************************************************/
	public function getOFXTransfer($accountType) {
		try {
			// need to make variables reference $this->					
			$content =
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
				"\t\t\t\t<ACCTTYPE>$defAccountType</ACCTTYPE>\n".
				"\t\t\t</BANKACCTTO>\n".
				"\t\t\t<TRNAMT>$tranAmount</TRNAMT>\n".
				"\t\t</XFERINFO>\n". // End transfer aggregate
				"\t\t<DTPOSTED>$tranDate2</DTPOSTED>\n".
				"\t</INTRARS>\n"; // End transfer response
			
			return $content;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Gets OFX transfer footer
	 *
	 * @return 	string	$content		the OFX content
	 **************************************************************************/
	public function getOFXTransferFooter() {
		try {
			// need to make variables reference $this->					
			$content = '</INTRATRNRS></BANKMSGSRSV1></OFX>'; // End response
			return $content;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->
} //<-- end class -->