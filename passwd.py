import os
import getpass
import time
from libs.functions import encryptString, decryptString, generateKey
import safeglobals
import json
import uuid
import hashlib
import platform

# init section
password = ""
exists = False
passTrue = False


# Function that write passwords into a specified file
def save_password(password):

	# Generating unique ID
	print ""
	print("   Generating salt ......"),
	salt = safeglobals.SALT
	print "[OK]"

	# Encrypting password
	print ""
	print("   Encrypting password ......"),
	encrypted_password = encryptString(password,generateKey(platform.system(),getpass.getuser(),safeglobals.SALT))
	print "[OK]"

	# Saving password to a specified file
	credentials = {"pass":encrypted_password}
	print ""
	print("   Saving password ......"),
	with open(safeglobals.path_password,"w") as f:
		f.write(json.dumps(credentials))
	print "[OK]"
	print ""
	print "Your master password has been saved into ["+safeglobals.path_password+"] file. This password is encrypted, however if someone gets access to your machine, your master password can be easily decrypted. Please make sure that this file is protected from unauthorized use"

def wait_for_password():
    passTrue = False
    while passTrue == False:
        password = getpass.getpass("Type a new master password: ")
        confirm_password = getpass.getpass("Confirm your master password: ")
        if password != "" and len(password)>=8 and len(password)<=256 and password == confirm_password:
            passTrue = True
        else:
            print ""
            print "   - Password length should be between 8 and 256 characters"
            print "   - Passwords should match"
            print ""
    return password

print ""
print "=============================================="
print "|    Saferoom Master Password generator      |"
print "=============================================="

# Checking the current platform informattion
print ""
print "OS: "+platform.system()
print "Current user: "+getpass.getuser()
print "Salt: "+safeglobals.SALT
print ""
print " ** Please note that these parameters will be used to generate the key, that will be used to encrypt your Master password. This key will not be stored anywhere and will be generated during the runtime"
print ""
print ""
print("   Checking if password already exists ......."),

# Checking if password exists
exists = os.path.isfile(safeglobals.path_password)


if (exists):
    print "[OK]"
    print ""
    overwrite = raw_input("Master password already exists. Do you want to overwrite it? [Yes|No]: ")
    if (overwrite.upper() == "No".upper()):
        exit()

    # Waiting for password input
    password = wait_for_password()
        
    # Saving password
    save_password(password)

else:
    print "[NOK]"
    print ""
    # Waiting for password inptut
    password = wait_for_password()

    # Saving password
    save_password(password)
