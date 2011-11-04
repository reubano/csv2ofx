<?php
/******************************************************************************
 * purpose: contains general functions to be used by all programs
 *****************************************************************************/

//<-- begin class -->
class General {
	protected $className = __CLASS__;	// class name
	protected $verbose;
	protected $fileIgnoreList = array('.', '..', '.DS_Store','.svn','.git*');
	protected $varIgnoreList = array('HTTP_POST_VARS', 'HTTP_GET_VARS', 
		'HTTP_COOKIE_VARS', 'HTTP_SERVER_VARS', 'HTTP_ENV_VARS', 
		'HTTP_SESSION_VARS', '_ENV', 'PHPSESSID','SESS_DBUSER', 
		'SESS_DBPASS','HTTP_COOKIE', 'GLOBALS', '_ENV', 'HTTP_ENV_VARS', 'argv', 
		'argc', '_POST', 'HTTP_POST_VARS', '_GET', 'HTTP_GET_VARS', '_COOKIE', 
		'HTTP_COOKIE_VARS', '_SERVER', 'HTTP_SERVER_VARS', '_FILES', 
		'HTTP_POST_FILES', '_REQUEST', 'ignoreList',
	);

	/************************************************************************** 
	 * The class constructor
	 *
	 * @param 	boolean $verbose	enable verbose comments
	 *************************************************************************/
	function __construct($verbose = FALSE) {
		$this->verbose = $verbose;
		if ($this->verbose) {
			fwrite(STDOUT, "$this->className class constructor set.\n");
		} //<-- end if -->
	} //<-- end function -->

