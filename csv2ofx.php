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
define('TIME_STAMP', date('YmdHis')); // format to yyyymmddhhmmss
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
	$startDate = date('Ymd', strtotime($start));
	$end = date('YmdHis', strtotime($result->options['end']));
	$endDate = date('Ymd', strtotime($end));
	$collAccts = explode(',', $result->options['collapse']);
	$currency = $result->options['currency'];
	$language = $result->options['language'];
	$overwrite = $result->options['overwrite'];
	$transfer = $result->options['transfer'];
	$respType = $transfer ? 'INTRATRNRS' : 'STMTTRNRS';
	$qif = $result->options['qif'];
	$type = $qif ? 'qif' : 'ofx';
	$defType = $result->options['accountType'] ?: $defType[$type];
	$typeList = $typeList[$type];
	$ext = $ext[$type];

	switch ($dest){
		case '$':
			$stdout = true;
			break;

		case '':
			$stdout = false;
			$dest = CUR_DIR.TIME_STAMP.'_'.$mapping.'.'.$ext;
			break;

		default:
			$stdout = false;
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

	$csv2ofx = new ofx($mapping, $csvContent, $result->options['verbose']);
	$csv2ofx->csvContent = $csv2ofx->cleanAmounts();
	$splitContent = $csv2ofx->makeSplits();

	if ($csv2ofx->split) {
		// verify splits
		$csv2ofx->verifySplits($splitContent);

		// sort splits by account name
		$function = array($array, 'arraySortBySubValue');
		$field = array_fill(0, count($splitContent), $csv2ofx->headAccount);
		$splitContent = array_map($function, $splitContent, $field);

		// combine splits of collapsable accounts
		$splitContent = $collAccts
			? $csv2ofx->collapseSplits($splitContent, $collAccts)
			: $splitContent;

		// get accounts and keys
		$maxAmounts = $csv2ofx->getMaxSplitAmounts($splitContent);
		$accountInfo = $csv2ofx->getAccounts($splitContent, $maxAmounts);
		$accounts = $accountInfo['accounts'];
		$keys = $accountInfo['keys'];

		// move main splits to beginning of transaction array
		$function = array($array, 'arrayMove');
		$splitContent = array_map($function, $splitContent, $keys);
	} else { // not a split transaction
		$accountInfo = $csv2ofx->getAccounts($splitContent);
		$accounts = $accountInfo['accounts'];
	} //<-- end if split -->

	$accountTypes = $csv2ofx->getAccountTypes($accounts, $typeList, $defType);
	$uniqueAccounts = array_combine($accounts, $accountTypes);
 	asort($uniqueAccounts);

	// variable mode setting
	if ($result->options['variables']) {
		print_r($vars->getVars(get_defined_vars()));
		exit(0);
	}

	// sub routines
	$subQIF = function ($transaction, $key, $accountInfo) use (
		&$content, $csv2ofx, $start, $end, $primary
	) {
		$accountType = $accountInfo[0];
		$account = $accountInfo[1];

		// if transaction doesn't match the account name, skip it
		$firstSplit = current($transaction);
		if ($firstSplit[$csv2ofx->headAccount] != $account) return;

		// if transaction is not in the specified date range, skip it
		$date = $firstSplit[$csv2ofx->headDate];
		$timeStamp = date('YmdHis', strtotime($date));
		if ($timeStamp <= $start || $timeStamp >= $end) return;

		// if this is a transfer from the primary account, skip it
		$splitAccount = $csv2ofx->headSplitAccount
			? $firstSplit[$csv2ofx->headSplitAccount]
			: $csv2ofx->defSplitAccount;

		if ($csv2ofx->split && $splitAccount == $primary) return;

		// get data
		$function = array($csv2ofx, 'getTransactionData');
		$data = $csv2ofx->split
			? array_map($function, $transaction)
			: $csv2ofx->getTransactionData($firstSplit);

		// load content
		$content .= $csv2ofx->split
			? $csv2ofx->getQIFTransactionContent($accountType, $data[0])
			: $csv2ofx->getQIFTransactionContent($accountType, $data);

		$function = array($csv2ofx, 'getQIFSplitContent');
		$csv2ofx->split ? array_shift($data) : '';
		$splitAccounts = $csv2ofx->split
			? $csv2ofx->getSplitAccounts($transaction)
			: null;

			$content .= $csv2ofx->split
			? implode('', array_map($function, $splitAccounts, $data))
			: $csv2ofx->getQIFSplitContent($splitAccount, $data);

		$content .= $csv2ofx->getQIFTransactionFooter();
	}; //<-- end closure -->

	$subOFX = function ($transaction, $key, $accountInfo) use (
		&$content, &$timeStamp, $csv2ofx, $start, $end, $primary, $transfer,
		$language, $currency
	) {
		$accountType = $accountInfo[0];
		$account = $accountInfo[1];
		$accountId = md5($account);

		// if transaction doesn't match the account name, skip it
		if ($transaction[$csv2ofx->headAccount] != $account) return;

		// if this is a transfer from the primary account, skip it
		$splitAccount = $transaction[$csv2ofx->headSplitAccount];
		if ($splitAccount == $primary) return;

		// else, business as usual
		$date = $transaction[$csv2ofx->headDate];
		$timeStamp = date('YmdHis', strtotime($date));

		// if transaction is not in the specified date range, skip it
		if ($timeStamp <= $start || $timeStamp >= $end) return;
		$data = $csv2ofx->getTransactionData($transaction);

		$content .= $transfer
			? $csv2ofx->getOFXTransfer($currency, $timeStamp, $accountId, $account, $accountType, $data)
			: $csv2ofx->getOFXTransaction($timeStamp, $data);
	}; //<-- end closure -->

	$mainQIF = function ($accountType, $account) use (
		&$content, $subQIF, $csv2ofx, $splitContent
	) {
		$content .= $csv2ofx->getQIFAccountHeader($account, $accountType);
		array_walk($splitContent, $subQIF, array($accountType, $account));
	}; //<-- end closure -->

	$mainOFX = function ($accountType, $account) use (
		&$content, $csvContent, $subOFX, $csv2ofx, $transfer, $currency,
		$startDate, $endDate
	) {
		$content .= $transfer
			? ''
			: $csv2ofx->getOFXTransactionAccountStart(
				$currency, md5($account), $account, $accountType, $startDate,
				$endDate
			);

		array_walk($csvContent, $subOFX, array($accountType, $account));

		$content .= $transfer
			? ''
			: $csv2ofx->getOFXTransactionAccountEnd();
	}; //<-- end closure -->

	// main routines
	$csvContent = $qif ? $csvContent : $array->xmlize($csvContent);
	$ofxContent = $csv2ofx->getOFXHeader(TIME_STAMP, $language);
	$ofxContent .= $csv2ofx->getOFXResponseStart($respType);
	$content = $qif ? '' : $ofxContent;

	$qif
		? array_walk($uniqueAccounts, $mainQIF)
		: array_walk($uniqueAccounts, $mainOFX);

	$ofxContent = $csv2ofx->getOFXResponseEnd($respType);
	$content .= $qif ? '' : $ofxContent;
	$stdout ? print($content) : $file->write2file($content, $dest, $overwrite);
	exit(0);
} catch (Exception $e) {
	fwrite(STDOUT, 'Program '.PROGRAM.': '.$e->getMessage()."\n");
	exit(1);
}
?>
