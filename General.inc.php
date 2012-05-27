<?php
/*******************************************************************************
 * purpose: contains general functions to be used by all programs
 ******************************************************************************/

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

	/*************************************************************************** 
	 * The class constructor
	 *
	 * @param 	boolean $verbose	enable verbose comments
	 **************************************************************************/
	public function __construct($verbose = FALSE) {
		$this->verbose = $verbose;

		if ($this->verbose) {
			fwrite(STDOUT, "$this->className class constructor set.\n");
		} //<-- end if -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Returns the extension of a file
	 *
	 * @param 	string 	$file 		a filename or the path to a file
	 * @return 	string	$ext		the file extension
	 * @throws 	Exception if $file is empty
	 **************************************************************************/
	public function getExtension($file) {
		if (empty($file)) {
			throw new Exception('Empty file passed from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$ext = pathinfo($file, PATHINFO_EXTENSION);
				return $ext;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.$this->className
					.'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Returns the ordinal suffix of a num, e.g., 1st, 2nd, 3rd.
	 *
	 * @param 	integer	$num a number
	 * @return 	string	$ext a number with the ordinal suffix
	 * @throws 	Exception if $file is empty
	 **************************************************************************/
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
				throw new Exception($e->getMessage().' from '.$this->className
					.'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
	} //<-- end function -->

	/*************************************************************************** 
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
	 **************************************************************************/
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
								throw new Exception('Wrong search type '. 
									'entered. Please type \'numeric\' or '.
									'\'string\'.'
								);
						} //<-- end switch -->
					} else { // it IS an array, so recurse
						$needleKeys[] = self::arraySearchType(
							$needle, $value, $n
						);
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
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->
	
	/*************************************************************************** 
	 * Writes data to a file 
	 * 
	 * @param 	string 	$content 	the data to write to the file 
	 * @param 	string 	$file 		the path to an empty or non existing file
	 * @return 	boolean	TRUE
	 * @throws 	Exception if $content is empty
	 * @throws 	Exception if $file exists as a non-empty file
	 **************************************************************************/
	public function write2File($content, $file) {
		if (empty($content)) { // check to make sure $content isn't empty
			throw new Exception('Empty content passed from '.$this->className.
				'->'.__FUNCTION__.'() line '.__LINE__
			);
		} elseif (file_exists($file) && filesize($file) != 0) {
			throw new Exception('File '.$file.' already exists from '.
				$this->className.'->'.__FUNCTION__.'() line '.__LINE__
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
				throw new Exception($e->getMessage().' from '.$this->className
					.'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Writes data to a file (overwrites file if it exists)
	 * 
	 * @param 	string 	$content 	the data to write to the file 
	 * @param 	string 	$file 		the path to a file 
	 * @return 	boolean	TRUE
	 **************************************************************************/
	public function overwriteFile($content, $file) {	
		try {
			if (!file_exists($file)) {
				self::write2File($content, $file);
			} else {
				$tempFile = tempnam('/tmp', __FUNCTION__.'.');
				$handle = fopen($tempFile, 'r');
				self::write2File($content, $tempFile);
				copy($tempFile, $file);				
				fclose($handle);
				unlink($tempFile);
			} //<-- end if -->
			
			return TRUE;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className
				.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->		
	} //<-- end function -->

	/*************************************************************************** 
	 * Returns an array from csv data
	 *
	 * @param 	string 	$csvContent		csv text or path to a csv file 
	 * @param 	boolean	$file 			is $csvContent a file path?
	 * @param 	string 	$fieldDelimiter the csv field delimiter 
	 * @return 	array	$content		array of csv data
	 * @throws 	Exception if $csvFile does not exist
	 **************************************************************************/
	public function csv2Array($csvContent, $fieldDelimiter = ',', $file = TRUE){
		try {
			if ($file) {
				$csvFile = $csvContent;
			
				if (!file_exists($csvFile)) {
					throw new Exception('File '.$csvFile.' does not exist'.
						' from '.$this->className.'->'.__FUNCTION__.'() line '.
						__LINE__
					);
				}
				
				$tempFile = self::makeLFLineEndings($csvFile);
				$handle = fopen($tempFile, 'r');
				unlink($tempFile);
			} else { // not a file
				$csvContent = self::lines2Array($csvContent);
			} //<-- end if -->
			
			if ($file) {	
				while (($data = fgetcsv($handle, 1000, $fieldDelimiter)) 
					!== FALSE)
				{
					$content[] = $data;
				} //<-- end while -->
				
				fclose($handle);
			} else { // not a file
				foreach ($csvContent as $data) {
					$content[] = str_getcsv($data, $fieldDelimiter);
				} //<-- end while -->
			} //<-- end if -->
			
			return $content;			
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className
				.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Converts an array to string while adding and extra string to beginning
	 * and end of each element
	 *
	 * @param 	array 	$content	array to convert 
	 * @param 	string 	$extra		string to add to the beginning and end of 
	 *								each array element
	 * @param 	string 	$delimiter	character to seperate each arrayelement 
	 * @return 	string	$content	content formatted on 1 line with the extra
	 *								string added to the beginning and end of
	 *								each array element
	 * @throws 	Exception if $content is not an array 
	 **************************************************************************/
	public function extraImplode($content, $extra = '\'', $delimiter = ' ') {		
		if (!is_array($content)) {
			throw new Exception('Please use an array from '.
				$this->className.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$content = $extra.implode($extra.$delimiter.$extra, $content).
					$extra; // array to string	
				return $content;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.$this->className
					.'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Returns an array from a multiline string
	 *
	 * @param 	string 	$content	a multiline string 
	 * @return 	array	$content	array (one element from each line in the
	 *								string)
	 **************************************************************************/
	public function lines2Array($content) {		
		try {
			$content = str_replace("\r\n", "\n", $content);
			$content = str_replace("\r", "\n", $content);
			$content = explode("\n", $content); // turn string to array
			array_pop($content); // remove last element since it is empty
			return $content;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Reads input from STDIN
	 *
	 * @return 	string	$string	data read from STDIN
	 * @throws 	Exception if there is no input
	 **************************************************************************/
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
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Creates an array by using one array for keys and another for its values
	 * Truncates/fills values if the number of elements for each array isn't 
	 * equal. 
	 *
	 * @param 	array 	$keys	the keys
	 * @param 	array 	$values	the values
	 * @return 	string	$string	data read from STDIN
	 * @throws 	Exception if there is no input
	 **************************************************************************/
	public function safeArrayCombine($keys, $values) { 
		try {
			$combinedArray = array(); 
			$keyCount = count($keys);
			$valueCount = count($values);
		    $difference = $keyCount - $valueCount;
		    
		    if ($difference > 0) {
		    	for ($i = 0; $i < $difference; $i++) {
					$values[] = $values[$valueCount - 1];
		    	}
			}
			
			for ($i=0, $keyCount; $i < $keyCount; $i++) {
				$combinedArray[$keys[$i]] = $values[$i];
			} 
		        
			return $combinedArray;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Case insensitive array search. 
	 *
	 * @param 	mixed 	$needle		the searched value
	 * @param 	array 	$haystack	the array to search
	 * @return 	string	$string		TRUE/FALSE
	 * @throws 	Exception if there is no input
	 **************************************************************************/
	public function in_arrayi($needle, $haystack) {
        return in_array(strtolower($needle), 
        	array_map('strtolower', $haystack)
        );
    }

	/*************************************************************************** 
	 * Hashes the contents of an array
	 *
	 * @param 	array 	$content	the array containing the content to hash
	 * @param 	string 	$hashKey	the key of the element to hash
	 * @param 	string 	$algo		the hashing algorithm to use
	 *
	 * supported algorithms:
	 * adler32; crc32; crc32b; gost; haval128,3; haval128,4; haval128,5; 
	 * haval160,3; haval160,4; haval160,5; haval192,3; haval192,4; haval192,5; 
	 * haval224,3; haval224,4; haval224,5; haval256,3; haval256,4; haval256,5; 
	 * md2; md4; md5; ripemd128; ripemd160; ripemd256; ripemd320; sha1; sha256; 
	 * sha384; sha512; snefru; tiger128,3; tiger128,4; tiger160,3; tiger160,4; 
	 * tiger192,3; tiger192,4; whirlpool
	 * 
	 * @throws 	Exception if $hashKey does not exist
	 **************************************************************************/
	public function hashArray(&$content, $hashKey, $algo = 'md5') {
		if(!array_key_exists($hashKey, current($content))) {
			throw new Exception('Key \''.$hashKey.'\' not found from '.
				$this->className.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				foreach ($content as $key => $value) {
					$content[$key][$hashKey] = hash($algo, $value[$hashKey]);
				}
		
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.$this->className.
					'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Delete elements of a multidimensional array all all the sub-arrays are
	 * empty
	 *
	 * @param 	array 	$content	multi-dimensional array
	 * @throws 	Exception if $content is not a multi-dimensional array
	 **************************************************************************/
	public function trimArray(&$content) {
		if (!is_array(current($content))) {
			throw new Exception('Please use a multi-dimensional array'.
				'from '.$this->className.'->'.__FUNCTION__.'() line '.
				__LINE__
			);
		} else {
			try {			
				// loop through each array
				$count = count($content);
				
				for ($i = 0; $i < $count; $i++) {
					$last = count($content[$i]) - 1;
					
					foreach ($content[$i] as $subKey => $subValue) {
						if (!empty($subValue)) {
							continue 2; // go to next array
						}
						
						if ($subKey == $last) {
							array_splice($content, $i, 1);
							$i--;
							$count--;
						}
					} //<-- end foreach -->
				} //<-- end foreach -->
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.$this->className
					.'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Adds elements to a multidimensional array so that each sub-array is as
	 * long as the first sub-array
	 *
	 * @param 	array 	$content	multi-dimensional array
	 * @throws 	Exception if $content is not a multi-dimensional array
	 **************************************************************************/
	public function lengthenArray(&$content) {
		if (!is_array(current($content))) {
			throw new Exception('Please use a multi-dimensional array'.
				'from '.$this->className.'->'.__FUNCTION__.'() line '.
				__LINE__
			);
		} else {
			try {				
				$count = count(current($content));
				
				// loop through each array
				foreach ($content as $key => $values) {				
					$num = $count - count($values);
					
					if ($num > 0) { // check that arrays are same size
						for ($i = 0; $i < $num; $i++) {
							array_push($content[$key], '');
						} //<-- end for -->
					} //<-- end if -->
				} //<-- end foreach -->
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.$this->className
					.'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->
	
	/*************************************************************************** 
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
	 **************************************************************************/
	public function arrayInsertKey($content) {
		if (!is_array(current($content))) {
			throw new Exception('Please use a multi-dimensional array'.
				'from '.$this->className.'->'.__FUNCTION__.'() line '.
				__LINE__
			);
		} else {
			try {				
				$maxElements = count($content);
				$maxValues = count(current($content));
				
				// loop through each array
				foreach ($content as $key => $values) {				
					// check that arrays are same size
					if (count($values) != $maxValues) { 
						throw new Exception('Array '.$key.' is wrong size');
					} //<-- end if -->
				} //<-- end for -->
				
				$keys = $content[0]; // get key names
				
				// loop through each array
				foreach ($content as $values) { 
					$newContent[] = array_combine($keys, $values);
				} //<-- end for loop through each array -->
				
				return $newContent;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.$this->className
					.'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->
	
	/*************************************************************************** 
	 * Recursively returns all defined variables
	 *
	 * @param 	array 	$ignoreList 	the variables to ignore 
	 * @return 	array 	$definedVars	defined variables not in the ignore list
	 **************************************************************************/
	public function getVars($vars, $ignoreList = NULL) {
		try {
			if (empty($ignoreList)) {
				$ignoreList = $this->varIgnoreList;
			} //<-- end if -->
			
			foreach ($vars as $key => $val) {
				if ($key === 0 
					|| (!in_array($key, $ignoreList)) 
					&& !is_null($val)
				) {
					if (is_array($val)) {
						$definedVars[$key] = self::getVars($val);
					} elseif (is_string($val) || is_numeric($val)) { 
						$definedVars[$key] = $val;
					} //<-- end if -->
				} //<-- end if --> 
			} //<-- end foreach -->
			
			return $definedVars;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->
	
	/*************************************************************************** 
	 * Returns the filename without extension of a file
	 *
	 * @param 	string 	$file 	a filename or the path to a file
	 * @return 	string	$base	filename without extension
	 * @throws 	Exception if an empty value is passed
	 **************************************************************************/
	public function getBase($file) {
		if (empty($file)) {
			throw new Exception('Empty file passed from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$base = pathinfo($file, PATHINFO_FILENAME);
				return $base;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.$this->className
					.'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Returns the full path to files in the current directory
	 *
	 * @param 	array 	$files 	a file in the current directory
	 * @return 	string	$base	filename without extension
	 * @throws 	Exception if $files is not an array 
	 **************************************************************************/
	public function getFullPath($files) {
		if (!is_array($files)) {
			throw new Exception('Please use an array from '.
				$this->className.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$dir = getcwd();
				
				foreach ($files as $key => $value) {
					if (strpos($value, '/') === FALSE) {
						$files[$key] = $dir.'/'.$value;
					} //<-- end if -->
				} //<-- end foreach -->
				
				return $files;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.$this->className
					.'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Reads the contents of a given file
	 * 
	 * @param 	string 	$file 		a filename or the path to a file
	 * @return 	string	$content	the file contents
	 * @throws 	Exception if $file does not exist
	 **************************************************************************/
	public function readFile($file) {
		if (!file_exists($file)) {
			throw new Exception('File '.$file.' does not exist from '.
				$this->className.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$handle 	= fopen($file, 'r');
				$string 	= NULL;
				
				while (!feof($handle)) {
					$string .= fgets($handle, 1024);
				} //<-- end while -->
				
				fclose($handle);
				return $string;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.$this->className
					.'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Writes a contents of a given file to a new file with LF line endings
	 * 
	 * @param 	string 	$file 		a filename or the path to a file
	 * @return 	string	$tempFile	path to the temporary file created
	 * @throws 	Exception if $file does not exist
	 **************************************************************************/
	public function makeLFLineEndings($file) {
		if (!file_exists($file)) {
			throw new Exception('File '.$file.' does not exist from '.
				$this->className.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$tempFile	= tempnam('/tmp', __FUNCTION__.'.');
				$string 	= self::readFile($file);
				$string 	= str_replace("\r\n", "\n", $string);
				$string 	= str_replace("\r", "\n", $string);
				self::write2File($string, $tempFile);
				return $tempFile;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.$this->className
					.'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/*************************************************************************** 
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
	 * @param 	string 	$formatKey	the key whose values you want to format
	 * @param 	string 	$format		the type of format to apply the (i.e. 
	 *								'number' or 'date')
	 *								
	 * @throws 	Exception if $content is not a multi-dimensional array
	 * @throws 	Exception if $format is invalid
	 **************************************************************************/
	public function formatArray(&$content, $formatKey, $format) {
		if (!is_array(current($content))) {
			throw new Exception('Please use a multi-dimensional array from '.
				$this->className.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				switch ($format){
					case 'number':
						foreach ($content as $key => $row) {
							$number = $row[$formatKey];
							$number = str_replace(',', '', $number) + 0;
							$number = number_format($number, 2, '.', '');
							$content[$key][$formatKey] = $number;
						} //<-- end foreach -->
					
						break;
						
					case 'date':
						foreach ($content as $key => $row) {
							$date = $row[$formatKey];
							// format to yyyy-mm-dd
							$date = date("Y-m-d", strtotime($date));
							$content[$key][$formatKey] = $date;
						} //<-- end foreach -->
						
						break;
						
					default:
						throw new Exception('Wrong format entered. Please type'.
							' \'number\' or \'date\'.'
						);
				} //<-- end switch -->
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '
					.$this->className.'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/*************************************************************************** 
	 * Sort a multidimensional array by the value of a given subkey
	 * 
	 * @param 	array 	$array	the array to sort
	 * @param 	string 	$key	the subkey to sort by 
	 * @return 	array	$content	new array with moved values	
	 **************************************************************************/
	public function arraySortBySubValue(&$array, $key) {
		if(!array_key_exists($key, current($array))) {
			throw new Exception('Key \''.$key.'\' not found from '.
				__CLASS__.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$cmp = function (array $a, array $b) use ($key) {
			    	return strcmp($a[$key], $b[$key]);
				};
				
			    usort($array, $cmp);
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.$this->className
					.'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->			

	/*************************************************************************** 
	 * Move a given element to the beginning of an array 
	 * 
	 * @param 	array 	$array	the array to perform the move on
	 * @param 	string 	$key	the the key of the element to move 
	 **************************************************************************/
	public function arrayMove(&$array, $key) {
		if(!array_key_exists($key, $array)) {
			throw new Exception('Key '.$key.' not found from '.
				$this->className.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$append = $array[$key];
				array_splice($array, $key, 1);
				array_unshift($array, $append);
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.$this->className
					.'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->			

	/*************************************************************************** 
	 * Recursively replaces all occurrences of $needle with $replace on 
	 * elements in an array (by reference)
	 * 
	 * @param 	array 	$content	the array to perform the replacement on
	 * @param 	string 	$needle		the value being searched for (an array may 
	 *								be used to designate multiple needles)
	 * @param 	string 	$replace	the replacement value that replaces $needle 
	 *								(an array may be used to designate multiple 
	 *								replacements)
	 **************************************************************************/
	public function arraySubstituteBr(&$content, $needle, $replace) {	
		try {
			foreach ($content as &$haystack) {
				if (!is_array($haystack)) { // If it's not an array, sanitize it
					$haystack = str_replace($needle, $replace, $haystack);
				} else { // it IS an array, so recurse
					self::arraySubstituteBr($haystack, $needle, $replace);
				} //<-- end if -->
			} //<-- end foreach -->	
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->
			
	/*************************************************************************** 
	 * Recursively replaces all occurrences of $needle with $replace on 
	 * elements in an array
	 * 
	 * @param 	array 	$content	the array to perform the replacement on
	 * @param 	string 	$needle		the value being searched for (an array may 
	 *								be used to designate multiple needles)
	 * @param 	string 	$replace	the replacement value that replaces $needle 
	 *								(an array may be used to designate multiple 
	 *								replacements)
	 *								
	 * @return 	array	$newContent	new array with replaced values	
	 **************************************************************************/
	public function arraySubstitute($content, $needle, $replace) {
		try {
			foreach ($content as $haystack) {				
				if (!is_array($haystack)) { // If it's not an array, sanitize it
					$newContent[] = str_replace($needle, $replace, $haystack);
				} else { // it IS an array, so recurse
					$newContent[] = self::arraySubstitute($haystack, 
						$needle, $replace);
				} //<-- end if -->
			} //<-- end foreach -->		
			
			return $newContent;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->
	
	/*************************************************************************** 
	 * Converts data to xml compliant input
	 * 
	 * @param 	string 	$content the content to clean 
	 * @return 	string 	$content the cleaned content
	 * @throws 	Exception if $content is empty
	 **************************************************************************/
	public function xmlize($content) {
		if (empty($content)) { // check to make sure $content isn't empty
			throw new Exception('Empty value passed from '.
				$this->className.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$invalid_text = array('&', '<', '>', '\r\n', '\n');
				$valid_text = array('&amp;', '&lt;', '&gt;', ' ', ' ');
				$content = str_replace($invalid_text, $valid_text, $content);
				return $content;
			} catch (Exception $e) { 
				throw new Exception($e->getMessage().' from '.$this->className.
					'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->
	
	/*************************************************************************** 
	 * Writes an array to a csv file (overwrites file if it exists)
	 * 
	 * @param 	string 	$content 		the data to write to the file 
	 * @param 	string 	$csvFile 		the path to a csv file 
	 * @param 	string 	$fieldDelimiter the csv field delimiter 
	 * @return 	boolean	TRUE
	 **************************************************************************/
	public function overwriteCSV($content, $csvFile, $fieldDelimiter = ',') {	
		try {
			if (!file_exists($csvFile)) {
				self::array2CSV($content, $csvFile, $fieldDelimiter);
			} else {
				//$tempFile = self::makeLFLineEndings($csvFile);
				$tempFile = tempnam('/tmp', __FUNCTION__.'.');
				$handle = fopen($tempFile, 'r');
				self::array2CSV($content, $tempFile, $fieldDelimiter);
				copy($tempFile, $csvFile);				
				fclose($handle);
				unlink($tempFile);
			} //<-- end if -->
			
			return TRUE;
		} catch (Exception $e) { 
			throw new Exception($e->getMessage().' from '.$this->className
				.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->		
	} //<-- end function -->
			
	/*************************************************************************** 
	 * Writes an array to a csv file
	 *
	 * @param 	string 	$content 		the data to write to the file 
	 * @param 	string 	$fieldDelimiter the csv field delimiter 
	 * @param 	string 	$csvFile 		the path to an empty or non existing 
	 *									csv file
	 * @return 	boolean	TRUE
	 * @throws 	Exception if $csvFile exists or is non-empty 
	 **************************************************************************/
	public function array2CSV($content, $csvFile, $fieldDelimiter = ',') {	
		if (file_exists($csvFile) && filesize($csvFile) != 0) {
			throw new Exception('File '.$csvFile.' already exists from '.
				$this->className.'->'.__FUNCTION__.'() line '.__LINE__
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
				throw new Exception($e->getMessage().' from '.$this->className
					.'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->
} //<-- end class -->
?>