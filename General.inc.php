<?php
/******************************************************************************
 * purpose: contains general functions to be used by all programs
 *****************************************************************************/

//<-- begin class -->
class General {
	var $className = __CLASS__;	// class name
	var $verbose;
	var $fileIgnoreList = array('.', '..', '.DS_Store','.svn','.git*');
	var $varIgnoreList = array('HTTP_POST_VARS', 'HTTP_GET_VARS', 
		'HTTP_COOKIE_VARS', 'HTTP_SERVER_VARS', 'HTTP_ENV_VARS', 
		'HTTP_SESSION_VARS', '_ENV', 'PHPSESSID','SESS_DBUSER', 
		'SESS_DBPASS','HTTP_COOKIE', 'GLOBALS', '_ENV', 'HTTP_ENV_VARS', 'argv', 
		'argc', '_POST', 'HTTP_POST_VARS', '_GET', 'HTTP_GET_VARS', '_COOKIE', 
		'HTTP_COOKIE_VARS', '_SERVER', 'HTTP_SERVER_VARS', '_FILES', 
		'HTTP_POST_FILES', '_REQUEST', 'ignoreList',
	);

	/************************************************************************** 
	 * This method is the class constructor 
 	 * 
	 * @return TRUE
	 *************************************************************************/
	function general($verbose = FALSE) {
		$this->verbose = $verbose;
		if ($this->verbose) {
			fwrite(STDOUT, "$this->className class constructor set.\n");
		} //<-- end if -->
		return TRUE;
	} //<-- end function -->

