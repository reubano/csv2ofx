<?php
/**
 *******************************************************************************
 * purpose: contains general functions to be used by all programs
 ******************************************************************************/
class Number {
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
	 * Returns a number with ordinal suffix, e.g., 1st, 2nd, 3rd.
	 *
	 * @param integer $num a number
	 *
	 * @return string $ext a number with the ordinal suffix
	 *
	 * @assert (11) == '11th'
	 * @assert (132) == '132nd'
	 **************************************************************************/
	public function addOrdinal($num) {
		try {
			if (!in_array(($num % 100), array(11, 12, 13))) {
				switch ($num % 10) {
					// Handle 1st, 2nd, 3rd
					case 1:
						return $num.'st';
					
					case 2:
						return $num.'nd';
					
					case 3:
						return $num.'rd';
				}
			}
			
			return $num.'th';
		
		} catch (Exception $e) { 
			throw new Exception(
				$e->getMessage().' from '.$this->_className.'->'.__FUNCTION__.
				'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->
} //<-- end Number class -->
