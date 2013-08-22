# VRFBackupTool.py #
---

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
