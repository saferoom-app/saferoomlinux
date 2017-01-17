# Import section
import safeglobals,os,json,re,requests, binascii
from flask import Blueprint, jsonify,abort,request,render_template
from libs.EvernoteManager import get_from_backup,update_note, get_note_store, prepare_content
from libs.decorators import restore_decorator
from libs.ConfigManager import get_access_token
from libs.functions import millisToDate
from libs.BackupManager import render_backup

# Initializing the blueprint
mod_backups = Blueprint("mod_backups",__name__)

## ============================================
## 	Routes
## ============================================

# This route is used to restore the Evernote note's content from the backup
@mod_backups.route("/restore/<string:guid>",methods=["POST"])
@restore_decorator
def restore_from_backup(guid):
    
    # Getting the note from the backup
    guid = request.get_json().get('guid')
    note = get_from_backup(guid)
    if not note:
        abort(safeglobals.http_internal_server,{"message":""})
    
    # Getting Access Token
    access_token = get_access_token()

    # Getting the Note Store (connecting to Evernote)
    note_store = get_note_store(access_token)

    # Connecting to Evernote and updating the note
    update_note(note_store,access_token,note)    

    # Sending the response
    return jsonify(status=safeglobals.http_ok,message=safeglobals.MSG_UPDATENOTE_OK)


# This route is used to delete the backup copy
@mod_backups.route("/delete/<string:guid>",methods=["POST"])
def delete_backup_copy(guid):
	
    # Checking if the backup exists
    if os.path.isfile(safeglobals.path_notes_backup % guid) == True:
        os.remove(safeglobals.path_notes_backup % guid)

    # Sending the response
    return jsonify(status=safeglobals.http_ok)

# This route is used to display the backup in a readable format
@mod_backups.route("/view/<string:guid>",methods=["GET"])
def view_backup(guid):

    # Getting the backup
    data = get_from_backup(guid)
    if not data:
        abort(safeglobals.http_not_found,{"message":safeglobals.ERROR_NO_BACKUP % (guid+".pickle")})

    # Checking if the backup exists
    content = render_backup(guid,safeglobals.service_evernote)
    return content