# Import section
import os
import config
from libs.functions import log_message,decryptString,generateKey
import platform
import getpass
import json

# Functions
def get_master_password():
    password = ""
    try:
        # Checking if master password file has been generated
        if os.path.exists(config.path_password) == False:
            return password

        # Checking if master password is in this file :)
        with open(config.path_password,"r") as f:
            data = json.loads(f.read())
        if not data['pass']:
            return password

        # Decrypting password
        password = decryptString(data['pass'],generateKey(platform.system(),getpass.getuser(),config.SALT))
        return password

    except Exception as e:
        log_message(str(e))
        return ""


def set_password(mode,otp):
	if (mode == "otp"):
		return otp
	else:
		return get_master_password()
