# Import section
from functools import wraps
from flask import request,copy_current_request_context, abort
import safeglobals,os
from libs.functions import handle_exception
from libs.ConfigManager import get_access_token
from libs.PasswordManager import get_master_password

def encrypt_decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        '''
            This decorator functions is used to check all provided data while encrypting the existing note. It does the following checks

                1. Checks if it was JSON request 
                2. Checks the data provided in the JSON request
        '''
        # Getting the data
        data = request.get_json()

        if not data:
            abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})
        if "guid" not in data or "mode" not in data or "pass" not in data or "service" not in data:
            abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})
        if data['mode'] == "otp" and data['pass'] == "":
            abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})
      
        # Checking the Evernote/Onenote access token
        if get_access_token(data['service']) == "":
            abort(safeglobals.http_bad_request,{"message":safeglobals.ERROR_NO_TOKEN})

        # Checking the provided password
        if data['mode'] == "master" and not get_master_password():
            return handle_exception(safeglobals.TYPE_JSON,safeglobals.http_bad_request,safeglobals.ERROR_NO_PASSWORD)

        return f(*args, **kwargs)
    return decorated_function

def decrypt_decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        '''
            This decorator functions is used to check all provided data while decrypting the note. It does the following checks

                1. Checks if GUID has been provided
                2. Checking passwords
                3. Checking the note on the local machine
        '''

        # Checking the GUID
        if not request.form['guid']:
            abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})
            
        # Checking if mode is set to "OTP" and OTP password has been provided
        if not request.form['mode']:
            abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})
        if request.form['mode'] == "otp" and not request.form['pass']:
            abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})

        # Checking that encrypted note is saved on local machine
        if os.path.exists(safeglobals.path_note_backup % request.form['guid']) == False:
            abort(safeglobals.http_not_found,{"message":safeglobals.MSG_NOTE_MISSING % safeglobals.path_note % (request.form['guid'],"")})       
            
        return f(*args, **kwargs)
    return decorated_function

def restore_decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        '''
            This decorator functions is used to check all provided data while restoring the note. It does the following checks

                1. Checks if GUID has been provided
                2. Checks if the backup exists
                3. Checks the access token
        '''

        # Parsing JSON
        data = request.get_json()
        if not data:
            abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})
        if "guid" not in data:
            abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})

        # Checking that backup exists
        if os.path.exists(safeglobals.path_notes_backup % data['guid']) == False:
            abort(safeglobals.http_not_found,{"message":safeglobals.MSG_NOTE_MISSING % safeglobals.path_notes_backup % data['guid']})

        # Checking the Evernote/Onenote access token
        if get_access_token(data['service']) == "":
            abort(safeglobals.http_bad_request,{"message":safeglobals.ERROR_NO_TOKEN})
            
        return f(*args, **kwargs)
    return decorated_function

def create_decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        '''
            This decorator functions is used to check all provided data while creating a new encrypted note                
        '''
        # Checking provided data
        if not request.form['title'] or request.form['title'] == "":
            abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})
    
        if not request.form['content'] or request.form['content'] == "":
            abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})

        if not request.form['notebook_guid'] or request.form['notebook_guid'] == "":
            abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})

        if request.form['service'] == safeglobals.service_onenote and request.form['section_guid'] == "":
            abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})

        if "en-media" in request.form['content'] and not request.form['filelist']:
            abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})

        if not request.form['mode']:
            abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})
        if request.form['mode'] == "otp" and not request.form['pass']:
            abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})

        if get_access_token() == "":
            abort(safeglobals.http_bad_request,{"message":safeglobals.ERROR_NO_TOKEN})

        return f(*args, **kwargs)
    return decorated_function