#!/usr/bin/env python
#
# VRFBackupTool.py
# Copyright (C) 2013 Aaron Melton <aaron(at)aaronmelton(dot)com>
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import base64		# Required to decode password
import datetime		# Required for date format
import ConfigParser # Required for configuration file
import Exscript		# Required for SSH, queue & logging functionality
import re			# Required for REGEX operations
import sys			# Required for printing without newline
import os			# Required to determine OS of host

from base64						import b64decode
from ConfigParser				import ConfigParser
from datetime                   import datetime
from Exscript                   import Account, Queue, Host, Logger
from Exscript.protocols 		import SSH2
from Exscript.util.file			import get_hosts_from_file
from Exscript.util.log          import log_to
from Exscript.util.decorator    import autologin
from Exscript.util.interact     import read_login
from Exscript.util.report		import status,summarize
from re							import search, sub
from sys						import stdout
from os							import name, path, remove, system


def backupVRF(vrfName, localPeer):
# This function takes the VRF Name and Local Peer IP as determined during
# the searchIndex() function, retrieves all matching VRFs from their respective
# routers and writes the config to a file.

	if username == '':				# If username is blank
		print
		account = read_login()		# Prompt the user for login credentials
	
	elif password == '':			# If password is blank
		print
		account = read_login()		# Prompt the user for login credentials

	else:							# Else use username/password from configFile
		account = Account(name=username, password=b64decode(password))
		
	print
	print "--> Logging into "+localPeer+"..."
	
	socket = SSH2()						# Set connection type to SSH2
	socket.connect(localPeer)			# Open connection to router
	socket.login(account)				# Authenticate on the remote host
	
	print "--> Backing up "+vrfName+"..."
	
	socket.execute("terminal length 0")	# Disable page breaks in router output
										# socket.autoinit() doesn't seem to disable
										# page breaks; Using standard command instead
	socket.execute("show running-config | section "+vrfName)	# Send command to router

	dated = datetime.now()				# Determine today's date
	dated = dated.strftime('%Y%m%d')	# Format date as YYYYMMDD

	outputFileName = backupDirectory+vrfName+'_Config_'+dated+'.txt'	# Define output filename based on hostname and date
	
	# Check to see if outputFileName currently exists.  If it does, tack an
	# integer onto the end of the filename until outputFileName no longer exists
	incrementFilename = 1
	while fileExist(outputFileName):
		outputFileName = backupDirectory+vrfName+'_Config_'+dated+'_'+str(incrementFilename)+'.txt'
		incrementFilename = incrementFilename + 1
		
	with open(outputFileName, 'w') as outputFile:
		try:
			outputFile.write(socket.response)	# Write contents of running config to output file
			
			# Use REGEX to locate Route Distinguisher in results from router
			routeDistinguisher = search(r'\srd\s\b[0-9]{0,4}\b:0', socket.response).group(0)
			# Use REGEX to remove everything but the actual Route Distinguisher number.
			routeDistinguisher = sub(r'\srd\s', '', routeDistinguisher)
			routeDistinguisher = sub(r':0', '', routeDistinguisher)
			
			socket.execute("show running-config | section SMVPN "+routeDistinguisher)
			outputFile.write(socket.response)	# Write contents of running config to output file
		except IOError:
			print "\n--> An error occurred opening "+outputFile+".\n"	

	socket.send("exit\r")	# Send the "exit" command to log out of router gracefully
	socket.close()			# Close SSH connection

	print '--> '+vrfName+' backed up to '+outputFileName+'.'

#@log_to(Logger())	# Logging decorator; Must precede buildIndex!
					# Logging (to screen) not useful unless # threads > 1
@autologin()		# Exscript login decorator; Must precede buildIndex!
def buildIndex(job, host, socket):
# This function builds the index file by connecting to the router and extracting all
# matching sections.  I chose to search for 'crypto keyring' because it is the only
# portion of a VPN config that contains the VRF name AND Peer IP.  Caveat is that
# the program temporarily captures the pre-shared key.  'crypto isakmp profile' was not
# a suitable query due to the possibility of multiple 'match identity address' statements

	stdout.write('.')					# Write period without trailing newline
	socket.execute("terminal length 0")	# Disable user-prompt to page through config
										# Exscript doesn't always recognize Cisco IOS
										# for socket.autoinit() to work correctly

	# Send command to router to capture results
	socket.execute("show running-config | section crypto keyring")

	with open(indexFileTmp, 'a') as outputFile:
		try:
			outputFile.write(socket.response)	# Write contents of running config to output file
		except IOError:
			print "\n--> An error occurred opening "+indexFileTmp+".\n"	

	socket.send("exit\r")	# Send the "exit" command to log out of router gracefully
	socket.close()			# Close SSH connection

	cleanIndex(indexFileTmp, host)		# Execute function to clean-up the index file
	
