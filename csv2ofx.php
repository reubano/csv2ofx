#!/usr/bin/env php
<?php
/**
 *******************************************************************************
 * csv2ofx converts a csv file to ofx and qif
 *******************************************************************************
 */

define('PROGRAM', pathinfo(__FILE__, PATHINFO_FILENAME));

if (strpos('@php_bin@', '@php_bin') === 0) { // not a pear install
	define('PROJECT_DIR', dirname(__FILE__).DIRECTORY_SEPARATOR);
} else {
	define(
		'PROJECT_DIR', '@php_dir@'.DIRECTORY_SEPARATOR.PROGRAM.
		DIRECTORY_SEPARATOR
	);
}

define('CUR_DIR', getcwd().DIRECTORY_SEPARATOR);
define('DATE_STAMP', date('Ymd')); // format to yyyymmdd
define('TIME_STAMP', date('Ymd_His')); // format to yyyymmdd_hhmmss
define('XML_FILE', PROJECT_DIR.PROGRAM.'.xml');

require PROJECT_DIR.'Autoload.php';

$defType = array('ofx' => 'CHECKING', 'qif' => 'Bank');
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
$typeList = array('ofx' => $ofxList, 'qif' => $qifList);
$ext = array('ofx' => 'ofx', 'qif' => 'qif');

// create the parser from xml file
$parser = Console_CommandLine::fromXmlFile(XML_FILE);

