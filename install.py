'''

Script is used to automate the procedure to install all necessary components for Saferoom app. Installation procedure consists of the following steps:

1. OS detection: the script detects what OS you're using
2. PIP and git installation
4. PIP verification
5. Flask, Requests and PyCrypto installation
6. Installing Evernote SDK
7. BeautifulSoup4 installation

'''

# Import section
import os
import platform
import sys
from subprocess import Popen, PIPE,call,check_call

# Functions section
def git(*args):
    return check_call(['git'] + list(args))
def python(*args):
    return check_call(['sudo','python']+list(args))

# Variables
is_centos = False # If this flag is True, then we need additional during Pycrypto installation
is_installed = False # Flag used to define whether the software has been installed or not
path_evernote = "/tmp/evernote-sdk-python"

# Script section
print "====================================================="
print "    Saferoom installation script "
print "====================================================="

# Checking the OS you're using
os_name = platform.platform()
print "\n    Current OS: %s \n" % (os)

# Checking if it is Windows
if "windows".upper() in str(os_name).upper():
    print "Currently Windows OS are not supported"
    exit()

# Checking if it is CentOS/Red Hat OS
# [skipped]

# Installing PIP and git
## 1. Checking if "pip" is already installed
print "    Installing PIP ... [please wait]\n"
try:
    process = Popen(['pip','--version'],stdout=PIPE, stderr=PIPE)
    stdout,stderr = process.communicate()
    is_installed = True
except OSError as e:
    is_installed == False
    print str(e)

# If "pip" is not installed, we need to install it
if is_installed == False:
    if "Ubuntu".upper() in os_name.upper():
        call(["sudo","apt-get","install","python-pip"])

print "    PIP installation: [Finished]"

## 2. GIT installation
is_installed = False
print "\n    Installing GIT ... [please wait]\n"
try:
    process = Popen(['git','--version'],stdout=PIPE,stderr=PIPE)
    stdout,stderr = process.communicate()
    is_installed = True
except OSError as e:
    is_installed = False

if is_installed == False:
    if "Ubuntu".upper() in os_name.upper():
        call(['sudo','apt-get','install','git'])

print "    GIT installation [Finished]"


# Installing flask, requests, pycrypto and beautifulsoup4
print "\n    Installing Flask, Requests, PyCrypto and BeautifulSoup ... [please wait]\n"
if "Ubuntu".upper() in os_name.upper():
    call(['pip','install','flask','requests','pycrypto','beautifulsoup4'])

print "Flask, Requests, PyCrypto and BeautifulSoup4 installation: [Finished]"

# Installing Evernote SDK
print "\n    Installing Evernote SDK\n"
if os.path.exists(path_evernote) == False:
    os.chdir("/tmp")
    git("clone", "https://github.com/evernote/evernote-sdk-python")

os.chdir(path_evernote)
python('setup.py','install')
print "    Evernote SDK installation: [Finished]"
