#!/usr/bin/env php
<?php
/**
 *******************************************************************************
 * csv2ofx converts a csv file to ofx and qif
 *******************************************************************************
 */
 
date_default_timezone_set('Africa/Nairobi');

$thisProjectDir		= dirname(__FILE__);
$projectsDir		= dirname($thisProjectDir);
$stdin				= FALSE;
$stdout				= FALSE;
$today				= date("Ymd"); // format to yyyymmdd
$timeStamp			= date("Ymd_His"); // format to yyyymmdd_hhmmss
$qifAccountTypeList = array(
	'Bank' => array('checking', 'savings', 'market', 'receivable', 'payable', 
		'visa', 'master', 'express', 'discover'),
	'Cash' => array('cash'),
);

$ofxAccountTypeList	= array(
	'CHECKING' => array('checking'), 
	'SAVINGS' => array('savings'), 
	'MONEYMRKT' => array('market'),
	'CREDITLINE' => array('visa', 'master', 'express', 'discover'),
);

$collAccts			= array('Accounts Receivable');
$destFile 			= $thisProjectDir.'/exports/'.$timeStamp;
$ofxAccountType 	= 'CHECKING';
$qifAccountType 	= 'Bank';
$ext 				= 'ofx';

// include files
require_once 'Console/CommandLine.php';
require_once $thisProjectDir.'/lib_general/General.inc.php';
require_once $thisProjectDir.'/CSV2OFX.inc.php';

// create the parser from xml file
$xmlfile = $thisProjectDir.'/csv2ofx.xml';
$parser = Console_CommandLine::fromXmlFile($xmlfile);

try {
	// run the parser
	$result = $parser->parse();

	// command arguments
	if ($result->args['srcFile'] == '$') {
		$stdin = TRUE;
	} //<-- end if -->	
	
	if ($result->args['destFile'] == '$') {
		$stdout = TRUE;
	} elseif ($result->args['destFile']) {
		$destFile = $result->args['destFile'];
	}
	
	// program setting
	$general = new general($result->options['verbose']);
	$program = $general->getBase(__FILE__);

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
		$ext = 'qif';
		$accountTypeList = $qifAccountTypeList;
		$defAccountType = $qifAccountType;
	} else {
		$accountTypeList = $ofxAccountTypeList;
		$defAccountType = $ofxAccountType;
	} //<-- end if -->

	if (!$destFile && !$stdout) {
		$destFile = $thisProjectDir.'/export/'.$timeStamp.'_'.$source.'.'.$ext;
	}

	if ($result->options['accountType']) {
		$defAccountType = $result->options['accountType'];
	}
	
	// debug mode setting
	if ($result->options['debug']) {
		print("[Command opts] ");
		print_r($result->options);
		print("[Command args] ");
		print_r($result->args);
		exit(0);
	} //<-- end if -->

	// execute program
	if ($stdin) {
		$csvContent = $general->csv2Array($general->readSTDIN(), $delimiter, FALSE);
	} else {
		$csvContent = $general->csv2Array($result->args['srcFile'], $delimiter);
	} //<-- end if -->
	
	$general->trimArray($csvContent);
	$general->lengthenArray($csvContent);
	$csvContent = $general->arrayInsertKey($csvContent);
	array_shift($csvContent);
	
	$csv2ofx = new csv2ofx($source, $csvContent, $result->options['verbose']);
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

	$csv2ofx->getAccounts($accountTypeList, $defAccountType);
	
	// variable mode setting
	if ($result->options['variables']) {
		print_r($general->getVars(get_defined_vars()));
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
						$tranSplitAccount = 
							$transaction[0][$csv2ofx->headSplitAccount];
						
						// if this is a transfer from the primary account, 
						// skip it and go to the next transaction
						if ($tranSplitAccount == $primary) {
							continue;
						}
					} //<-- end if not split -->
			
					$timestamp = 
						strtotime($transaction[0][$csv2ofx->headDate]);
					
					// if transaction is not in the specified date range, 
					// go to the next one
					if ($timestamp <= $startDate || $timestamp >= $endDate) { 
						continue;
					}
	
					// get data for first split
					$csv2ofx->setTransactionData($transaction[0], $timestamp);
					
					$content .= 
						$csv2ofx->getQIFTransactionContent($accountType);
					
					if ($csv2ofx->split) {
						// loop through each additional split
						foreach ($transaction as $key => $split) {
							if ($key > 0) {
								$csv2ofx->setTransactionData($split, 
									$timestamp
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
		$csvContent = $general->xmlize($csvContent); // make recursive
		
		if ($result->options['transfer']) {
			$content = $csv2ofx->getOFXTransferHeader($timeStamp);
		} else { // it's a transaction
			$content = $csv2ofx->getOFXTransactionHeader($timeStamp);
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
					$timestamp = strtotime($transaction[$csv2ofx->headDate]);
					
					// if transaction is not in the specified date range, 
					// go to the next one
					if ($timestamp <= $startDate || $timestamp >= $endDate) { 
						continue;
					}

					$csv2ofx->setTransactionData($transaction, $timestamp);
					
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