	/************************************************************************** 
	 * Returns the extension of a file
	 *
	 * @param 	string 	$file 		a filename or the path to a file
	 * @return 	string	$ext		the file extension
	 * @throws 	Exception if $file is empty
	 *************************************************************************/
	public function getExtension($file) {
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
	 * Returns the ordinal suffix of a num, e.g., 1st, 2nd, 3rd.
	 *
	 * @param 	integer	$num a number
	 * @return 	string	$ext a number with the ordinal suffix
	 * @throws 	Exception if $file is empty
	 *************************************************************************/
	public function addOrdinal($num) {
		try {
			if (!in_array(($num % 100), array(11, 12, 13))){
				switch ($num % 10) {
					// Handle 1st, 2nd, 3rd
					case 1: return $num.'st';
					case 2: return $num.'nd';
					case 3: return $num.'rd';
				}
			}
			
			return $num.'th';
			
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.__CLASS__.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
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
	 * @throws 	Exception if $needle is invalid
	 *************************************************************************/
	public function arraySearchType($needle, $haystack, $n = 1) {
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
						$needleKeys[] = self::arraySearchType($needle, $value, $n);
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
	 * Writes data to a file 
	 * 
	 * @param 	string 	$content 	the data to write to the file 
	 * @param 	string 	$file 		the path to an empty or non existing file
	 * @return 	boolean	TRUE
	 * @throws 	Exception if $content is empty
	 * @throws 	Exception if $file exists as a non-empty file
	 *************************************************************************/
	public function write2File($content, $file) {
		if (empty($content)) { // check to make sure $content isn't empty
			throw new Exception('Empty content passedfrom '.__CLASS__.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} elseif (file_exists($file) && filesize($file) != 0) {
			throw new Exception('File .'.$file.' already exists from '.
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
	 * Returns csv data as an array
	 *
	 * @param 	string 	$csvFile		the path to a csv file 
	 * @param 	string 	$fieldDelimiter the csv field delimiter 
	 * @return 	array	$content		array of csv data
	 * @throws 	Exception if $csvFile does not exist
	 *************************************************************************/ 
	public function csv2Array($csvFile, $fieldDelimiter = ',') {		
		if (!file_exists($csvFile)) {
			throw new Exception('File '.$csvFile.' does not exist from '.
				__CLASS__.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$tempFile = self::makeLFLineEndings($csvFile);
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
	 * Reads input from STDIN
	 *
	 * @return 	string	$string	data read from STDIN
	 * @throws 	Exception if there is no input
	 *************************************************************************/ 
	public function readSTDIN() {
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
	 * Performs array_combine() on a multi-dimensional array using the first 
	 * element for the keys and the remaining elements as the values
	 *
	 * @param 	array 	$content	of the following form:
	 * 								$content = array(
	 *									array($key1, $key2, $key3), 
	 *									array($value1, $value2, $value3),
	 *									array($value4, $value5, $value6))
	 *
	 * @return 	array	$newContent	of the following form:	
	 * 								$content = array(
	 *								array($key1 => $key1, 
	 *									$key2 => $key2, 
	 *									$key3 => $key3),
	 * 								array($key1 => $value1, 
	 *									$key2 => $value2, 
	 *									$key3 => $value3),
	 *								array($key1 => $value4, 
	 *									$key2 => $value5, 
	 *									$key3 => $value6))
	 *
	 * @throws 	Exception if $content is not a multi-dimensional array
	 *************************************************************************/ 
	public function arrayInsertKey($content) {	
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
	 * Recursively returns all defined variables
	 *
	 * @param 	array 	$ignoreList 	the variables to ignore 
	 * @return 	array 	$definedVars	defined variables not in the ignore list
	 *************************************************************************/ 
	public function getVars($vars, $ignoreList = NULL) {
		try {
			if (empty($ignoreList)) {
				$ignoreList = $this->varIgnoreList;
			} //<-- end if -->
			
			foreach ($vars as $key => $val) {
				if (!in_array($key, $ignoreList) && !empty($val)) {
					if (is_array($val)) {
						$definedVars[$key] = self::getVars($val);
					} elseif (is_string($val)) { 
						$definedVars[$key] = $val;
					} //<-- end if -->
				} //<-- end if --> 
			} //<-- end foreach -->
			
			return $definedVars;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.__CLASS__.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->
	
	/************************************************************************** 
	 * Returns the filename without extension of a file
	 *
	 * @param 	string 	$file 		a filename or the path to a file
	 * @return 	string	$base		filename without extension
	 * @throws 	Exception if an empty value is passed
	 *************************************************************************/ 
	public function getBase($file) {
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
	 * Returns the full path to files in the current directory
	 *
	 * @param 	array 	$files 	a file in the current directory
	 * @return 	string	$base	filename without extension
	 * @throws 	Exception if $files is not an array 
	 *************************************************************************/ 
	public function getFullPath($files) {
		if (!is_array($files)) {
			throw new Exception('Please use an array from '.
				__CLASS__.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$dir = getcwd();
				
				foreach ($files as $key => $value) {
					if (strpos($value, '/') === FALSE) {
						$files[$key] = '"'.$dir.'/'.$value.'"';
					} //<-- end if -->
				} //<-- end foreach -->
				
				return $files;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.__CLASS__.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/************************************************************************** 
	 * Writes a contents of a given file to a new file with LF line endings
	 * 
	 * @param 	string 	$file 		a filename or the path to a file
	 * @return 	string	$tempFile	path to the temporary file created
	 * @throws 	Exception if $file does not exist
	 *************************************************************************/ 
	public function makeLFLineEndings($file) {
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
				self::write2File($string, $tempFile);
				return $tempFile;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.__CLASS__.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/************************************************************************** 
	 * Performs a number or date format on the elements of a given key in a 
	 * multi-dimensional array suitable for import into a sqlite database
	 *	 
	 * @param 	array 	$content	of the following form:
	 * 								$content = array(
	 *									array($key1 => $value1, 
	 *										$key2 => $value2, 
	 *										$key3 => $value3),
	 *									array($key1 => $value4, 
	 *										$key2 => $value5, 
	 *										$key3 => $value6))
	 *
	 * @param 	string 	$key		the key whose values you want to format
	 * @param 	string 	$format		the type of format to apply the (i.e. 
	 *								'number' or 'date')
	 *								
	 * @return 	array	$newContent	new array with formatted values	
	 * @throws 	Exception if $content is not a multi-dimensional array
	 * @throws 	Exception if $format is invalid
	 *************************************************************************/
	public function formatArray($content, $key, $format) {
		if (!is_array($content[0])) {
			throw new Exception('Please use a multi-dimensional array from '.
				__CLASS__.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
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
					$newContent[$i][$key] = $row;
					$i++;
				} //<-- end foreach -->
						
				return $newContent;
				} catch (Exception $e) { 
					throw new Exception($e->getMessage().' from '.__CLASS__.'->'.
						__FUNCTION__.'() line '.__LINE__
					);
				} //<-- end try -->
			} //<-- end if -->
		} //<-- end function -->
			
	/************************************************************************** 
	 * Recursively replaces all occurrences of $needle with $replace on 
	 * elements in an array
	 * 
	 * @param 	array 	$content	the array to perform the replacement on
	 *
	 * @param 	string 	$needle		the value being searched for (an array may 
	 *								be used to designate multiple needles)
	 * @param 	string 	$replace	the replacement value that replaces $needle 
	 *								(an array may be used to designate multiple 
	 *								replacements)
	 *								
	 * @return 	array	$newContent	new array with replaced values	
	 *************************************************************************/ 
	public function arraySubstitute($content, $needle, $replace) {
		try {
			foreach ($content as $haystack) {
				if (!is_array($haystack)) { // If it's not an array, sanitize it
					$newContent[] = str_replace($needle, $replace, $haystack);
				} else { // it IS an array, so recurse
					$newContent[] = self::arraySubstitute($haystack, 
						$needle, $replace
					);
				} //<-- end if -->
			} //<-- end foreach -->		
			
			// I think all I have to do is the following:
			// $newContent = str_replace($needle, $replace, $content);
			return $newContent;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.__CLASS__.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/************************************************************************** 
	 * Overwrites an array to a pre-existing csv file
	 * 
	 * @param 	string 	$content 		the data to write to the file 
	 * @param 	string 	$csvFile 		the path to a csv file 
	 * @param 	string 	$fieldDelimiter the csv field delimiter 
	 * @return 	boolean	TRUE
	 * @throws 	Exception if $csvFile does not exist
	 *************************************************************************/ 
	public function overwriteCSV($content, $csvFile, $fieldDelimiter = ',') {	
		if (!file_exists($csvFile)) {
			throw new Exception('File .'.$csvFile.' does not exsit from '.
				__CLASS__.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$tempFile = self::makeLFLineEndings($csvFile);
				$handle = fopen($tempFile, 'r');
				self::array2CSV($content, $tempFile, $fieldDelimiter);
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
	 * Writes an array to a csv file 
	 *
	 * @param 	string 	$content 		the data to write to the file 
	 * @param 	string 	$csvFile 		the path to an empty or non existing 
	 *									csv file
	 * @param 	string 	$fieldDelimiter the csv field delimiter 
	 * @return 	boolean	TRUE
	 * @throws 	Exception if $csvFile exists or is non-empty 
	 *************************************************************************/ 
	public function array2CSV($content, $csvFile, $fieldDelimiter = ',') {	
		if (file_exists($csvFile) && filesize($csvFile) != 0) {
			throw new Exception('File .'.$csvFile.' already exists from '.
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