	/************************************************************************** 
	 * This method gets the get file or filename extension 
 	 * 
	 * @return extension
	 * @throws Exception if passed an empty string
	 *************************************************************************/
	function getExtension($file) {
		if (empty($file)) {
			throw new Exception('Empty file passed from '.__CLASS__.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$ext = pathinfo($file, PATHINFO_EXTENSION);
				return $ext;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.__CLASS__.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/************************************************************************** 
	 * Recursively searches an array for the nth occurance of a given value 
	 * type and returns the corresponding key if successful. If passed a 
	 * multi-dimensional array, it will returns an array of keys.  
 	 *
 	 * @param 	array 	$haystack 	the array to search
 	 * @param 	string 	$needle 	the type of element to find (i.e. 'numeric' 
 	 *								or 'string')
	 * @param 	int 	$n 			the nth element to find   
	 * @return 	mixed	the key (or array of keys) of the found element(s) 
	 * @throws 	Exception if it can't find enough elements
	 * @throws 	Exception if passed an invaled needle
	 *************************************************************************/
	function arraySearchType($needle, $haystack,  $n = 1) {
		try {
			$i = 0; // needle element counter
			
			foreach ($haystack as $key => $value) {
				// check to make sure I haven't found too many elements
				if ($i < $n) {
					// It's not an array, so look for needle elements
					if (!is_array($value)) { 
						switch ($needle){
							case 'numeric':
								if (is_numeric($value)) {
									$needleKeys[] = $key;
									$i++;
								} //<-- end if -->
								
								break;
								
							case 'string':
								if (!is_numeric($value)) {
									$needleKeys[] = $key;
									$i++;
								} //<-- end if -->
								
								break;
								
							default:
								throw new Exception('Wrong search type entered.'. 
									'Please type \'numeric\' or \'string\'.'
								);
						} //<-- end switch -->
					} else { // it IS an array, so recurse
						$needleKeys[] = general::arraySearchType($needle, $value, $n);
					} //<-- end if !is_array -->
				} //<-- end if $i < $n -->
			} //<-- end foreach -->
			
			// check to see if I recursed
			if (count($needleKeys) > 1 
				&& count(array_unique($needleKeys)) == 1) 
			{
				// I recursed so return entire array of last keys
				return $needleKeys;
			} else { // I didn't recurse
				// check to make sure I found enough elements
				if (count($needleKeys) >= $n) {
					// I only want the last key found
					$lastKey = array_pop($needleKeys);
					return $lastKey;
				} else {
					throw new Exception('Array does not contain '.$n.
						' '.$needle.' elements'
					);
				} //<-- end if -->
			} //<-- end if -->
			
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.__CLASS__.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->
	
	/************************************************************************** 
	 * This method gets writes data to a file 
 	 * 
 	 * @return boolean regarding success/failure
	 * @throws Exception if passed an empty string
	 * @throws Exception if file already exists
	 *************************************************************************/
	function write2File($content, $file) {
		//need to add check that makes sure path exists
		if (empty($content)) { // check to make sure $content isn't empty
			throw new Exception('Empty content passedfrom '.__CLASS__.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} elseif (file_exists($file) && filesize($file) != 0) {
			throw new Exception('File .'.$file.' already exsits from '.
				__CLASS__.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$handle = fopen($file, 'w');
				$bytes = fwrite($handle, $content);
				fclose($handle);
					
				if ($this->verbose) {
					fwrite(STDOUT, "Wrote $bytes bytes to $file!\n");
				} //<-- end if -->
					
				return TRUE;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.__CLASS__.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/************************************************************************** 
	 * This method gets csv data 
 	 *
	 * @return array of csv data 
	 * @throws Exception if the CSV file does not exist  
	 *************************************************************************/ 
	function csv2Array($csvFile, $fieldDelimiter = ',') {		
		if (!file_exists($csvFile)) {
			throw new Exception('File '.$csvFile.' does not exist from '.
				__CLASS__.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				/*
				$perl = Perl::getInstance();
				$content = $perl->eval('
					use Text::xSV;
					
					my $csv = new Text::xSV;
					my @file;
					$csv->set_sep($fieldDelimiter);
					$csv->open_file($csvFile);
					while (my $row = $csv->get_row()) {
						foreach (@$row) { 
							$_ = "" unless defined $_;
						}; //<-- end foreach -->
						
						push(@file, $row);
					} //<-- end while -->
				'); //<-- end perl -->
				*/			
				
				$tempFile = general::makeLFLineEndings($csvFile);
				$handle = fopen($tempFile, 'r');
				
			    while (($data = fgetcsv($handle, 1000, $fieldDelimiter)) 
			    		!== FALSE) {
					$content[] = $data;
			    } //<-- end while -->
				
				fclose($handle);
				unlink($tempFile);
				return $content;
				
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.__CLASS__.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/************************************************************************** 
	 * This method reads input from STDIN
 	 *
	 * @return string of inputted data 
	 * @throws Exception if there is no input  
	 *************************************************************************/ 
	function readSTDIN() {
		try {
			$string = NULL;
			$handle = fopen('php://stdin', 'r');
			
			while (!feof($handle)) {
				$string .= fgets($handle, 1024);
			} //<-- end while -->
			
			fclose($handle);
			
			if (!$string) {
				throw new Exception('No data read from STDIN.');
			} else {
				return $string;
			} //<-- end if -->
		} catch (Exception $e) { 
			die('Exception in '.__CLASS__.'->'.__FUNCTION__.'() line '.
				$e->getLine().': '.$e->getMessage()."\n"
			);
		} //<-- end try -->
	} //<-- end function -->

	/************************************************************************** 
	 * This method expects an array of the following form:
 	 * $content = array(array('key 1', 'key 2', 'key 3'), 
 	 *						array('value 1', 'value 2', 'value 3'),
 	 *						array('value 4', 'value 5', 'value 6'))
 	 *
	 * and returns it in the following form:
	 * $content = array(array('key 1' => 'key 1', 
	 *							'key 2' => 'key 2', 
	 *							'key 3' => 'key 3'),
	 * 						array('key 1' => 'value 1', 
	 *							'key 2' => 'value 2', 
	 *							'key 3' => 'value 3'),
	 *						array('key 1' => 'value 4', 
	 *							'key 2' => 'value 5', 
	 *							'key 3' => 'value 6'))
	 *
	 * @return array of csv data 
	 * @throws Exception if the CSV file does not exist  
	 *************************************************************************/ 
	function arrayInsertKey($content) {	
		if (!is_array($content[0])) {
			throw new Exception('Please use a multi-dimensional array from '.
				__CLASS__.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {				
				$maxElements = count($content);
				$maxValues = count($content[0]);
				
				// loop through each array
				foreach ($content as $values) {				
					// check that arrays are same size
					if (count($values) != $maxValues) { 
						throw new Exception('Arrays are not of same size');
					} //<-- end if -->
				} //<-- end for -->
				
				$keys = $content[0]; // get key names
				
				// loop through each array
				foreach ($content as $values) { 
					$newContent[] = array_combine($keys, $values);
				} //<-- end for loop through each array -->
				
				return $newContent;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.__CLASS__.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->
	
	/************************************************************************** 
	 * This method recursively returns an array of all defined  
	 * variables
 	 *
	 * @return array of all defined variables
	 * @throws Exception if an empty value is passed 
	 *************************************************************************/ 
	function getVars($definedVars, $ignoreList = NULL) {
		if (empty($definedVars)) {
			throw new Exception('Empty content passed from '.__CLASS__.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				if (empty($ignoreList)) {
					$ignoreList = $this->varIgnoreList;
				} //<-- end if -->
				
				//$message['Variables:'] = array();
				
				foreach ($definedVars as $key => $val) {
					if (!in_array($key,$ignoreList) && !empty($val)) {
						if (is_array($val)) {
							$message[$key] = general::getVars($val);
						} elseif (is_string($val)) { 
							$message[$key] = $val;
						} //<-- end if -->
					} //<-- end if --> 
				} //<-- end foreach -->
				
				return $message;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.__CLASS__.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->
	
	/************************************************************************** 
	 * This method gets the file or filename base (filename without extension)  
 	 *
	 * @return string
	 * @throws Exception if an empty value is passed
	 *************************************************************************/ 
	function getBase($file) {
		if (empty($file)) {
			throw new Exception('Empty file passed from '.__CLASS__.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$base = pathinfo($file, PATHINFO_FILENAME);
				return $base;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.__CLASS__.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/************************************************************************** 
	 * This method changes the line endings of a text file to LF
	 * 
 	 *
	 * @return filename of normalized file
	 *************************************************************************/ 
	function makeLFLineEndings($file) {
		if (!file_exists($file)) {
			throw new Exception('File '.$file.' does not exist from '.
				__CLASS__.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$handle 	= fopen($file, 'r');
				$string 	= NULL;
				$tempFile	= tempnam('/tmp', __FUNCTION__.'.');
				
				while (!feof($handle)) {
					$line = fgets($handle, 1024);
					$line = str_replace("\r\n", "\n", $line);
					$line = str_replace("\r", "\n", $line);
					$string .= $line;
				} //<-- end while -->
				
				fclose($handle);
				general::write2File($string, $tempFile);
				return $tempFile;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.__CLASS__.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/************************************************************************** 
	 * This takes an array of the following form:
	 * $content = array(array('key 1' => 'value 1', 
	 *							'key 2' => 'value 2', 
	 *							'key 3' => 'value 3'),
	 *						array('key 1' => 'value 4', 
	 *							'key 2' => 'value 5', 
	 *							'key 3' => 'value 6'))
	 *
	 * and formats the given to key to a number or date suitable for import 
	 * into a sqlite database
	 * 
 	 *
	 * @return formatted array
	 * @throws Exception if the wrong format is entered
	 *************************************************************************/
	function formatArray($content, $key, $format) {
		try {
			$i = 0;
			
			switch ($format){
				case 'number':
					foreach ($content as $row) {
						$number = $row[$key];
						$number = str_replace(',', '', $number);
						$number = $number + 0;
						$formattedRow[] = number_format($number, 2, '.',
							''
						);
					} //<-- end foreach -->
				
					break;
					
				case 'date':
					foreach ($content as $row) {
						$date = $row[$key];
						
						// format to yyyy-mm-dd
						$formattedRow[] = date("Y-m-d", strtotime($date));
					} //<-- end foreach -->
					
					break;
					
				default:
					throw new Exception('Wrong format entered. Please type'.
						' \'number\' or \'date\'.'
					);
			} //<-- end switch -->

			foreach ($formattedRow as $row) {
				$content[$i][$key] = $row;
				$i++;
			} //<-- end foreach -->
					
			return $content;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.__CLASS__.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end function -->
			
	/************************************************************************** 
	 * This method recursively performs a string replace on array values
	 * 
 	 *
	 * @return sanitized array 
	 *************************************************************************/ 
	function arraySubstitute($array, $find, $replacement) {
		try {
			foreach ($array as $data) {
				if (!is_array($data)) { // If it's not an array, sanitize it
					$cleanArray[] = str_replace($find, $replacement, $data);
				} else { // it IS an array, so recurse
					$cleanArray[] = general::arraySubstitute($data, 
						$find, $replacement
					);
				} //<-- end if -->
			} //<-- end foreach -->		
			
			return $cleanArray;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.__CLASS__.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/************************************************************************** 
	 * This method writes an array to a pre-existing csv file 
 	 *
	 * @return TRUE 
	 * @throws Exception if the CSV file already exists
	 *************************************************************************/ 
	function overwriteCSV($content, $csvFile, $fieldDelimiter = ',') {	
		if (!file_exists($csvFile)) {
			throw new Exception('File .'.$csvFile.' does not exsit from '.
				__CLASS__.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$tempFile = general::makeLFLineEndings($csvFile);
				$handle = fopen($tempFile, 'r');
				general::array2CSV($content, $tempFile, $fieldDelimiter);
				copy($tempFile, $csvFile);				
				fclose($handle);
				unlink($tempFile);
				return TRUE;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.__CLASS__.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->
			
	/************************************************************************** 
	 * This method writes an array to a csv file 
 	 *
	 * @return TRUE 
	 * @throws Exception if the CSV file does not exist  
	 *************************************************************************/ 
	function array2CSV($content, $csvFile, $fieldDelimiter = ',') {	
		if (file_exists($csvFile) && filesize($csvFile) != 0) {
			throw new Exception('File .'.$csvFile.' already exsits from '.
				__CLASS__.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {	
				$handle = fopen($csvFile, 'w');
				foreach ($content as $fields) {
				    $length = fputcsv($handle, $fields, $fieldDelimiter);
				} //<-- end foreach -->
				
				fclose($handle);
				
				if ($this->verbose) {
					fwrite(STDOUT, "wrote $length characters to $csvFile!\n");
				} //<-- end if -->
				
				return TRUE;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.__CLASS__.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->
} //<-- end class -->
?>