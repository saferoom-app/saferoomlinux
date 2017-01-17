# Import section
import safeglobals,os,json,re,requests,shutil,binascii
import xml.etree.ElementTree as ET
from flask import Blueprint, jsonify,abort,request,render_template,session
from libs.functions import encryptNote,stringMD5,decryptNote,decryptFileData,getMime,getIcon,millisToDate,fileMD5,str_to_bool,handle_exception,send_response,parse_content, get_status, write_status,remove_status
from bs4 import BeautifulSoup, Tag
from libs.EvernoteManager import list_notes,create_note,get_note,render_note,prepare_content,encrypt_note, get_note_store, get_raw_note, backup_note, update_note, upload_note, get_from_backup
from libs.OnenoteManager import list_on_notes, get_page,create_on_note, render_page, init_note
from libs.PasswordManager import set_password,get_master_password
from libs.ConfigManager import get_access_token
from libs.decorators import encrypt_decorator, decrypt_decorator, create_decorator
from libs.Safenote import Safenote


# Initializing the blueprint
mod_note = Blueprint("mod_note",__name__)

# Initializing routes
@mod_note.route("/list",methods=['POST','GET'])
def notes():
    
    # Defining response type
    if request.form['format']:
        responseType = request.form['format']
    else:
        responseType = "json"

    # Getting developer token
    access_token = get_access_token()
    if access_token == "":
        abort(safeglobals.http_bad_request,{"message":safeglobals.ERROR_NO_TOKEN})

    # Connecting to Evernote
    note_store = get_note_store(access_token)

    # Getting a list of notes
    notes = list_notes(note_store,\
        access_token,\
        str_to_bool(request.form['refresh']),\
        request.form["type"],\
        request.form['guid'],\
        request.form['display'])

    # Sending response based on specified response type
    return send_response(notes,responseType,{safeglobals.TYPE_HTML:"list.notes.html"})

@mod_note.route("/create",methods=['POST'])
@create_decorator
def createnote():
   
    content = request.form['content']
    fileList = json.loads(request.form['filelist'])
    tags = []
    if request.form['tags']:
        tags = request.form['tags'].split(",")

    # Filtering data
    content = content.replace("<p id=\"saferoomAttach\"><br></p>","").replace("<br>","").replace("id=\"saferoomAttach\"","")       
    content = parse_content(request.form['service'],content)

    # Set password
    password = set_password(request.form['mode'],request.form['pass'])

    # Creating a note
    access_token = get_access_token(request.form['service'])

    # Creating a new note
    note = Safenote()
    note.title = request.form['title']
    note.content = content
    if (request.form['service'] == safeglobals.service_onenote):
        note.notebookGuid = request.form['section_guid']
    else:
        note.notebookGuid = request.form['notebook_guid']
    note.tagNames = [str(tag).strip() for tag in tags ]
    

    # Adding resources to the note
    note.resources = []
    hashes = []
    for file in fileList:
        if (file.get('name') and file.get('mime')):
            note.resources.append(Safenote.create_resource(os.path.join(safeglobals.path_tmp,file.get('name'))))
            hashes.append(file.get('hash'))

    
    # Encrypting the note
    note.encrypt(password,request.form['service'])

    if request.form['service'] == safeglobals.service_evernote:

        # Connecting to Evernote
        note_store = get_note_store(access_token)

        # Uploading the note to server
        upload_note(note_store,access_token,note)

    elif request.form['service'] == safeglobals.service_onenote:
        create_on_note(access_token,note,hashes)    

    return jsonify(status=safeglobals.http_ok,message=safeglobals.MSG_NOTECREATE_OK)
    
@mod_note.route("/decrypt",methods=['POST'])
@decrypt_decorator
def decrypt_note():
    
    # Getting the GUID
    guid = request.form['guid']
    note = Safenote.get_from_backup(guid,path=safeglobals.path_note_backup)

    # Setting decryption password
    password = set_password(request.form['mode'],request.form['pass'])
    
    # Decrypting the note
    try:
        note.content = Safenote.get_content(note.content)
        note.decrypt(password)
    except Exception as e:
        return handle_exception(safeglobals.TYPE_HTML,safeglobals.http_internal_server,e.message)        

    # Dumping resource into the file
    note.dump_resources()

    # Finding all <en-media> tags within the note content
    return note.render()

@mod_note.route("/on/decrypt",methods=['POST'])
@decrypt_decorator
def decrypt_onenote_note():
    
    # Getting GUID
    guid = request.form['guid']
    note = Safenote.get_from_backup(guid,path=safeglobals.path_note_backup)

    # Setting decryption password
    password = set_password(request.form['mode'],request.form['pass'])

    # Decrypting the note
    try:
        note.content = Safenote.get_content(note.content)
        note.decrypt(password)
    except Exception as e:
        return handle_exception(safeglobals.TYPE_HTML,safeglobals.http_internal_server,str(e))
    
    return note.render(safeglobals.service_onenote)

