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
$stdin 				= FALSE;
$today				= date("Ymd"); // format to yyyymmdd
$timeStamp			= date("mdy_His"); // format to mmddyy_hhmmss
$startDate			= strtotime('1/1/1900');
$endDate			= strtotime('now');
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

$source				= 'mint';
$collapse			= array('Accounts Receivable');
$primary			= 'MITFCU Checking';
$outFile 			= $thisProjectDir.'/exports/'.$timeStamp;
$currency			= 'USD';
$defTranType		= 'CREDIT';
$ofxAccountType 	= 'CHECKING';
$qifAccountType 	= 'Bank';
$language			= 'ENG';

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

	// command argument
	$csvFile = $result->args['csvFile'];

	if ($csvFile == '$') {
		$stdin = TRUE;
	} //<-- end if -->
	
	// command options
	$debugmode	= $result->options['debug'];
	$varmode	= $result->options['variables'];
	$verbose	= $result->options['verbose'];
	$testmode	= $result->options['test'];

	// program setting
	$general = new general($verbose);
	$program = $general->getBase(__FILE__);

	// load options if present
	if ($result->options['source']) {
		$source = $result->options['source'];
	}
	
	if ($result->options['primary']) {
		$primary = $result->options['primary'];
	}
	
	if ($result->options['start']) {
		$startDate = strtotime($result->options['start']);
	}
	
	if ($result->options['end']) {
		$endDate = strtotime($result->options['end']);
	}
	
	if ($result->options['collapse']) {
		$collapse = $result->options['collapse'];
		$collapse = explode(',', $collapse);
	}
	
	if ($result->options['currency']) {
		$currency = $result->options['currency'];
	}
	
	if ($result->options['language']) {
		$language = $result->options['language'];
	}
	
	if ($result->options['outFile']) {
		$outFile = $result->options['outFile'];
		
		if ($outFile=='-') {
			$testmode = TRUE;
		}
	}
	
	if ($result->options['transfer']) {
		$transfer = $result->options['transfer'];
	}
	
	if ($result->options['accountType']) {
		$defAccountType = $result->options['accountType'];
	}

	if ($result->options['qif']) {
		$qif = $result->options['qif'];
		$accountTypeList = $qifAccountTypeList;
		$outFile = $outFile.'_'.$source.'_export.qif';
		$defAccountType = $qifAccountType;
	} else {
		$accountTypeList = $ofxAccountTypeList;
		$outFile = $outFile.'_'.$source.'_export.ofx';
		$defAccountType = $ofxAccountType;
	} //<-- end if -->
	
	// debug and variable mode settings
	if ($debugmode OR $varmode) {
		if ($debugmode) {
			print("[Command opts] ");
			print_r($result->options);
			print("[Command args] ");
			print_r($result->args);
		} //<-- end if -->

		if ($varmode) {
			$general->printVars(get_defined_vars());
		}
		
		exit(0);
	} //<-- end if -->

	// execute program
	if ($stdin) {
		$csvContent = $general->readSTDIN();
	} else {
		$csvContent = $general->csv2Array($csvFile);
	} //<-- end if -->
	
	$csvContent = $general->arrayInsertKey($csvContent);
	array_shift($csvContent);
	
	$csv2ofx = new csv2ofx($source, $csvContent, $verbose);
	$csv2ofx->setAmounts();

	if ($csv2ofx->split) {
		$csv2ofx->setTranIds();
		$csv2ofx->verifySplits();
		$csv2ofx->sortSplits($csv2ofx->headAccount);
		$csv2ofx->collapseSplits($collapse);
		$csv2ofx->organizeSplits();
	} else { // not a split transaction
		$csv2ofx->makeSplits();
	} //<-- end if split -->

	$csv2ofx->getAccounts($accountTypeList, $defAccountType);

	if ($qif) {
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
		
		if ($transfer) {
			$content = $csv2ofx->getOFXTransferHeader($timeStamp);
		} else { // it's a transaction
			$content = $csv2ofx->getOFXTransactionHeader($timeStamp);
		} //<-- end if transfer -->

		// loop through each account
		foreach ($csv2ofx->accounts as $account => $accountType) {
			// create account id using an md5 hash of the account name
			$accountId = md5($account);
			
			if (!$transfer) {
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
					
					if ($transfer) {
						$content .= 
							$csv2ofx->getOFXTransfer($account, $accountType);
					} else { // it's a transaction
						$content .= $csv2ofx->getOFXTransaction();
					} //<-- end if transfer -->
				} //<-- end if -->
			} //<-- end for loop through transactions -->
			
			if (!$transfer) {
				$content .= $csv2ofx->getOFXTransactionAccountEnd();
			} //<-- end if not transfer -->
		} //<-- end foreach loop through accounts -->
		
		if ($transfer) {
			$content .=$csv2ofx->getOFXTransferFooter();
		} else { // it's a transaction
			$content .=	$csv2ofx->getOFXTransactionFooter();
		} //<-- end if transfer -->
	} //<-- end if qif -->

	if (!$testmode) {
		$general->write2file($content, $outFile);
	} else {
		print_r($content);
	} //<-- end if not test mode -->

	exit(0);
} catch (Exception $e) {
	fwrite(STDOUT, 'Program '.$program.': '.$e->getMessage()."\n");
	exit(1);
}
?>