def cleanIndex(indexFileTmp, host):
# This function strips all the unnecessary information collected from the router leaving
# only the VRF name, remote Peer IP and local hostname or IP

	try:
		# If the temporary index file can be opened, proceed with clean-up
		with open(indexFileTmp, 'r') as srcIndex:

			try:
				# If the actual index file can be opened, proceed with clean-up
				# Remove unnecessary details from the captured config
				with open(indexFile, 'a') as dstIndex:
					# Use REGEX to step through config and remove everything but
					# the VRF Name, Peer IP & append router hostname/IP to the end
					a = srcIndex.read()
					b = sub(r'show running-config \| section crypto keyring.*', '', a)
					c = sub(r'crypto keyring ', '' ,b)
					d = sub(r'.(\r?\n)..pre-shared-key.address.', ',' ,c)
					e = sub(r'.key.*\r', ','+host.get_name() ,d)
					f = sub(r'.*#', '', e)
					dstIndex.write(f)

			# Exception: actual index file was not able to be opened
			except IOError:
				print "\n--> An error occurred opening "+indexFile+".\n"

	# Exception: temporary index file was not able to be opened
	except IOError:
		print "\n--> An error occurred opening "+indexFileTmp+".\n"
	
	# Always remove the temporary index file
	finally:
		remove(indexFileTmp)	# Critical to remove temporary file as it contains passwords!

def confirm(prompt="", defaultAnswer="y"):
# This function prompts the user to answer "y" for yes or "n" for no
# Returns true if the user answers Yes, false if the answer is No
# The user will not be able to bypass this function without entering valid input: y/n

	while True:
		# Convert response to lower case for comparison
		response = raw_input(prompt).lower()
	
		# If no answer provided, assume Yes
		if response == '':
			return defaultAnswer
	
		# If response is Yes, return true
		elif response == 'y':
			return True
	
		# If response is No, return false
		elif response == 'n':
			return False
	
		# If response is neither Yes or No, repeat the question
		else:
			print "Please enter y or n."

def fileExist(fileName):
# This function checks the parent directory for the presence of a file
# Returns true if found, false if not

	try:
		# If file can be opened, it must exist
		with open(fileName, 'r') as openedFile:
			return True	# File found

	# Exception: file cannot be opened, must not exist
	except IOError:
		return False	# File NOT found

def routerLogin():
# This function prompts the user to provide their login credentials and logs into each
# of the routers before calling the buildIndex function to extract relevant portions of
# the router config.  As designed, this function actually has the capability to login to
# multiple routers simultaneously.  I chose to not allow it to multi-thread given possibility
# of undesirable results from multiple threads writing to the same index file simultaneously

	try:# Check for existence of routerFile; If exists, continue with program
		with open(routerFile, 'r'): pass
		
		# Read hosts from specified file & remove duplicate entries, set protocol to SSH2
		hosts = get_hosts_from_file(routerFile,default_protocol='ssh2',remove_duplicates=True)

		if username == '':				# If username is blank
			account = read_login()		# Prompt the user for login credentials

		elif password == '':			# If password is blank
			account = read_login()		# Prompt the user for login credentials

		else:							# Else use username/password from configFile
			account = Account(name=username, password=b64decode(password))
		
		queue = Queue(verbose=0, max_threads=1)	# Minimal message from queue, 1 threads
		queue.add_account(account)				# Use supplied user credentials
		print
		stdout.write("--> Building index...") 	# Print without trailing newline
		queue.run(hosts, buildIndex)			# Create queue using provided hosts
		queue.shutdown()						# End all running threads and close queue
		
		#print status(Logger())	# Print current % status of operation to screen
								# Status not useful unless # threads > 1

	# Exception: router file was not able to be opened
	except IOError:
		print "\n--> An error occurred opening "+routerFile+".\n"

