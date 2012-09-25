<?php
/**
 *******************************************************************************
 * purpose: contains general functions to be used by all programs
 ******************************************************************************/
class String {
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
	 * Makes a string xml compliant
	 * 
	 * @param string $content the content to clean 
	 *
	 * @return string $content the cleaned content
	 * @throws Exception if $content is empty
	 **************************************************************************/
	public function xmlize($content) {
		if (empty($content)) { // check to make sure $content isn't empty
			throw new Exception(
				'Empty value passed from '.$this->_className.'->'.__FUNCTION__.
				'() line '.__LINE__
			);
		} else {
			try {
				$invalidText = array('&', '<', '>', '\r\n', '\n');
				$validText = array('&amp;', '&lt;', '&gt;', ' ', ' ');
				return str_replace($invalidText, $validText, $content);
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
	 * Parses each line of an array of raw csv data into an array 
	 *
	 * @param array $csvContent		 csv content (each array should contain one
	 * 								 line of csv data)
	 * @param string $fieldDelimiter the csv field delimiter 
	 *
	 * @return array $arrContent	 array of csv data
	 * @throws Exception if $csvFile does not exist
	 *
	 * @assert (array('content,to,parse')) == array('content', 'to', 'parse')
	 **************************************************************************/
	public function csv2Array($csvContent, $fieldDelimiter=',') {
		try {
			$arrContent = array_walk(
				$csvContent, 'str_getcsv', $fieldDelimiter
			);
			
			return $arrContent;			
		} catch (Exception $e) { 
			throw new Exception(
				$e->getMessage().' from '.$this->_className.'->'.__FUNCTION__.
				'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->

	/**
	 ***************************************************************************
	 * Converts an array to string while adding an extra string to the beginning
	 * and end of each element
	 *
	 * @param array  $content 	array to convert 
	 * @param string $extra  	string to add to the beginning and end of 
	 *							each array element
	 * @param string $delimiter	character to seperate each arrayelement 
	 *
	 * @return string $content	content formatted on 1 line with the extra
	 *							string added to the beginning and end of
	 *							each array element
	 * @throws Exception if $content is not an array 
	 **************************************************************************/
	public function extraImplode($content, $extra = '\'', $delimiter = ' ') {
		if (!is_array($content)) {
			throw new Exception(
				'Please use an array from '.$this->_className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				return $extra.implode($extra.$delimiter.$extra, $content).
					$extra; // array to string	
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
	 * Converts line endings to LF line endings
	 * 
	 * @param string $content data to process
	 *
	 * @return string $content data with LF line endings
	 * @throws Exception if $file does not exist
	 **************************************************************************/
	public function makeLFLineEndings($content) {
		try {
			$content = str_replace("\r\n", "\n", $content);
			$content = str_replace("\r", "\n", $content);
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
	 * Returns an array from a multiline string
	 *
	 * @param string $content a multiline string 
	 *
	 * @return array $content array (one element from each line in the
	 *						  string)
	 **************************************************************************/
	public function lines2Array($content, $lineEnding="\n") {		
		try {
			$content = explode($lineEnding, $content); // turn string to array
			array_pop($content); // remove last element since it is empty
			return $content;
		} catch (Exception $e) { 
			throw new Exception(
				$e->getMessage().' from '.$this->_className.'->'.__FUNCTION__.
				'() line '.__LINE__
			);
		} //<-- end try -->
	} //<-- end function -->
} //<-- end String Class -->