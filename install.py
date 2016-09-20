'''

Script is used to automate the procedure to install all necessary components for Saferoom app. Installation procedure consists of the following steps:

1. OS detection: the script detects what OS you're using
2. Python version checking
3. PIP and git installation
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
is_installed = False # Flag used to define whether the software has been installed or not
path_evernote = "/tmp/evernote-sdk-python"

# Script section
print "====================================================="
print "    Saferoom installation script "
print "====================================================="

# Checking the OS you're using
os_name = platform.platform()
print "\n    Current OS: %s \n" % (os_name)

# Checking if it is Windows
if "windows".upper() in str(os_name).upper():
    print "Currently Windows OS are not supported"
    exit()

# Installing PIP and git
## 1. Checking if "pip" is already installed
print "\n\nInstalling PIP\n========================================"
try:
    process = Popen(['pip','--version'],stdout=PIPE, stderr=PIPE)
    stdout,stderr = process.communicate()
    is_installed = True
except OSError as e:
    is_installed == False

# If "pip" is not installed, we need to install it
if is_installed == False:
    if "Ubuntu".upper() in os_name.upper():
        call(["sudo","apt-get","install","python-pip"])
    elif "centos".upper() in os_name.upper():
        call(["sudo","yum","install","-y","epel-release"])
        call(["sudo","yum","install","-y","python-pip"])
else:
    print "\n    [Already installed ]\n"
## 2. GIT installation
is_installed = False
print "\n\nInstalling GIT\n========================================"
try:
    process = Popen(['git','--version'],stdout=PIPE,stderr=PIPE)
    stdout,stderr = process.communicate()
    is_installed = True
except OSError as e:
    is_installed = False

if is_installed == False:
    if "Ubuntu".upper() in os_name.upper():
        call(['sudo','apt-get','install','git'])
    elif "centos".upper() in os_name.upper():
        call(["sudo","yum","install","-y","git"])
else:
    print "\n    [Already installed ]\n"
# Installing flask, requests, pycrypto and beautifulsoup4
print "\n\nInstalling Flask, Requests, PyCrypto and BeautifulSoup\n========================================"
if "Ubuntu".upper() in os_name.upper():
    call(['pip','install','flask','requests','pycrypto','beautifulsoup4'])
elif "centos".upper() in os_name.upper():
    call(['pip','install','flask','requests','beautifulsoup4'])
    print "\n\nInstalling python-devel and gcc\n========================================"
    call(['sudo','yum','install','-y','python-devel','gcc'])
    print "\n\nInstalling PyCrypto\n========================================\n"
    call(['pip','install','pycrypto'])

# Installing Evernote SDK
print "\n\nInstalling Evernote SDK\n========================================"
if os.path.exists(path_evernote) == False:
    os.chdir("/tmp")
    git("clone", "https://github.com/evernote/evernote-sdk-python")

os.chdir(path_evernote)
python('setup.py','install')


'''
    Verification section. Here we will check that all libraries have been successfully installed
'''

print "\n\nVerifying the installation\n========================================"
print ""
print ("    Flask  ..........."),
try:
    from flask import Flask
    print "[OK]"
except ImportError as e:
    print "[NOK]\n"+"    "+str(e)

print ("\n    PyCrypto  ........"),
try:
    from Crypto.Hash import SHA256
    print "[OK]"
except ImportError as e:
    print "[NOK]\n"+"    "+str(e)

print ("\n    Requests  ........"),
try:
    import requests
    print "[OK]"
except ImportError as e:
    print "[NOK]\n"+"    "+str(e)

print ("\n    Evernote SDK  ...."),
try:
    from evernote.api.client import EvernoteClient
    print "[OK]"
except ImportError as e:
    print "[NOK]\n"+"    "+str(e)

print ("\n    BeautifulSoup4  .."),
try:
    from bs4 import BeautifulSoup
    print "[OK]"
except ImportError as e:
    print "[NOK]\n"+"    "+str(e)
print ""


 

