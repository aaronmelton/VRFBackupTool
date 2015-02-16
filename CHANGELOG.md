# VRFBackupTool.py #
---

## VRFBackupTool v0.0.10-alpha (2015-02-16) ##
* Made a minor correction to code to ensure compatability with 15.X train of
  Cisco IOS.

## VRFBackupTool v0.0.9-alpha (2014-03-17) ##
* Replaced tab with four spaces.
* Replaced ' with " to be consistent throughout the file.
* Corrected problem where application would fail if logFileDirectory or 
  backupFileDirectory in settings.cfg was blank.

## VRFBackupTool v0.0.8-alpha (2013-09-09) ##
* Corrected makedirs() functionality: Directories with a trailing backslash
  in the config file were not being created thereby causing the application
  to fail.
* Moved logFileDirectory & backupDirectory makedirs() function such that the
  directory would only be created if/when the parent function was called
  instead of creating both directories whenever the application executed.
* Removed 'dated' variable, which was a duplicate of global variable 'date'
 
## VRFBackupTool v0.0.7-alpha (2013-08-29) ##
* Updated the backupVRF function so that the application will not log into
  any routers and retrieve results if the output file cannot be opened.
* Corrected 'mkdir' function to 'makedirs' so that directories will be
  created recursively, if they do not exist.
* Added basic logging to file to track results if application has to connect
  to a router to run buildIndex().
* Suppressed error SPAM from stdout by adding stderr=(open(os.devnull, 'w'))
  to the Queue() function. (Errors are still written to the log.)

## VRFBackupTool v0.0.6-alpha (2013-08-28) ##
* Added functionality to specify configFile from the command line.
* Updated README.md

## VRFBackupTool v0.0.5-alpha (2013-08-26) ##
* Created README.md, VRFBackupTool.png
* Updated code to remove unused modules and add additional comments.
 
 ## VRFBackupTool v0.0.4-alpha (2013-08-22) ##
* Added whitespace to the end of the "show running-config | section SMVPN"
  command to prevent incorrect matches.  (Without the space at the end, a
  search for "3" would also return "31" or "300", etc.)

## VRFBackupTool v0.0.3-alpha (2013-08-20) ##
* Adjusted output spacing (removing/moving 'print' statements)
* Added additional comments to code, configFile, routerFile.

## VRFBackupTool v0.0.2-alpha (2013-08-16) ##
* Corrected bad REGEX being applied to routeDistinguisher that incorrectly
  caused the function to grab ALL SMVPN profiles instead of the only matching
  profile.
* Changed the configFile format in such a way that a single configFile
  can be used for my different VRF applications.
* Replaced old file open function method with new file open technique
  outputFile=open(file, 'w') --> with open(file, 'w') as openFile:
* Added error checking to append a trailing backslash to the backupDirectory
  should it be missing.
* Added error checking to append a trailing integer to the backup outputFileName
  should the file already exist.
* Updated error messages so they reflect the actual filename as read
  from the configFile.
* Rewrote "Building index..." message so it does not take up most of the
  screen when working with a large batch of routers.
* Updated example configFile output to reflect new changes in configFile format.

## VRFBackupTool v0.0.1-alpha (2013-08-15) ##
* Initial commit
