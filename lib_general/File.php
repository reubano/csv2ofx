<?php
/**
 *******************************************************************************
 * purpose: contains general functions to be used by all programs
 ******************************************************************************/

date_default_timezone_set('Africa/Nairobi');
class File {
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
	 * Returns the extension of a file
	 *
	 * @param string $file a filename or the path to a file
	 *
	 * @return string $ext the file extension
	 * @throws Exception if $file is empty
	 *
	 * @assert ('file.ext') == 'ext'
	 * @assert ('/path/to/file.ext') == 'ext'
	 **************************************************************************/
	public function getExtension($file) {
		if (empty($file)) {
			throw new Exception(
				'Empty file passed from '.$this->_className.'->'.__FUNCTION__.
				'() line '.__LINE__
			);
		} else {
			try {
				return pathinfo($file, PATHINFO_EXTENSION);
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
	 * Writes data to a file 
	 * 
	 * @param string $content	 the data to write to the file 
	 * @param string $file	  	 the file path
	 * @param boolean $overWrite over write file if exists 
	 *
	 * @return int $bytes the number of bytes written to file
	 * @throws Exception if $content is empty
	 * @throws Exception if $file exists as a non-empty file
	 **************************************************************************/
	public function write2File($content, $file, $overWrite=false) {
		if (empty($content)) { // check to make sure $content isn't empty
			throw new Exception(
				'Empty content passed from '.$this->_className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} elseif (file_exists($file) && !$overWrite) {
			throw new Exception(
				'File '.$file.' already exists from '.$this->_className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$handle = fopen($file, 'w');
				$bytes = fwrite($handle, $content);
				fclose($handle);
					
				if ($this->_verbose) {
					fwrite(STDOUT, "Wrote $bytes bytes to $file!\n");
				} //<-- end if -->
					
				return $bytes;
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
	 * Returns the filename without extension of a file
	 *
	 * @param string $file a filename or the path to a file
	 *
	 * @return string $base	filename without extension
	 * @throws Exception if an empty value is passed
	 *
	 * @assert ('file.ext') == 'file'
	 * @assert ('/path/to/file.ext') == 'file'
	 **************************************************************************/
	public function getBase($file) {
		if (empty($file)) {
			throw new Exception(
				'Empty file passed from '.$this->_className.'->'.__FUNCTION__.
				'() line '.__LINE__
			);
		} else {
			try {
				return pathinfo($file, PATHINFO_FILENAME);
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
	 * Returns the full path to files in the current directory
	 *
	 * @param array $files a file in the current directory
	 *
	 * @return string $base	filename without extension
	 * @throws Exception if $files is not an array 
	 **************************************************************************/
	public function getFullPath($files) {
		if (!is_array($files)) {
			throw new Exception(
				'Please use an array from '.$this->_className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {
				$dir = getcwd();
				
				$addDir = function (&$value, $key) {
					if (strpos($value, '/') === false) {
				 		$value = $dir.'/'.$value;
					}
				};
				
				array_walk_recursive($files, $addDir);
				return $files;
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
	 * Reads the contents of a given file to an array
	 * 
	 * @param string  $file			  a filename or the path to a file
	 * @param boolean $csv			  is $file a csv file?
	 * @param string  $fieldDelimiter the csv field delimiter 
	 *
	 * @return array $content the file contents
	 * @throws Exception if $file does not exist
	 **************************************************************************/
	public function file2Array($file, $csv=false, $fieldDelimiter=',') {
		if (!file_exists($file)) {
			throw new Exception(
				'File '.$file.' does not exist from '.$this->_className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {				
				$handle = fopen($file, 'r');
				
				while (!feof($handle)) {
					if ($csv) {
						$content[] = fgetcsv($handle, 1024, $fieldDelimiter);
					} else {
						$content[] = fgets($handle, 1024);
					}
				} //<-- end while -->
				
				fclose($handle);
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
	 * Reads the contents of a given file to a string
	 * 
	 * @param string $file a filename or the path to a file
	 *
	 * @return string $content the file contents
	 * @throws Exception if $file does not exist
	 **************************************************************************/
	public function file2String($file) {
		if (!file_exists($file)) {
			throw new Exception(
				'File '.$file.' does not exist from '.$this->_className.'->'.
				__FUNCTION__.'() line '.__LINE__
			);
		} else {
			try {				
				$handle = fopen($file, 'r');
				$content = null;
				
				while (!feof($handle)) {
					$content .= fgets($handle, 1024);
				} //<-- end while -->
				
				fclose($handle);
				return $content;
			} catch (Exception $e) { 
				throw new Exception(
					$e->getMessage().' from '.$this->_className.'->'.
					__FUNCTION__.'() line '.__LINE__
				);
			} //<-- end try -->
		} //<-- end if -->
	} //<-- end function -->
} //<-- end File class -->
