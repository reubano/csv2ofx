#!/usr/bin/env php
<?php
// Configuration
date_default_timezone_set('Africa/Nairobi');

$thisProjectDir	= dirname(__FILE__);
$projectsDir		= dirname($thisProjectDir);
$today		= date("Ymd"); // format to yyyymmdd
$timeStamp	= date("mdy_His"); // format to mmddyy_hhmmss
$startDate	= strtotime('-1 month');
$endDate	= strtotime('now');
$accounts = array();
$accountTypes = array();
$accountTypeList = array('');
$ofxAccountTypeList = array('CHECKING', 'SAVINGS', 'MONEYMRKT', 'CREDITLINE');
$qifAccountTypeList = array('Bank', 'Bank', 'Bank', 'Bank');
$accountTypeSearch = array(
	array('checking'), array('savings'), 
	array('market', 'money market')
);

$accountTypeSearch[] = array('visa', 'master', 'american express', 'discover');
$account	= 'mint';
$primary	= 'MITFCU Checking';
$outFile 	= $thisProjectDir.'/exports/'.$timeStamp;
$currency	= 'USD';
$defTranType	= 'CREDIT';
$ofxAccountType = 'CHECKING';
$qifAccountType = 'Bank';
$language	= 'ENG';

// include files
require_once 'Console/CommandLine.php';
require_once $projectsDir.'/library/error2.inc';
require_once $projectsDir.'/library/class_general.inc';

// create the parser from xml file
$xmlfile = $thisProjectDir.'/csv2ofx.xml';
$parser = Console_CommandLine::fromXmlFile($xmlfile);