try {
	// run the parser
	$result = $parser->parse();

	// command arguments
	$source = $result->args['source'];
	$dest = $result->args['dest'];

	// load options if present
	$delimiter = $result->options['delimiter'];
	$mapping = $result->options['mapping'];
	$primary = $result->options['primary'];
	$start = date('YmdHis', strtotime($result->options['start']));
	$end = date('YmdHis', strtotime($result->options['end']));
	$collAccts = explode(',', $result->options['collapse']);
	$currency = $result->options['currency'];
	$language = $result->options['language'];
	$overwrite = $result->options['overwrite'];
	$transfer = $result->options['transfer'];
	$qif = $result->options['qif'];
	$type = $qif ? 'qif' : 'ofx';
	$defType = $result->options['accountType'] ?: $defType[$type];
	$typeList = $typeList[$type];
	$ext = $ext[$type];

	switch ($dest){
		case '$':
			$stdout = TRUE;
			break;

		case '':
			$stdout = FALSE;
			$dest = CUR_DIR.TIME_STAMP.'_'.$mapping.'.'.$ext;
			break;

		default:
			$stdout = FALSE;
	} //<-- end switch -->

	if ($result->options['debug']) {
		print('[Command opts] ');
		print_r($result->options);
		print('[Command args] ');
		print_r($result->args);
		exit(0);
	} //<-- end if -->

	// program setting
	$vars = new vars($result->options['verbose']);
	$file = new file($result->options['verbose']);
	$array = new myarray($result->options['verbose']);
	$string = new string($result->options['verbose']);

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
	$csv2ofx->csvContent = $csv2ofx->cleanAmounts();
	$splitContent = $csv2ofx->makeSplits();

	if ($csv2ofx->split) {
		// verify splits
		$csv2ofx->verifySplits($splitContent);

		// sort splits by account name
		$function = array('myarray', 'arraySortBySubValue');
		$field = array_fill(0, count($splitContent), $csv2ofx->headAccount);
		$splitContent = array_map($function, $splitContent, $field);

		// combine splits of collapsable accounts
		$splitContent = $csv2ofx->collapseSplits($splitContent, $collAccts);

		// get accounts and keys
		$maxAmounts = $csv2ofx->getMaxSplitAmounts($splitContent);
		$accounts = $csv2ofx->getAccounts($splitContent, $maxAmounts);
		$keys = array_keys($accounts);

		// move main splits to beginning of transaction array
		$function = array('myarray', 'arrayMove');
		$field = array_fill(0, count($splitContent), $keys);
		$splitContent = array_map($function, $splitContent, $field);
	} else { // not a split transaction
		$accounts = $csv2ofx->getAccounts($splitContent);
	} //<-- end if split -->

	$accountTypes = $csv2ofx->getAccountTypes($accounts, $typeList, $defType);
	$accounts = array_combine($accounts, $accountTypes);
	$uniqueAccounts = array_unique(sort($accounts));

	// variable mode setting
	if ($result->options['variables']) {
		print_r($vars->getVars(get_defined_vars()));
		exit(0);
	}

	$csvContent = $qif ? $csvContent : $array->xmlize($csvContent);
	$ofxContent = $transfer
		? $csv2ofx->getOFXTransferHeader($timeStamp)
		: $csv2ofx->getOFXTransactionHeader($timeStamp);

	$content = $qif ? '' : $ofxContent;

	$qif
		? array_walk($uniqueAccounts, $mainQIF)
		: array_walk($uniqueAccounts, $mainOFX);

	$ofxContent = $transfer
		? $csv2ofx->getOFXTransferFooter()
		: $csv2ofx->getOFXTransactionFooter();

	$content .= $qif ? '' : $ofxContent;

// 	if ($qif) {
// 		foreach ($uniqueAccounts as $account => $accountType) {
	$mainQIF = function ($accountType, $account) use (&$content) {
		$content .= $csv2ofx->getQIFTransactionHeader($account, $accountType);

		// loop through each transaction
		foreach ($csv2ofx->newContent as $transaction) {
			// if transaction doesn't match the account name, skip it
			$firstSplit = current($transaction);
			if ($firstSplit[$csv2ofx->headAccount] != $account) continue;

			// if transaction is not in the specified date range, skip it
			$date = $firstSplit[$csv2ofx->headDate];
			$timeStamp = date('YmdHis', strtotime($date));
			if ($timeStamp <= $start || $timeStamp >= $end) continue;

			// if this is a transfer from the primary account, skip it
			$splitAccount = $csv2ofx->headSplitAccount
				? $firstSplit[$csv2ofx->headSplitAccount]
				: $csv2ofx->defSplitAccount;

			if ($csv2ofx->split && $splitAccount == $primary) continue;

			// get data
			$function = array('csv2ofx', 'getTransactionData');
			$fill = array_fill(0, count($transaction), $timeStamp);
			$data = $csv2ofx->split
				? $csv2ofx->getTransactionData($firstSplit, $timeStamp)
				: array_map($function, $transaction, $fill);

			// load content
			$content .= $csv2ofx->getQIFTransactionContent($accountType);
			$function = array('csv2ofx', 'getQIFSplitContent');
			$fill = array_fill(0, count($transaction), $timeStamp);
			$content .= $csv2ofx->split
				? $csv2ofx->getQIFSplitContent($splitAccount, $data)
				: implode('', array_map($function, $transaction, $fill));

			$content .= $csv2ofx->getQIFTransactionFooter();
		} //<-- end loop through transactions -->
	}; //<-- end loop through accounts -->
// 	} else { // it's ofx
		// loop through each account
// 		foreach ($uniqueAccounts as $account => $accountType) {
	$mainOFX = function ($accountType, $account) use (&$content) {
		$content .= $transfer
			? ''
			: $csv2ofx->getOFXTransactionAccountStart(
				$currency, md5($account), $account, $accountType, DATE_STAMP
			);

		// loop through each transaction
		foreach ($csvContent as $transaction) {
			// if transaction doesn't match the account name, skip it
			if ($transaction[$csv2ofx->headAccount] != $account) continue;

			// if this is a transfer from the primary account, skip it
			$splitAccount = $transaction[$csv2ofx->headSplitAccount];
			if ($splitAccount == $primary) continue;

			// else, business as usual
			$date = $firstSplit[$csv2ofx->headDate];
			$timeStamp = date('YmdHis', strtotime($date));

			// if transaction is not in the specified date range, skip it
			if ($timeStamp <= $start || $timeStamp >= $end) continue;
			$data = $csv2ofx->getTransactionData($transaction, $timeStamp);

			$content .= $transfer
				? $csv2ofx->getOFXTransfer($account, $accountType)
				: $csv2ofx->getOFXTransaction();
		}; //<-- end for loop through transactions -->

		$content .= $transfer
			? ''
			: $csv2ofx->getOFXTransactionAccountEnd($timeStamp);
	}; //<-- end foreach loop through accounts -->

// 		$content .= $transfer
// 			? $csv2ofx->getOFXTransferFooter()
// 			: $csv2ofx->getOFXTransactionFooter();
// 	} //<-- end if qif -->

	$stdout ? print($content) : $file->write2file($content, $dest, $overwrite);
	exit(0);
} catch (Exception $e) {
	fwrite(STDOUT, 'Program '.PROGRAM.': '.$e->getMessage()."\n");
	exit(1);
}
?>