def searchIndex(fileName):
# This function searches the index for search string provided by user and
# returns the results, if any are found

	# Ask the user to provide search string
	print
	searchString = raw_input("Enter the VRF Name you want to back up: ")
	
	# Repeat the question until user provides ANY input
	while searchString == '':
		searchString = raw_input("Enter the VRF Name you want to back up: ")
	
	# As long as the user provides ANY input, the application will search for it
	else:
		try:
			# If the index file can be opened, proceed with the search
			with open(fileName, 'r') as openedFile:
				# Quickly search the file for search string provided by user
				# If search string found in the file, we will search again to return the results
				# Otherwise inform the user their search returned no results
				if searchString in openedFile.read():
					openedFile.seek(0)	# Reset file cursor position
					searchFile = openedFile.readlines()	# Read each line in the file one at a time
					for line in searchFile:
						if searchString in line:
							word = line.split(',')	# Split up matching line at the comments
							vrfName = word[0]				# Strip out VRF name from search results
							localPeer = word[2].rstrip()	# Strip out Local Peer IP from search results
							backupVRF(vrfName, localPeer)
	
				# Else: Search string was not found
				else:
					print "\n--> Your search string was not found in "+indexFile+".\n"
	
		# Exception: index file was not able to be opened
		except IOError:
			print "\n--> 2. An error occurred opening "+indexFile+".\n"
							 
def upToDate(fileName):
# This function checks the modify date of the index file
# Returns true if file was last modified today, false if the file is older than today

	# If the modify date of the file is equal to today's date
	if datetime.fromtimestamp(path.getmtime(fileName)).date() == datetime.today().date():
		return True	# File is "up-to-date" (modified today)

	# Else the modify date of the index file is not today's date
	else:
		return False	# File is older than today's date


# Change the filenames of these variables to suit your needs
configFile='settings.cfg'

# Determine OS in use and clear screen of previous output
system('cls' if name=='nt' else 'clear')

print "VRF Backup Tool v0.0.2-alpha"
print "----------------------------"

try:
# Try to open configFile
	with open(configFile, 'r'):
		print
	
except IOError:
# Except if configFile does not exist, create an example configFile to work from
	try:
		with open (configFile, 'w') as exampleFile:
			print
			print "--> Config file not found; Creating "+configFile+"."
			print
			exampleFile.write("[account]\n#password is base64 encoded! Plain text passwords WILL NOT WORK!\n#Use website such as http://www.base64encode.org/ to encode your password\nusername=\npassword=\n\n")
			exampleFile.write("[VRFBackupTool]\n#Check your paths! Files will be created; Directories will not.\n#Bad directories may result in errors!\n#variable=C:\path\\to\\filename.ext\nrouterFile=routers.txt\nindexFile=index.txt\nindexFileTmp=index.txt.tmp\nbackupDirectory=\n")
	except IOError:
		print "\n--> An error occurred creating the example "+configFile+".\n"

finally:
# Finally, using the provided configFile (or example created), pull values
# from the config and login to the router(s)
	config = ConfigParser(allow_no_value=True)
	config.read(configFile)
	username = config.get('account', 'username')
	password = config.get('account', 'password')
	routerFile = config.get('VRFBackupTool', 'routerFile')
	indexFile = config.get('VRFBackupTool', 'indexFile')
	indexFileTmp = config.get('VRFBackupTool', 'indexFileTmp')
	backupDirectory = config.get ('VRFBackupTool', 'backupDirectory')
	
	# If backupDirectory does not contain trailing backslash, append one
	if backupDirectory != '':
		if backupDirectory[-1:] != "\\":
			backupDirectory = backupDirectory+"\\"
			
	# Does routerFile exist?
	if fileExist(routerFile):
		# Does indexFile exist?
		if fileExist(indexFile):
			# File created today?
			if upToDate(indexFile):
				print("--> Index found and appears up to date.")
				searchIndex(indexFile)
			else: # if upToDate(indexFile):
				# Update indexFile?
				print
				if confirm("The index does not appear up-to-date.\n\nWould you like to update it? [Y/n] "):
					print
					# Remove old indexFile to prevent duplicates from being added by appends
					remove(indexFile)
					routerLogin()
					print
					searchIndex(indexFile)
				else: # if confirm("Would you like to update the index? [Y/n] "):
					searchIndex(indexFile)
		else: # if fileExist(indexFile):
			print("--> No index file found, we will create one now.")
			routerLogin()
			print
			searchIndex(indexFile)
			
	else: # if fileExist(routerFile):
		try:
			with open (routerFile, 'w') as exampleFile:
				exampleFile.write("192.168.1.1\n192.168.1.2\nRouterA\nRouterB\nRouterC\netc...")
				print
				print "Required file "+routerFile+" not found; One has been created for you."
				print "This file must contain a list, one per line, of Hostnames or IP addresses the"
				print "application will then connect to download the running-config."
				print
		except IOError:
			print
			print "Required file "+routerFile+" not found."
			print "This file must contain a list, one per line, of Hostnames or IP addresses the"
			print "application will then connect to download the running-config."
			print

print
print "--> Done."
raw_input()	# Pause for user input.