// run the parser
try {
	$result = $parser->parse();

	//*************************************
	// Begin csv2ofx
	//*************************************

	// command argument
	$csvFile 	= $result->args['csvFile'];
		
	// load options if present
	if ($result->options['account']) $thisAccount = $result->options['account'];
	if ($result->options['primary']) $primary = $result->options['primary'];
	if ($result->options['start']) {
		$startDate = strtotime($result->options['start']);
	}
	
	if ($result->options['end']) $endDate = strtotime($result->options['end']);
	if ($result->options['currency']) $currency = $result->options['currency'];
	if ($result->options['language']) $language = $result->options['language'];
	
	if ($result->options['outFile']) {
		$outFile = $result->options['outFile'];
		if ($outFile=='-') $testmode	= TRUE;
	}
	
	if ($result->options['transfer']) $transfer = $result->options['transfer']; 
	if ($result->options['accountType']) {
		$defAccountType = $result->options['accountType'];
	}

	if ($result->options['qif']) {
		$qif = $result->options['qif'];
		$accountTypeList = $qifAccountTypeList;
		$outFile = $outFile.'_'.$account.'_export.qif';
		$defAccountType = $qifAccountType;
	} else {
		$accountTypeList = $ofxAccountTypeList;
		$outFile = $outFile.'_'.$account.'_export.ofx';
		$defAccountType = $ofxAccountType;
	} //<-- end if -->
	
	// set headers 
	// modify the 'custom' section to add support for other websites
	// add additional case blocks if needed
	switch($thisAccount) {
		case 'mint':
			$headAccount 		= 'Account Name';
			$headDate 			= 'Date';
			$headTranType 	= 'Transaction Type';
			$headAmount 		= 'Amount';
			$headDesc 	= 'Original Description';
			$headPayee 		= 'Description';
			$headNotes 		= 'Notes';
			$headCategory 		= 'Category';
			break;

		case 'yoodle':
			$headAccount	= 'Account Name';
			$headDate 		= 'Date';
			$headTranType = 'Transaction Type';
			$headAmount 	= 'Amount';
			$headDesc = 'Original Description';
			$headPayee 	= 'User Description';
			$headNotes 	= 'Memo';
			$headCategory 	= 'Category';
			$headClass 	= 'Classification';
			$headTranId 	= 'Transaction Id';
			break;
 
 		case 'custom':
			$headAccount	= 'Header Field';
			$headAccountId= 'Header Field';
			$headDate 		= 'Header Field';
			$headTranType = 'Header Field';
			$headAmount 	= 'Header Field';
			$headDesc = 'Header Field';
			$headPayee 	= 'Header Field';
			$headNotes 	= 'Header Field';
			$headCategory 	= 'Header Field';
			$headClass 	= 'Header Field';
			$headTranId 	= 'Header Field';
			$headCheckNum = 'Header Field';
			break;
			
		default:
			$errors = TRUE;
			fwrite(STDERR, "Error in $program on line ".__LINE__."\n");
			fwrite(STDERR, "Selected a non-existent account.\n");
			//goto the_end; <-- figure out why goto isn't working -->
	} //<-- end switch -->
		
	// command options
	$debugmode	= $result->options['debug'];
	$varmode	= $result->options['variables'];
	$verbose	= $result->options['verbose'];
	if (is_null($testmode)) $testmode	= $result->options['test'];

	// program setting
	$general = new class_general($verbose);
	$program = $general->get_base(__FILE__);
	
	// debug and variable mode settings
	if ($debugmode OR $varmode) {
		if ($debugmode) {
			print("[Command opts] ");
			print_r($result->options);
			print("[Command args] ");
			print_r($result->args);
		} //<-- end if -->

		if ($varmode) $general->print_vars(get_defined_vars());
		exit(0);
	} //<-- end if -->

	// execute program
	$csvContent = $general->csv2array($csvFile);
	$maxrows = count($csvContent);
	
	for ($i=0; $i<$maxrows; $i++) {
		// remove non xml compliant characters
		if (!$qif) $csvContent[$i] = $general->xmlize($csvContent[$i]);
		// get account names
		$accounts[] = $csvContent[$i][$headAccount];
	} //<-- end for loop -->
	
	$accounts = array_unique($accounts);
	sort($accounts);
	$maxAccounts = count($accounts);
	$maxAccountTypes = count($accountTypeList);
	
	// detect account types
	for ($i=0; $i<$maxAccounts; $i++) { // loop through each account
		// loop through each account type
		for ($j=0; $j<$maxAccountTypes; $j++) {
			$accountType = $accountTypeList[$j];
			$search = $accountTypeSearch[$j];
			
			foreach($search as $search) { // loop through each search term
				$found = stripos($accounts[$i], $search);
				
				if ($found) {
				 	$accountTypes[$i] = $accountType;
				 	continue 3; // stop searching and move to next account
				} //<-- end if -->
			} //<-- end for loop through search terms -->
		} //<-- end for loop through account types -->
					
		// if no matches found, apply default account type
		$accountTypes[$i] = $defAccountType;
		//print_r("$accountTypes[$i]\n");
	} //<-- end for loop through accounts -->
	
	if ($qif) {
		// loop through each account
		for ($i=0; $i<$maxAccounts; $i++) {
			$tranAccount = $accounts[$i];
			$tranAccountType = $accountTypes[$i];
			
			$content .=
			"!Account\n".
			"N$tranAccount\n".
			"T$tranAccountType\n".
			"^\n";

			// find the rows matching the account name and loop 
			// through each transaction
			for ($j=0; $j<$maxrows; $j++) {
				if ($csvContent[$j][$headAccount] == $accounts[$i]) {
					$tranCategory = $csvContent[$j][$headCategory];
					// if this is a transfer from the primary account, skip it 
					// and go to the next transaction
					if ($tranCategory == $primary) continue;
					
					// else, business as usual
					$tranDate = $csvContent[$j][$headDate];
					$tranTimestamp = strtotime($tranDate);
					
					// if transaction is not in the specified date range, 
					// go to the next one
					if ($tranTimestamp >= $startDate 
						&& $tranTimestamp <= $endDate
					) { 
						$tran_date = date("m/d/y", $tranTimestamp);
					} else continue;
					
					$tranType = $csvContent[$j][$headTranType];
					$tranAmount = $csvContent[$j][$headAmount];
					if ($tranType == 'debit') $tranAmount = '-'.$tranAmount;
					$tranDesc = $csvContent[$j][$headDesc];
					$tranPayee = $csvContent[$j][$headPayee];
					$tranNotes = $csvContent[$j][$headNotes];
					if ($tranNotes) $tranDesc = $tranDesc.' - '.$tranNotes;
					if ($headClass) $tranClass = $csvContent[$j][$headClass];
					
					if ($headCheckNum) {
						$tranCheckNum = $csvContent[$j][$headCheckNum];
					}
					
					$content .= "!Type:$tranAccountType\n";
					if ($tranCheckNum) $content .= "N$tranCheckNum\n";
	
					$content .=
					"D$tran_date\n".
					"P$tranPayee\n";
					
					// enter a split so gnucash won't ignore the memo
					if ($tranClass) {
						$content .= "S$tranCategory".'/'."$tranClass"."\n";
					} else {
						$content .= "S$tranCategory\n";
					}
					
					$content .=
					'$'."$tranAmount\n".
					"E$tranDesc\n".
					"^\n";
				} //<-- end if -->
			} //<-- end for loop through transactions -->
		} //<-- end foreach loop through accounts -->
		
	} else { // it's ofx
		if ($transfer) {
			$content =
			"<OFX>\n".
			"	<SIGNONMSGSRSV1>\n".
			"	   <SONRS></SONRS>\n".
			"	</SIGNONMSGSRSV1>\n".
			"	<BANKMSGSRSV1><INTRATRNRS>\n". // Begin response
			"		<TRNUID>$time</TRNUID>\n".
			"		<STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS>\n";
			
			// loop through each account
			for ($i=0; $i<$maxAccounts; $i++) {
				$tranAccount = $accounts[$i];
				$tranAccountType = $accountTypes[$i];
				
				// create account id using an md5 hash of the account name
				$tranAccountId = md5($tranAccount);
	
				// find the rows matching the account name and loop 
				// through each transaction
				for ($j=0; $j<$maxrows; $j++) {
					if ($csvContent[$j][$headAccount] == $accounts[$i]) {
						// if this is a transfer from the primary account, 
						// skip it and go to the next transaction
						$tranCategory = $csvContent[$j][$headCategory];
						if ($tranCategory == $primary) continue; 
						
						// else, business as usual
						$tranDate = $csvContent[$j][$headDate];
						$tranTimestamp = strtotime($tranDate);
						
						// if transaction is not in the specified date range, 
						// go to the next one
						if ($tranTimestamp >= $startDate 
							&& $tranTimestamp <= $endDate
						) {
							$tran_date = date("Ymd", $tranTimestamp);
						} else {
							continue;
						}
	
						$tranType = $csvContent[$j][$headTranType];
						$tranAmount = $csvContent[$j][$headAmount];
						if ($tranType == 'debit') $tranAmount = '-'.$tranAmount;
						$tranDesc = $csvContent[$j][$headDesc];
						$tranPayee = $csvContent[$j][$headPayee];
						$tranNotes = $csvContent[$j][$headNotes];
						
						if ($headClass) {
							$tranClass = $csvContent[$j][$headClass];
						}
						
						if ($headCheckNum) {
							$tranCheckNum = $csvContent[$j][$headCheckNum];
						}
						
						if ($headTranId) $tranId = $csvContent[$j][$headTranId];
						if ($tranNotes) $tranDesc = $tranDesc.' - '.$tranNotes;
						if ($tranClass) $tranDesc = $tranDesc.' - '.$tranClass;
	
						// create category id using an md5 hash of the category
						$tranCategoryId = md5($tranCategory);
					
						// set transaction id to check number (if exists)
						if ($tranCheckNum) $tranId = $tranCheckNum;
						
						// if no id, create it using an md5 
						// hash of the transaction details
						if (!$tranId) {
							$hashCombo = $tran_date.$tranAmount.
								$tranPayee.$tranCategory.$tranDesc;
							$tranId = md5($hashCombo);
						} //<-- end if -->
				
						$content .=
						"	<INTRARS>\n". // Begin transfer response
						"		<CURDEF>$currency</CURDEF>\n".
						"		<SRVRTID>$time</SRVRTID>\n".
						"		<XFERINFO>\n". // Begin transfer aggregate
						"			<BANKACCTFROM>\n".
						"				<BANKID>$tranAccountId</BANKID>\n".
						"				<ACCTID>$tranAccount</ACCTID>\n".
						"				<ACCTTYPE>$tranAccountType</ACCTTYPE>\n".
						"			</BANKACCTFROM>\n".
						"			<BANKACCTTO>\n".
						"				<BANKID>$tranCategoryId</BANKID>\n".
						"				<ACCTID>$tranCategory</ACCTID>\n".
						"				<ACCTTYPE>$defAccountType</ACCTTYPE>\n".
						"			</BANKACCTTO>\n".
						"			<TRNAMT>$tranAmount</TRNAMT>\n".
						"		</XFERINFO>\n". // End transfer aggregate
						"		<DTPOSTED>$tran_date</DTPOSTED>\n".
						"	</INTRARS>\n"; // End transfer response
					} //<-- end if -->
				} //<-- end for loop through transactions -->
			} //<-- end foreach loop through accounts -->
	
			$content .=	"</INTRATRNRS></BANKMSGSRSV1></OFX>"; // End response
	
		} else { // it's a transaction
			$content =
			"<OFX>\n".
			"	<SIGNONMSGSRSV1>\n".
			"	   <SONRS>\n".
			"		<STATUS>\n".
			"			<CODE>0</CODE>\n".
			"			<SEVERITY>INFO</SEVERITY>\n".
			"		</STATUS>\n".
			"		<DTSERVER>$today</DTSERVER>\n".
			"		<LANGUAGE>$language</LANGUAGE>\n".
			"		</SONRS>\n".
			"	</SIGNONMSGSRSV1>\n".
			"	<BANKMSGSRSV1><STMTTRNRS>\n".
			"		<TRNUID>$time</TRNUID>\n".
			"		<STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS>\n";
	
			// loop through each account
			for ($i=0; $i<$maxAccounts; $i++) {
				$tranAccount = $accounts[$i];
				$tranAccountType = $accountTypes[$i];
				
				// create account id using an md5 hash of the account name
				$tranAccountId = md5($tranAccount);
	
				$content .=
				"	<STMTRS>\n".
				"		<CURDEF>$currency</CURDEF>\n".
				"		<BANKACCTFROM>\n".
				"			<BANKID>$tranAccountId</BANKID>\n".
				"			<ACCTID>$tranAccount</ACCTID>\n".
				"			<ACCTTYPE>$tranAccountType</ACCTTYPE>\n".
				"		</BANKACCTFROM>\n".
				"		<BANKTRANLIST>\n".
				"			<DTSTART>$today</DTSTART>\n".
				"			<DTEND>$today</DTEND>\n";
				
				// find the rows matching the account name and loop through 
				// each transaction
				for ($j=0; $j<$maxrows; $j++) {
					if ($csvContent[$j][$headAccount] == $accounts[$i]) {
						// if this is a transfer from the primary account, 
						// skip it and go to the next transaction
						$tranCategory = $csvContent[$j][$headCategory];
						if ($tranCategory == $primary) continue; 
						
						// else, business as usual
						$tranDate = $csvContent[$j][$headDate];
						$tran_date = date("Ymd", strtotime($tranDate));
						$tranType = $csvContent[$j][$headTranType];
						$tranAmount = $csvContent[$j][$headAmount];
						if ($tranType == 'debit') $tranAmount = '-'.$tranAmount;
						$tranDesc = $csvContent[$j][$headDesc];
						$tranPayee = $csvContent[$j][$headPayee];
						$tranNotes = $csvContent[$j][$headNotes];
						
						if ($headClass) {
							$tranClass = $csvContent[$j][$headClass];
						}
						
						if ($headCheckNum) {
							$tranCheckNum = $csvContent[$j][$headCheckNum];
						}
						
						if ($headTranId) $tranId = $csvContent[$j][$headTranId];
						
						if ($tranNotes) {
							$tranMemo = $tranDesc.' - '.$tranNotes.
							' - '.$tranCategory;
						} else {
							$tranMemo = $tranDesc.' - '.$tranCategory;
						}
						
						if ($tranClass) $tranMemo = $tranMemo.' - '.$tranClass;
						
						// set transaction id to check number (if exists)
						if ($tranCheckNum) $tranId = $tranCheckNum;
						
						// if no id, create it using an md5 hash 
						// of the transaction details
						if (!$tranId) {
							$hashCombo = $tran_date.$tranAmount.
								$tranPayee.$tranMemo;
							$tranId = md5($hashCombo);
						}
						
						$content .=
						"				<STMTTRN>\n".
						"					<TRNTYPE>$defTranType</TRNTYPE>\n".
						"					<DTPOSTED>$tran_date</DTPOSTED>\n".
						"					<TRNAMT>$tranAmount</TRNAMT>\n".
						"					<FITID>$tranId</FITID>\n".
						"					<CHECKNUM>$tranId</CHECKNUM>\n".
						"					<NAME>$tranPayee</NAME>\n".
						"					<MEMO>$tranMemo</MEMO>\n".
						"				</STMTTRN>\n";
					} //<-- end if -->
				} //<-- end for loop through transactions -->
			
				$content .=
				"		</BANKTRANLIST>\n".
				"		<LEDGERBAL>\n".
				"			<BALAMT>0</BALAMT>\n".
				"			<DTASOF>$today</DTASOF>\n".
				"		</LEDGERBAL>\n".
				"	</STMTRS>\n";
			} //<-- end foreach loop through accounts -->
	
			$content .=	"</STMTTRNRS></BANKMSGSRSV1></OFX>";
		} //<-- end if transfer -->
	} //<-- end if qif -->

	if (!$testmode) {
		$check = $general->write2file($content, $outFile);
		if (!$check) $errors = TRUE;
	} else fwrite(STDOUT, "$content\n");

	if (!$errors) {
		if ($verbose) {
			fwrite(STDOUT, "Program $program completed successfully!\n");
		}
		
		exit(0);
	} else {
		fwrite(STDERR, "Program $program completed with errors.\n");
		exit(1);
	} //<-- end if errors -->
				
	//*************************************
	// End csv2ofx 
	//*************************************
} catch(Exception $exc) {
	$parser->displayError($exc->getMessage());
}
?>