import os
import getpass
import time
from libs.functions import encryptString, decryptString
import config
import json
import uuid

# init section
password = ""
exists = False
passTrue = False

# Function that write passwords into a specified file
def save_password(password):

	# Generating unique ID
	print ""
	print("   Generating salt ......"),
	salt = uuid.uuid4()
	print "[OK]"

	# Encrypting password
	print ""
	print("   Encrypting password ......"),
	encrypted_password = encryptString(password,getpass.getuser()+"__"+str(salt))
	print "[OK]"

	# Saving password to a specified file
	credentials = {"pass":encrypted_password,"salt":str(salt)}
	print ""
	print("   Saving password ......"),
	with open(config.path_password,"w") as f:
		f.write(json.dumps(credentials))
	print "[OK]"
	print ""
	print "Your master password has been saved into ["+config.path_password+"] file. This password is encrypted, however if someone gets access to your machine, your master password can be easily decrypted. Please make sure that this file is protected from unauthorized use"

print ""
print "=============================================="
print "|    Saferoom Master Password generator      |"
print "=============================================="

print ""
print("   Checking if password already exists ......."),

# Checking if password exists
exists = os.path.isfile(config.path_password)
print "[OK]"
print ""

if (exists):
    overwrite = raw_input("Master password already exists. Do you want to overwrite it? [Yes|No]: ")
    if (overwrite.upper() == "No".upper()):
        exit()

    while passTrue == False:
        password = getpass.getpass("Type a new master password: ")
        if password != "" and len(password)>=8 and len(password)<=256:
            passTrue = True
        else:
            print ""
            print "   - Password length should be between 8 and 256 characters"
            print ""
    # Saving password
    save_password(password)

else:
    while passTrue == False:
        password = getpass.getpass("Type a new master password: ")
        if password != "" and len(password)>8 and len(password)<256:
            passTrue = True
        else:
            print ""
            print "   - Password length should be between 8 and 256 characters"
            print ""

    # Saving password
    save_password(password)
