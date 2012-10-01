#!/usr/bin/env php
<?php
/**
 *******************************************************************************
 * csv2ofx converts a csv file to ofx and qif
 *******************************************************************************
 */
 
date_default_timezone_set('Africa/Nairobi');

if (strpos('@php_bin@', '@php_bin') === 0) { // not a pear install
	define('PROJECT_DIR', dirname(__FILE__).DIRECTORY_SEPARATOR);
} else {
	define('PROJECT_DIR', '@php_bin@'.DIRECTORY_SEPARATOR);
}

define('PROG_DIR', 'csv2ofx'.DIRECTORY_SEPARATOR);
define('CUR_DIR', getcwd().DIRECTORY_SEPARATOR);
define('TODAY', date("Ymd")); // format to yyyymmdd
define('TIME_STAMP', date("Ymd_His"); // format to yyyymmdd_hhmmss
define('XML_FILE', PROJECT_DIR.'csv2ofx.xml');

require PROJECT_DIR.PROG_DIR.'Autoload.php';

$accountList = array('ofx' => 'CHECKING', 'qif' => 'Bank');
$ofxList = array(
	'CHECKING' => array('checking'), 
	'SAVINGS' => array('savings'), 
	'MONEYMRKT' => array('market'),
	'CREDITLINE' => array('visa', 'master', 'express', 'discover')
);

$bankList = array(
	'checking', 'savings', 'market', 'receivable', 'payable', 'visa', 'master',
	'express', 'discover'
);

$qifList = array('Bank' => $bankList, 'Cash' => array('cash'));
$accountTypeList = array('ofx' => $ofxList, 'qif' => $qifList);

$ext = array('ofx' => 'ofx', 'qif' => 'qif');


// create the parser from xml file
$parser = Console_CommandLine::fromXmlFile(XML_FILE);

try {
	// run the parser
	$result = $parser->parse();
	
	// command arguments
	$source = $result->args['source'];
	$dest = $result->args['dest'];
	
	// program setting
	$vars = new vars($result->options['verbose']);
	$file = new file($result->options['verbose']);
	$array = new myarray($result->options['verbose']);
	$string = new string($result->options['verbose']);
	$program = $file->getBase(__FILE__);

	// load options if present
	$delimiter = $result->options['delimiter'];
	$mapping = $result->options['mapping'];
	$primary = $result->options['primary'];	
	$startDate = strtotime($result->options['start']);
	$endDate = strtotime($result->options['end']);
	$collAccts = explode(',', $result->options['collapse']);
	$currency = $result->options['currency'];
	$language = $result->options['language'];

	if ($result->options['qif']) {
		$type = 'qif';
	} else {
		$type = 'ofx';
	}
	
	$accountType = $result->options['accountType'];
	$accountTypeList = $accountTypeList[$type];
	$ext = $ext[$type];

	switch ($dest){
		case '$':
			$stdout = TRUE;
			break;
			
		case '':
			$stdout = FALSE;
			$destFile = CUR_DIR.TIME_STAMP.'_'.$mapping.'.'.$ext;
			print("$destFile\n");
			exit;
			break;
			
		default:
			$stdout = FALSE;
			$destFile = $dest;
	} //<-- end switch -->		
	
	if ($result->options['debug']) {
		print('[Command opts] ');
		print_r($result->options);
		print('[Command args] ');
		print_r($result->args);
		exit(0);
	} //<-- end if -->

	// execute program
	if (file_exists($source)) {
		$content = $file->file2String($source);
		$content = $string->makeLFLineEndings($content, $delimiter);
	} else {
		$content = $source;
	} //<-- end if -->
	
	$content = $string->lines2Array($content);
	$csvContent = $string->csv2Array($content, $delimiter);
	$csvContent = $array->arrayTrim($csvContent, $delimiter);
	$csvContent = $array->arrayLengthen($csvContent, $delimiter);
	$csvContent = $array->arrayInsertKey($csvContent);
	array_shift($csvContent);
	
	$csv2ofx = new csv2ofx($mapping, $csvContent, $result->options['verbose']);
	$csv2ofx->setAmounts();

	if ($csv2ofx->split) {
		$csv2ofx->setTranIds();
		$csv2ofx->verifySplits();
		$csv2ofx->sortSplits($csv2ofx->headAccount);
		$csv2ofx->collapseSplits($collAccts);
		$csv2ofx->organizeSplits();
	} else { // not a split transaction
		$csv2ofx->makeSplits();
	} //<-- end if split -->
	
	$csv2ofx->getAccounts($accountTypeList, $accountType[$type]);
		
	// variable mode setting
	if ($result->options['variables']) {
		print_r($vars->getVars(get_defined_vars()));
		exit(0);
	}

	if ($result->options['qif']) {
		$content = '';
		
		foreach ($csv2ofx->accounts as $account => $accountType) {
			$content .= 
				$csv2ofx->getQIFTransactionHeader($account, $accountType);
			
			// loop through each transaction
			foreach ($csv2ofx->newContent as $transaction) {
				// find the rows matching the account name 
				if ($transaction[0][$csv2ofx->headAccount] == $account) {
					if (!$csv2ofx->split) {
						if ($csv2ofx->headSplitAccount) {
							$tranSplitAccount = 
								$transaction[0][$csv2ofx->headSplitAccount];
						} else {
							$tranSplitAccount = $csv2ofx->defSplitAccount;
						}
						
						// if this is a transfer from the primary account, 
						// skip it and go to the next transaction
						if ($tranSplitAccount == $primary) {
							continue;
						}
					} //<-- end if not split -->
			
					TIME_STAMP = 
						strtotime($transaction[0][$csv2ofx->headDate]);
					
					// if transaction is not in the specified date range, 
					// go to the next one
					if (TIME_STAMP <= $startDate || TIME_STAMP >= $endDate) { 
						continue;
					}
	
					// get data for first split
					$csv2ofx->setTransactionData($transaction[0], TIME_STAMP);
					
					$content .= 
						$csv2ofx->getQIFTransactionContent($accountType);
					
					if ($csv2ofx->split) {
						// loop through each additional split
						foreach ($transaction as $key => $split) {
							if ($key > 0) {
								$csv2ofx->setTransactionData($split, 
									TIME_STAMP
								);
								
								$content .= $csv2ofx->getQIFSplitContent();
							} //<-- end if -->
						} //<-- end loop through splits -->
					} else { // not a split transaction
						$content .= $csv2ofx->getQIFSplitContent();
					} //<-- end if split -->
					
					$content .= $csv2ofx->getQIFTransactionFooter();
				} //<-- end if correct account -->
			} //<-- end loop through transactions -->
		} //<-- end loop through accounts -->	
	} else { // it's ofx
		// remove non xml compliant characters
		$csvContent = $array->xmlize($csvContent);
		
		if ($result->options['transfer']) {
			$content = $csv2ofx->getOFXTransferHeader(TIME_STAMP);
		} else { // it's a transaction
			$content = $csv2ofx->getOFXTransactionHeader(TIME_STAMP);
		} //<-- end if transfer -->

		// loop through each account
		foreach ($csv2ofx->accounts as $account => $accountType) {
			// create account id using an md5 hash of the account name
			$accountId = md5($account);
			
			if (!$result->options['transfer']) {
				$content .= $csv2ofx->getOFXTransactionAccountStart();
			} //<-- end if not transfer -->
			
			// find the rows matching the account name and loop 
			// through each transaction
			foreach ($csvContent as $transaction) {
				if ($transaction[$csv2ofx->headAccount] == $account) {
					// if this is a transfer from the primary account, 
					// skip it and go to the next transaction
					$tranSplitAccount = 
						$transaction[$csv2ofx->headSplitAccount];
					
					if ($tranSplitAccount == $primary) {
						continue;
					}
					
					// else, business as usual
					TIME_STAMP = strtotime($transaction[$csv2ofx->headDate]);
					
					// if transaction is not in the specified date range, 
					// go to the next one
					if (TIME_STAMP <= $startDate || TIME_STAMP >= $endDate) { 
						continue;
					}

					$csv2ofx->setTransactionData($transaction, TIME_STAMP);
					
					if ($result->options['transfer']) {
						$content .= 
							$csv2ofx->getOFXTransfer($account, $accountType);
					} else { // it's a transaction
						$content .= $csv2ofx->getOFXTransaction();
					} //<-- end if transfer -->
				} //<-- end if -->
			} //<-- end for loop through transactions -->
			
			if (!$result->options['transfer']) {
				$content .= $csv2ofx->getOFXTransactionAccountEnd();
			} //<-- end if not transfer -->
		} //<-- end foreach loop through accounts -->
		
		if ($result->options['transfer']) {
			$content .=$csv2ofx->getOFXTransferFooter();
		} else { // it's a transaction
			$content .=	$csv2ofx->getOFXTransactionFooter();
		} //<-- end if transfer -->
	} //<-- end if qif -->

	if ($stdout) {
		print($content);
	} else {
		$file->write2file($content, $destFile, $result->options['overwrite']);
	} //<-- end if not test mode -->

	exit(0);
} catch (Exception $e) {
	fwrite(STDOUT, 'Program '.$program.': '.$e->getMessage()."\n");
	exit(1);
}
?>