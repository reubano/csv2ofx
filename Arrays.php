<?php
/**
 *******************************************************************************
 * purpose: contains general functions to be used by all programs
 ******************************************************************************/
class Arrays {
	protected $_className = __CLASS__;	// class name
	protected $_verbose;

	/**
	 ***************************************************************************
	 * The class constructor
	 *
	 * @param boolean $verbose enable verbose comments
	 *
	 **************************************************************************/
	public function __construct($verbose=false) {
		$this->_verbose = $verbose;

		if ($this->_verbose) {
			fwrite(STDOUT, "$this->_className class constructor set.\n");
		} //<-- end if -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Recursively searches an array for the nth occurance of a given value 
	 * type and returns the corresponding key if successful.
	 *
	 * @param string $needle   the type of element to find (i.e. 'numeric' 
	 *						   or 'string')
	 * @param array  $haystack the array to search
	 * @param int    $n 	   the nth element to find 
	 *
	 * @return array	array of the key(s) of the found element(s) 
	 * @throws Exception if it can't find enough elements
	 * @throws Exception if $needle is invalid
	 *
	 * @assert ('numeric', array('one', 2, 3)) == array(1)
	 * @assert ('numeric', array('one', 2, 3), 2) == array(2)
	 * @assert ('string', array(array('one', 2, 3), array(1, 'two', 3))) == array(1, 2)
	 **************************************************************************/
	public function arraySearchType($needle, $haystack, $n=1) {
		try {
			$i = 0; // needle element counter
			
			$main = function ($value, $key, $comparison) use (
				&$i, &$needleKeys, $needle, $n
			) {
				if ($i < $n) {
					if (!is_array($value)) { 
						if (call_user_func($comparison, $value)) {
							$i++;
							
							if ($i == $n) {
								$needleKeys[] = $key;
							}
						}
					} else { // it IS an array, so recurse
						$needleKeys[] = General::arraySearchType(
							$needle, $value, $n
						);
					} //<-- end if !is_array -->
				} //<-- end if -->
			}; //<-- end closure -->
						
			$numFormat = function ($value, $key) use ($main) {
				call_user_func($main, $value, $key, 'is_numeric');
			}; //<-- end closure -->
			
			$notNumFormat = function ($value, $key) use ($main) {
				call_user_func($main, $value, $key, '!is_numeric');
			}; //<-- end closure -->
							
			switch ($needle) {
				case 'numeric':
					array_walk($haystack, $main, 'is_numeric');
					break;
					
				case 'string':
					array_walk($haystack, $main, '!is_numeric');
					break;
					
				default:
					throw new Exception(
						'Wrong search type entered. Please type \'numeric\' or'.
						' \'string\'.'
					);
			} //<-- end switch -->
			
			return $needleKeys;
			
		} catch (Exception $e) { 
			throw new Exception(
				$e->getMessage().' from '.$this->_className.'->'.__FUNCTION__.
				'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->
	
	/**
	 ***************************************************************************
	 * Writes an array to a csv file
	 *
	 * @param string  $content		  the data to write to the file 
	 * @param string  $csvFile		  the file path
	 * @param string  $fieldDelimiter the csv field delimiter
	 * @param boolean $overWrite	  over write file if exists 
	 *
	 * @return boolean	true
	 * @throws Exception if $csvFile exists or is non-empty 
	 **************************************************************************/
	public function array2CSV(
		$content, $csvFile, $fieldDelimiter=',', $overWrite=false
	) {	
		if (file_exists($csvFile) && !$overWrite) {
			throw new Exception(
				'File '.$csvFile.' already exists from '.$this->_className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {	
				$handle = fopen($csvFile, 'w');
				// $count = count($content);
				array_walk($content, 'fputcsv', $handle, $fieldDelimiter);
				
				//array_map(
				//	'fputcsv',
				//	array_fill(0, $count, $handle),
				//	$content,
				//	array_fill(0, $count, $fieldDelimiter)
				//);
				
				if ($this->_verbose) {
					fwrite(STDOUT, "wrote $count lines to $csvFile!\n");
				} //<-- end if -->				
								
				return fclose($handle);
			} catch (Exception $e) { 
				throw new Exception(
					$e->getMessage().' from '.$this->_className.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Recursively replaces all occurrences of $needle with $replace on 
	 * elements in an array
	 * 
	 * @param array  $content the array to perform the replacement on
	 * @param string $needle  the value being searched for (an array may 
	 *						  be used to designate multiple needles)
	 * @param string $replace the replacement value that replaces $needle 
	 *						  (an array may be used to designate multiple 
	 *						  replacements)
	 *								
	 * @return array $newContent new array with replaced values	
	 *
	 * @assert (array('one', 'two', 'three'), 'two', 2) == array('one', 2, 'three')
	 **************************************************************************/
	public function arraySubstitute($content, $needle, $replace) {
		try {
			$strReplaceRec = function (&$haystack, $key) use (
				$needle, $replace
			) {
				str_replace($needle, $replace, $haystack);
			};
			
			array_walk_recursive($content, $strReplaceRec);	
			return $content;
		} catch (Exception $e) { 
			throw new Exception(
				$e->getMessage().' from '.$this->_className.'->'.__FUNCTION__.
				'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Move a given element to the beginning of an array (by reference)
	 * 
	 * @param array  &$content the array to perform the move on
	 * @param string $key 	   the key of the element to move 
	 *
	 * @return array $content  the moved array
	 *
	 * @assert (array('one', 'two', 'three'), 'two', 2) == array('one', 2, 'three')
	 **************************************************************************/
	public function arrayMoveBr(&$content, $key) {
		if (!array_key_exists($key, $content)) {
			throw new Exception(
				'Key '.$key.' not found from '.$this->_className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$append = $content[$key];
				array_splice($content, $key, 1);
				return array_unshift($content, $append);
			} catch (Exception $e) { 
				throw new Exception(
					$e->getMessage().' from '.$this->_className.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->			

	/**
	 ***************************************************************************
	 * Sort a multidimensional array (by reference) by the value of a given subkey
	 * 
	 * @param array  &$array the array to sort
	 * @param string $key	 the subkey to sort by 
	 *
	 * @return array $content the sorted array	
	 **************************************************************************/
	public function arraySortBySubValueBr(&$array, $key) {
		if (!array_key_exists($key, current($array))) {
			throw new Exception(
				'Key \''.$key.'\' not found from '.__CLASS__.'->'.__FUNCTION__.
				'() line '.__LINE__
			);
		} else {
			try {
				$cmp = function (array $a, array $b) use ($key) {
					return strcmp($a[$key], $b[$key]);
				};
				
				return usort($array, $cmp);
			} catch (Exception $e) { 
				throw new Exception(
					$e->getMessage().' from '.$this->_className.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->			
	/**
	 ***************************************************************************
	 * Creates an array by using one array for keys and another for its values
	 * Truncates/fills values if the number of elements for each array isn't 
	 * equal. 
	 *
	 * @param array $keys	the keys
	 * @param array $values	the values
	 *
	 * @return array $combinedArray	combined array
	 * @throws Exception if there is no input
	 *
	 * @assert (array(1, 2, 3), array(2, 3, 4, 5)) == array(1 => 2, 2 => 3, 3 => 4)
	 **************************************************************************/
	public function arraySafeCombine($keys, $values) { 
		try {
			$combinedArray = array(); 
			$keyCount = count($keys);
			$valueCount = count($values);
			$difference = $keyCount - $valueCount;
			
			if ($difference > 0) {
				$values = array_pad($values, $difference, 0);
			} else {
				$values = array_slice($values, 0, $keyCount, true);
			}
			
			return array_combine($keys, $values);
		} catch (Exception $e) { 
			throw new Exception(
				$e->getMessage().' from '.$this->_className.'->'.__FUNCTION__.
				'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Case insensitive array search. 
	 *
	 * @param mixed $needle	  the value to search for
	 * @param array $haystack the array to search
	 *
	 * @return string $string true/false
	 * @throws Exception if there is no input
	 *
	 * @assert ('Two', array('one', 'two', 'three')) == true
	 **************************************************************************/
	public function inArray($needle, $haystack) {
		try {
			return in_array(
				strtolower($needle), array_map('strtolower', $haystack)
			);
		} catch (Exception $e) { 
			throw new Exception(
				$e->getMessage().' from '.$this->_className.'->'.__FUNCTION__.
				'() line '.__LINE__
			);
		} //<-- end try -->
	}

	/**
	 ***************************************************************************
	 * Hashes the contents of an array (by reference)
	 *
	 * @param array  &$content the array containing the content to hash
	 * @param string $hashKey  the key of the element to hash
	 * @param string $algo	   the hashing algorithm to use
	 *
	 * @return array $content  the hashed array
	 *
	 * supported algorithms:
	 * adler32; crc32; crc32b; gost; haval128,3; haval128,4; haval128,5; 
	 * haval160,3; haval160,4; haval160,5; haval192,3; haval192,4; haval192,5; 
	 * haval224,3; haval224,4; haval224,5; haval256,3; haval256,4; haval256,5; 
	 * md2; md4; md5; ripemd128; ripemd160; ripemd256; ripemd320; sha1; sha256; 
	 * sha384; sha512; snefru; tiger128,3; tiger128,4; tiger160,3; tiger160,4; 
	 * tiger192,3; tiger192,4; whirlpool
	 * 
	 * @throws Exception if $hashKey does not exist
	 **************************************************************************/
	public function arrayHashBr(&$content, $hashKey, $algo = 'md5') {
		if (!array_key_exists($hashKey, current($content))) {
			throw new Exception(
				'Key \''.$hashKey.'\' not found from '.$this->_className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$hash = function (&$value, $key) use ($hashKey, $algo) {
					if ($key == $hashKey) {
						$value = hash($algo, $value);
					}
				};
				
				array_walk_recursive($content, $hash);
				return $content;
			} catch (Exception $e) { 
				throw new Exception(
					$e->getMessage().' from '.$this->_className.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->
	
	/**
	 ***************************************************************************
	 * Delete elements of a multidimensional array (by reference) if all the 
	 * sub-arrays are empty
	 *
	 * @param array &$content multi-dimensional array
	 *
	 * @return array $content  the trimmed array
	 * @throws Exception if $content is not a multi-dimensional array
	 **************************************************************************/
	public function arrayTrimBr(&$content) {
		if (!is_array(current($content))) {
			throw new Exception(
				'Please use a multi-dimensional array'.'from '.
				$this->_className.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$rednull = function ($a, $b) {		
					return(!empty($a) && !empty($b));
				};
				
				$notAllnull = function ($content) {
					return array_reduce($content, $rednull);
				};
	
				return array_filter($content, $notAllnull);
			} catch (Exception $e) { 
				throw new Exception(
					$e->getMessage().' from '.$this->_className.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Adds elements to a multidimensional array (by reference) so that each 
	 * sub-array is as long as the first sub-array
	 *
	 * @param array &$content multi-dimensional array
	 *
	 * @return array $content  the lengthed array
	 * @throws Exception if $content is not a multi-dimensional array
	 **************************************************************************/
	public function arrayLengthenBr(&$content) {
		if (!is_array(current($content))) {
			throw new Exception(
				'Please use a multi-dimensional array'.'from '.
				$this->_className.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {				
				$count = count(current($content));
				
				$lengthen = function ($item) use ($count) {
					$num = $count - count($item);
					
					if ($num > 0) {
						for ($i = 0; $i < $num; $i++) {
							array_push($item, '');
						} //<-- end for -->
					}
				};
				
				return array_map($lengthen, $content);
				
			} catch (Exception $e) { 
				throw new Exception(
					$e->getMessage().' from '.$this->_className.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->
	
	/**
	 ***************************************************************************
	 * Performs array_combine() on a multi-dimensional array using the first 
	 * element for the keys and the remaining elements as the values
	 *
	 * @param array $content of the following form:
	 * 							$content = array(
	 *								array($key1, $key2, $key3), 
	 *								array($value1, $value2, $value3),
	 *								array($value4, $value5, $value6))
	 *
	 * @return array $newContent of the following form:	
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
	 * @throws Exception if $content is not a multi-dimensional array
	 *
	 * @assert(array(array('key1', 'key2', 'key3'), array('value1', 'value2', 'value3'), array('value4', 'value5', 'value6'))) == array(array('key1' => 'key1', 'key2' => 'key2', 'key3' => 'key3'), array('key1' => 'value1', 'key2' => 'value2', 'key3' => 'value3'), array('key1' => 'value4', 'key2' => 'value5', 'key3' => 'value6'))
	 **************************************************************************/
	public function arrayInsertKey($content) {
		if (!is_array(current($content))) {
			throw new Exception(
				'Please use a multi-dimensional array'.'from '.
				$this->_className.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {				
				$maxValues = count(current($content));
				$keys = $content[0]; // get key names
				
				$checkSize = function ($values, $key) use ($maxValues) {
					if (count($values) != $maxValues) {
						throw new Exception('Array '.$key.' is wrong size');
					}
				};
				
				$combine = function ($values) use ($keys) {
					$values = array_combine($keys, $values);
				};
				
				array_walk($content, $checkSize);				
				return array_map($combine, $content);	
			} catch (Exception $e) { 
				throw new Exception(
					$e->getMessage().' from '.$this->_className.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->
	
	/**
	 ***************************************************************************
	 * Performs a number or date format on the elements of a given key in a 
	 * multi-dimensional array (by reference) for import into a sqlite database
	 *	 
	 * @param array  &$content	the array to format
	 * @param string $formatKey	the key whose values you want to format
	 * @param string $format	the type of format to apply the (i.e. 'number' 
	 *							or 'date')
	 *								
	 * @return array $content  the formatted array
	 * @throws Exception if $content is not a multi-dimensional array
	 * @throws Exception if $format is invalid
	 *
	 * @assert(array(array('key1' => '1/1/12'), array('key1' => '2/1/12'), 'key1', 'date') == array(array('key1' => '2012-01-01'), array('key1' => '2012-02-01')
	 **************************************************************************/
	public function arrayFormatBr(&$content, $formatKey, $format) {
		if (!is_array(current($content))) {
			throw new Exception(
				'Please use a multi-dimensional array from '.$this->_className.
				'->'.__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$numFormat = function (&$number, $key) use ($formatKey) {
					if ($key == $formatKey) {
						$number = str_replace(',', '', $number) + 0;
						$number = number_format($number, 2, '.', '');
					}
				};
				
				$dateFormat = function (&$date, $key) use ($formatKey) {
					if ($key == $formatKey) {
						$date = date("Y-m-d", strtotime($date));
					}
				};
								
				switch ($format) {
					case 'number':
						array_walk_recursive($content, $numFormat);
						break;
						
					case 'date':
						array_walk_recursive($content, $dateFormat);
						break;
						
					default:
						throw new Exception(
							'Wrong format entered. Please type'.' \'number\' '.
							'or \'date\'.'
						);
				} //<-- end switch -->
				
				return $content;
			} catch (Exception $e) { 
				throw new Exception(
					$e->getMessage().' from '.$this->_className.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->
} //<-- end Array class -->