@mod_note.route("/<string:GUID>",methods=['POST','GET'])
def note(GUID):
  
    # Checking that GUID has been specified
    if not GUID or GUID == "":
        abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})

    if request.method == "GET":
        return render_template("view.html",title="Application :: View note",guid=GUID)

    # Getting note
    forceRefresh = False
    data = request.get_json()
    if not data:
        abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})
    if "refresh" in data:
        forceRefresh = data['refresh']            

    # Checking developer token
    access_token = get_access_token()
    if access_token == "":
        abort(safeglobals.http_bad_request,{"message":safeglobals.ERROR_NO_TOKEN})

    # Connecting to Evernote
    note_store = get_note_store(access_token)
    
    # Getting note    
    note = get_note(note_store,access_token,GUID,forceRefresh)
       
    # Sending response
    return jsonify(note={"title":note.title,"content":note.render(),\
        "favourite":note.is_encrypted(),"backup":note.is_backed_up(),"encrypted":note.is_encrypted()})

@mod_note.route("/encrypt",methods=["POST"])
@encrypt_decorator
def encrypt_evernote_note():

    # Getting the password
    data = request.get_json()

    # Creating status
    write_status(data['sid'],{"status":safeglobals.MSG_INIT,"value":0})
        
    # Setting encryption password
    password = set_password(data['mode'],data['pass'])

    # Getting Access Token
    access_token = get_access_token()

    # Connecting to Evernote
    note_store = get_note_store(access_token)
     
    # Downloading the note
    write_status(data['sid'],{"status":safeglobals.MSG_DOWN_BACKUP,"value":0})

    # Backing up notes
    for guid in data['guid']:
        
        # Downloading a note from the Evernote server
        note = get_note(note_store,access_token,guid,True)
        
        # Backing up the note
        note.backup()

    # Starting to encrypt notes
    count = 1
    for guid in data['guid']:

        # Getting a note from backup
        note = Safenote.get_from_backup(guid)
        if not note:
            count = count + 1
            continue

        # Checking that note has not been encrypted before
        if safeglobals.ENCRYPTED_SUFFIX in note.content:
            count = count + 1
            continue

        # Writing status
        write_status(data['sid'],{"status":safeglobals.MSG_ENCRYPT_NOTE % (note.title),"value":count})
        
        # Encrypting and uploading the note
        note.encrypt(password)
        update_note(note_store,access_token,note)

        # Clearing the cached copy of the note
        if note.is_backed_up() == True:
            os.remove(safeglobals.path_note_backup % note.guid)

        count = count + 1
    
    remove_status(data['sid'])
    return jsonify(status=safeglobals.http_ok)    

@mod_note.route("/on/encrypt",methods=["POST"])
@encrypt_decorator
def encrypt_onenote_note():
    
    # Parsing JSON
    json = request.get_json()

    # Getting Access Token
    access_token = get_access_token(safeglobals.service_onenote)

    # Getting current page
    content = download_note(access_token,json['guid'][0])

    # Creating a note object for backup
    note = init_note(json['guid'][0],content)
    print note.guid
    
    return ""

@mod_note.route("/status/<string:sid>")
def get_encryption_status(sid):
    return jsonify(get_status(sid))

@mod_note.route("/on/list/<string:guid>/<string:responseType>")
def list_onenote_notes(guid,responseType):
    forceRefresh = False
    if request.args.get("refresh"):
        forceRefresh = str_to_bool(request.args.get("refresh"))

    # Getting a list of sections
    access_token = get_access_token(safeglobals.service_onenote)
    notes = list_on_notes(access_token,forceRefresh,guid)

    # Returning response based on specified format
    return send_response(notes,responseType,{"default":"onenote.list.notes.html"})    

@mod_note.route("/on/<string:guid>",methods=["GET","POST"])
def get_onenote_note(guid):
    if request.method == "GET":
        return render_template("onenote.view.html",title="Application :: View note",guid=guid)
    else:
        content = ""

    # Checking the request
    forceRefresh = False
    if not guid or guid == "":
        abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})
    
    data = request.get_json()
    if not data:
        abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})
    forceRefresh = data['refresh']            

    # Getting access token
    access_token = get_access_token(safeglobals.service_onenote)
    if access_token == "":
        abort(safeglobals.http_bad_request,{"message":safeglobals.ERROR_NO_TOKEN})               

    # Downloading note
    page = Safenote()
    page = get_page(access_token,guid,forceRefresh)

    # Sending response
    return jsonify(note={"title":page.title,"content":page.render(safeglobals.service_onenote),\
        "favourite":page.is_favourite(),"backup":page.is_backed_up(),"encrypted":page.is_encrypted()})

    