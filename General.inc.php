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
	 * Recursively replaces all NULL elements with 0 in an array (by reference)
	 * if a following element is non-null
	 * @param 	array 	$content	the array to perform the replacement on
	 * @param 	string 	$replace	the replacement value that replaces $needle
	 *								(an array may be used to designate multiple
	 *								replacements)
	 **************************************************************************/
	public function arrayFillMissing(&$content) {
		try {
			$count = count($content);
			$keys = array_keys($content);

			for ($i = 0; $i < $count; $i++) {
				$currkey = $keys[$i];

				// If it's not an array, continue checking
				if (!is_array($content[$currkey])) {
					if (is_null($content[$currkey])) {
						if ($i != 0 && $i != $count - 1) {
							$prevkey = $keys[$i - 1];
							$nextkey = $keys[$i + 1];

							if (!is_null($content[$nextkey])) {
								$content[$currkey] = 0;
							} //<-- end if -->

							if (!is_null($content[$prevkey])) {
								$pass = FALSE;

								for ($j = $i; $j < $count; $j++) {
									// check to see if there is at least one
									// additional non-null value following
									if (!is_null($content[$keys[$j]])) {
										$pass = TRUE;
										break;
									} //<-- end if -->
								} //<-- end for -->

								if ($pass) {
									$content[$currkey] = 0;
								} else {
									// no more non-null values so exit loop
									break;
								} //<-- end if -->
							} //<-- end if -->
						} //<-- end if -->
					} //<-- end if -->
				} else { // it IS an array, so recurse
					self::arrayFillMissing($content[$currkey]);
				} //<-- end if -->
			} //<-- end foreach -->
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/***************************************************************************
	 * Recursively replaces all NULLs with $replace in an array (by reference)
	 * @param 	array 	$content	the array to perform the replacement on
	 * @param 	string 	$replace	the replacement value that replaces $needle
	 *								(an array may be used to designate multiple
	 *								replacements)
	 **************************************************************************/
	public function arrayReplaceNull(&$content, $replace) {
		try {
			foreach ($content as &$haystack) {
				// If it's not an array, replace it
				if (!is_array($haystack)) {
					if (is_null($haystack)) {
						$haystack = $replace;
					} //<-- end if -->
				} else { // it IS an array, so recurse
					self::arrayReplaceNull($haystack, $replace);
				} //<-- end if -->
			} //<-- end foreach -->
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->


	/***************************************************************************
	 * A date function supporting the microseconds.
	 *
	 * @param 	string	$format 		time format
	 * @param 	integer	$uTimeStamp 	time (defaults to the value of time())
	 * @return 	string	$newTimestamp 	time with microseconds
	 **************************************************************************/
	public function udate($format, $uTimeStamp = NULL) {
		try {
			if (is_null($uTimeStamp)) {
				$uTimeStamp = microtime(true);
			}

			$timeStamp = floor($uTimeStamp);
			$milliSeconds = round(($uTimeStamp - $timeStamp) * 1000000);
			$newTimestamp = date(preg_replace('`(?<!\\\\)u`', $milliSeconds,
				$format), $timeStamp
			);

			return $newTimestamp;
		} catch (Exception $e) {
			throw new Exception($e->getMessage().' from '.$this->className
				.'->'.__FUNCTION__.'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/***************************************************************************
	 * Returns the first set of completely non-null sub-arrays or the first
	 * sub-array if none are non-null
	 *
	 * @param 	array 	$content	multi-dimensional array
	 * @throws 	Exception if $content is not a multi-dimensional array
	 **************************************************************************/
	public function getNonNull($content) {
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
					$lastkey = array_pop(array_keys($content[$i]));

					foreach ($content[$i] as $subKey => $subValue) {

						if (is_null($subValue)) {
							continue 2; // go to next array
						}

						if ($subKey == $lastkey) {
							return $content[$i];
						}
					} //<-- end foreach -->

					return $content[0];
				} //<-- end foreach -->

			} catch (Exception $e) {
				throw new Exception($e->getMessage().' from '.$this->className
					.'->'.__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->
} //<-- end class -->
?>
