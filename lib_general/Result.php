<?php
/**
 *******************************************************************************
 * purpose: contains general functions to be used by all programs
 ******************************************************************************/

date_default_timezone_set('Africa/Nairobi');
class Result {
	protected $_className = __CLASS__;	// class name
	public $result;

	/**
	 ***************************************************************************
	 * The class constructor
	 *
	 * @param boolean $verbose enable verbose comments
	 *
	 **************************************************************************/
	public function __construct($result) {
		$this->result = $result;

		if ($this->_verbose) {
			fwrite(STDOUT, "$this->_className class constructor set.\n");
		} //<-- end if -->
	} //<-- end function -->
} //<-- end Result class -->
