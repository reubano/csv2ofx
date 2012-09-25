<?php
/**
 *******************************************************************************
 * purpose: contains general functions to be used by all programs
 ******************************************************************************/
class Vars {
	protected $_className = __CLASS__;	// class name
	protected $_verbose;
	protected $_fileIgnoreList = array('.', '..', '.DS_Store','.svn','.git*');
	protected $_varIgnoreList = array(
		'HTTP_POST_VARS', 'HTTP_GET_VARS', 'HTTP_COOKIE_VARS', 
		'HTTP_SERVER_VARS', 'HTTP_ENV_VARS', 'HTTP_SESSION_VARS', '_ENV', 
		'PHPSESSID','SESS_DBUSER', 'SESS_DBPASS','HTTP_COOKIE', 'GLOBALS', 
		'_ENV', 'HTTP_ENV_VARS', 'argv', 'argc', '_POST', 'HTTP_POST_VARS', 
		'_GET', 'HTTP_GET_VARS', '_COOKIE', 'HTTP_COOKIE_VARS', '_SERVER', 
		'HTTP_SERVER_VARS', '_FILES', 'HTTP_POST_FILES', '_REQUEST', 
		'ignoreList'
	);
	
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
	 * Recursively returns all defined variables
	 *
	 * @param array $vars 		the defined variables 
	 * @param array $ignoreList the variables to ignore 
	 *
	 * @return array $definedVars defined variables not in the ignore list
	 **************************************************************************/
	public function getVars($vars, $ignoreList=null) {
		try {
			if (empty($ignoreList)) {
				$ignoreList = $this->_varIgnoreList;
			} //<-- end if -->
				
			$main = function ($val, $key) use ($ignoreList, &$definedVars) {
				if ($key === 0 
					|| (!in_array($key, $ignoreList)) && !is_null($val)
				) {
					if (is_array($val)) {
						$definedVars[$key] = self::getVars($val);
					} elseif (is_string($val) || is_numeric($val)) { 
						$definedVars[$key] = $val;
					} //<-- end if -->
				} //<-- end if --> 
			}; //<-- end closure -->
			
			array_walk($vars, $main);			
			return $definedVars;
		} catch (Exception $e) { 
			throw new Exception(
				$e->getMessage().' from '.$this->_className.'->'.__FUNCTION__.
				'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->
} /*<-- end class -->*/
