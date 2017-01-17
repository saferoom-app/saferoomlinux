'''
CLI utility used to automate some procedures

'''

# Import section
import argparse,os,safeglobals,binascii
from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import NoteSortOrder, Note, Resource,Data, ResourceAttributes
from libs.ConfigManager import get_access_token
from libs.PasswordManager import get_master_password
from libs.functions import fileMD5,encryptData
from shutil import copyfile
from libs.EvernoteManager import list_notebooks,create_note, list_notes, get_note,update_note,upload_note,get_note_store, get_raw_note
from libs.OnenoteManager import list_on_notebooks,list_sections_all,is_access_token_valid,create_on_note
from libs.texttable import Texttable
from mimetypes import MimeTypes
from libs.safeparser import init_parser
from libs.Safenote import Safenote

# Initializing the parser
new_parser = init_parser()
option = new_parser.parse_args()
check = {}

# Functions section
def list_items(service,type,refresh):
    items = []
    notebooks = []
    sections = []
    if (service == "evernote"):
        if (type == "notebooks"):
            
            # Connecting to Evernote
            access_token = get_access_token()
            note_store = get_note_store(access_token)

            # Loading a list of notebooks
            notebooks = list_notebooks(note_store,access_token,refresh)

            # Collecting items
            for notebook in notebooks:
                items.append({"name":notebook['name'].encode('utf-8'),"guid":notebook['guid'].encode('utf-8'),"parent":"--"})
    
    elif (service == "onenote"):
        if type == "notebooks":
            notebooks = list_on_notebooks(get_access_token(safeglobals.service_onenote),refresh)
            for notebook in notebooks:
                items.append({"name":notebook['text'],"guid":notebook['guid'],"parent":"--"})
        elif type == "sections":
            sections = list_sections_all(get_access_token(safeglobals.service_onenote),refresh)
            for section in sections:
                items.append({"name":section['text'],"guid":section['guid'],"parent":section['parent']})

    # Return items
    return items
def print_title(title):
    print "\n=========================================================="
    print "         %s        " % title
    print "==========================================================\n"
def print_item(max_length,title):
    if (max_length < 32):
        print ("      > {:32s} ......... ").format(title),
    else:
        print ("      > {:64s} ......... ").format(title),
def get_max_length(items):
    max_length = 0
    for item in filtered_items:
        if len(item.title) > max_length:
            max_length = len(item.title)
    return max_length
def download_notes(note_store,access_token,query):

    # Connecting to Evernote account (getting note store)
    note_store = get_note_store(access_token)

    # Creating ResultSpec and NoteFilter
    noteFilter = NoteFilter(order=NoteSortOrder.UPDATED,notebookGuid=option.container,words=query)
    result_spec = NotesMetadataResultSpec(includeTitle=True,includeCreated=True,includeUpdated=True,includeNotebookGuid=True)
    
    # Getting the result
    print("    "+safeglobals.MSG_DOWNLOAD_NOTES+" ......"),
    response = note_store.findNotesMetadata(access_token, noteFilter, safeglobals.evernote_offset, safeglobals.evernote_maxnotes, result_spec)
    print safeglobals.MSG_LABEL_OK

    # Sending response
    return response
def print_error(message):
    print "\n     %s\n" % message        


# Checking Master password
print_title(safeglobals.TITLE_PRELIM_CHECK)

print("\n    {:36s} ......").format(safeglobals.MSG_PASSWORD_CHECK),
check['master_password'] = (get_master_password() != "")
if check['master_password'] == True:
	print safeglobals.MSG_LABEL_OK
else:
	print safeglobals.MSG_LABEL_NOK

# Checking Evernote developer token
print("    {:36s} ......").format(safeglobals.MSG_TOKEN_CHECK % "Evernote"),
check['developer_token'] = (get_access_token() != "")
if check['developer_token'] == True:
	print safeglobals.MSG_LABEL_OK
else:
	print safeglobals.MSG_LABEL_NOK

# Checking Onenote tokens
print("    {:36s} ......").format(safeglobals.MSG_TOKEN_CHECK % "Onenote"),
check['onenote_token'] = is_access_token_valid()
if check['onenote_token'] == True:
	print safeglobals.MSG_LABEL_OK
else:
	print safeglobals.MSG_LABEL_NOK


# Executing command
if option.which == "encrypt":
    
    # Printint the title
    print_title(safeglobals.TITLE_ENCRYPT_FILE)

    # Checking files to be encrypted
    attachments = []
    files = option.file.split(",")
    for file in files:
        if os.path.isfile(file) == True:
            attachments.append(file)
        else:
            print "    "+safeglobals.MSG_FILE_NOTFOUND % (file)
            exit()


    # Copying file to Saferoom temp folder
    print("\n    "+safeglobals.MSG_COPY_TOTMP+" ......"),
    for file in attachments:
        dst_path = os.path.join(os.getcwd(),safeglobals.path_tmp,os.path.basename(file))
        copyfile(file,dst_path)
        if os.path.isfile(dst_path) == False:
            print safeglobals.MSG_LABEL_NOK + msg_copy_error
    print safeglobals.MSG_LABEL_OK

    # Calculating original file hash (this is needed for Evernote and Onenote services)
    mime_type = MimeTypes()
    fileList = []
    for file in attachments:
        dst_path = os.path.join(os.getcwd(),safeglobals.path_tmp,os.path.basename(file))
        fileList.append({"name":os.path.basename(file),"hash":fileMD5(dst_path),"mime":mime_type.guess_type(file)[0]})
    
    # Checking password
    print("    %s ......" % safeglobals.MSG_CREATE_NOTE),
    if option.mode == "master":
        if check['master_password'] == False:
            print safeglobals.MSG_LABEL_NOK+"    "+msg_masterpass_notfound
            exit()
        password = get_master_password()
    elif option.mode == "otp":
        if option.key == "":
            print safeglobals.MSG_LABEL_NOK+"    "+msg_otppass_notfound
            exit()
        password = option.key

    # Checking the access token
    service = safeglobals.service_evernote
    if (option.service == "onenote"):
        service = safeglobals.service_onenote
    access_token = get_access_token(service)

    # Creating note
    note = Safenote()
    note.title = option.title
    note.notebookGuid = option.container
    note.resources = []
    hashes = []
    content = []
    for file in fileList:
        dst_path = os.path.join(os.getcwd(),safeglobals.path_tmp,os.path.basename(file['name']))
        print dst_path
        note.resources.append(Safenote.create_resource(dst_path))
        hashes.append(file['hash'])
    
    # Creating a note
    if option.service == "evernote":

        # Creating content
        for resource in note.resources:
            content.append("<en-media type=\"%s\" hash=\"%s\"/><br/>" \
                % (resource.mime,binascii.hexlify(resource.data.bodyHash)))
        note.content = "".join(content)

        # Encrypting note
        note.encrypt(password)

        # Connecting to Evernote
        note_store = get_note_store(access_token)

        # Uploading the note to server
        upload_note(note_store,access_token,note) 

    elif option.service == "onenote":
        
        for resource in note.resources:
            if "image" in resource.mime:
                content.append("<img src='name:%s' data-filename='%s' />" % (binascii.hexlify(resource.data.bodyHash,resource.attributes.fileName)))
            else:
                content.append("<object data-attachment='%s' data='name:%s' type='%s'/>" % (resource.attributes.fileName,binascii.hexlify(resource.data.bodyHash),resource.mime))

        # Setting content
        note.content = "".join(content)

        # Encrypting the note
        note.encrypt(password,service=safeglobals.service_onenote)

        # Creating encrypted page
        create_on_note(access_token,note,hashes)

    print safeglobals.MSG_LABEL_OK
        
elif option.which == "list":
    # Checking the developer token
    if option.service == "evernote" and check['developer_token'] == False:
        print_error(safeglobals.ERROR_NO_TOKEN)
        exit()

    # Checking the Onenote access tokens
    if option.service == "onenote" and check['onenote_token'] == False:
    	print_error(safeglobals.ERROR_NO_TOKEN)
        exit()

    # Getting items
    items = list_items(option.service,option.type,option.refresh)
    filtered_items = filter(lambda d: option.name in d['name'], items)
        
    # Displaying a table
    parent = "--"
    table = Texttable()
    table.set_cols_align(["c", "c","c"])
    table.set_cols_valign(["m", "m","m"])
    table.add_row(["Name", "GUID","Parent"])
    for item in filtered_items:
        table.add_row([item['name'].encode("utf-8"),\
            item['guid'].encode("utf-8"),\
            item['parent']])
    print table.draw()

elif option.which == "notes":

    # Checking the access token
    access_token = get_access_token()
    if not access_token:
        print_error(safeglobals.ERROR_NO_TOKEN)
        exit()

    # Connecting to Evernote server
    note_store = get_note_store(access_token)

    if option.operation == "list":
        
        # Getting the list of notes
        data = list_notes(accessToken=access_token,forceRefresh=True,type="notebook",guid=option.container)

        # Processing the list of notes
        print data
        filtered_items = filter(lambda d: option.name in d['title'], data)
        
        # Displaying a table
        parent = "--"
        table = Texttable()
        table.set_cols_align(["c", "c"])
        table.set_cols_valign(["m", "m"])
        table.add_row(["Name", "GUID"])
        for item in filtered_items:
            table.add_row([item['title'].encode("utf-8"),\
                item['guid'].encode("utf-8")])

        print table.draw() 

    elif option.operation == "encrypt":

        # Getting the list of notes
        response = download_notes(note_store,access_token,"-"+safeglobals.ENCRYPTED_PREFIX[:-2])
        
        # Processing the list of notes
        filtered_items = filter(lambda d: option.guid in d.guid, response.notes)
        max_length = get_max_length(filtered_items)
        
        # First, we need to download and backup all the notes
        print_title(safeglobals.TITLE_DOWNLOAD_BACKUP_NOTES)
        for item in filtered_items:
            
            # Getting the note content
            print_item(max_length,item.title)
            note = get_note(note_store,access_token,item.guid)
            print safeglobals.MSG_LABEL_DONE

            # Backing up the downloaded note
            note.backup()

        # Checking that all backups have been created
        print_title(safeglobals.TITLE_CHECK_BACKUPS)
        print("    "+safeglobals.MSG_BACKUP_CHECK+" ......"),
        for item in filtered_items:
            if os.path.isfile(safeglobals.path_notes_backup % item.guid) == False:
                print safeglobals.MSG_LABEL_NOK + "\n" + safeglobals.ERROR_NO_BACKUP % item.guid
                exit()
        print safeglobals.MSG_LABEL_OK+"\n    "+(safeglobals.MSG_BACKUP_CREATED % safeglobals.path_notes_backup).replace("%s","<guid>")+"\n"


        # Starting to encrypt notes
        print_title(safeglobals.TITLE_ENCRYPT_NOTES)
        if len(filtered_items) == 0:
            print "\n    [INFO]: "+safeglobals.MSG_NOENCRYPTED_NOTES+"\n"
            exit()
        
        note = None
        for item in filtered_items:
            
            # Getting the note content
            print_item(max_length,item.title)
            try:
                # Instead of loading the note once again, we are reading it from the backup
                note = Safenote.get_from_backup(item.guid)

                # Getting password
                password = get_master_password()
                if option.password != "":
                    password = option.password

                # Encrypting the note
                note.encrypt()
                
                # Uploading the note to Evernote server
                update_note(note_store,access_token,note)
                print safeglobals.MSG_LABEL_OK

            except Exception as e:
                print "[NOK]\n\n    [ERROR]:"+e.message
        exit()

    elif option.operation == "restore":
                
        # Creating ResultSpec and NoteFilter
        response = download_notes(note_store,access_token,safeglobals.ENCRYPTED_PREFIX[:-2])
        
        # Processing the list of notes
        filtered_items = filter(lambda d: option.guid in d.guid, response.notes)
        max_length = get_max_length(filtered_items)

        # Checking that all notes have the backup and restore from this backup
        
        print_title(safeglobals.TITLE_RESTORE_NOTES)
        note = Safenote()
        for item in filtered_items:
            print_item(max_length,item.title)
            note.guid = item.guid
            
            # Checking if not is backed up
            if note.is_backed_up() == False:
                print safeglobals.ERROR_BACKUP_NOK
            else:               
                # Getting the note from the backup
                note = Safenote.get_from_backup(item.guid)

                # Updating the note
                update_note(note_store,access_token,note)
                print safeglobals.MSG_LABEL_OK
        exit()
    
    elif option.operation == "reencrypt":

        # Checking that passwords have been provided
        if not option.password or not option.oldpassword:
            print msg_no_passwords
            exit()
        
        # Creating ResultSpec and NoteFilter
        response = download_notes(note_store,access_token,safeglobals.ENCRYPTED_PREFIX[:-2])

        # Processing the list of notes
        filtered_items = filter(lambda d: option.guid in d.guid, response.notes)
        max_length = get_max_length(filtered_items)

        # First we need to decrypt using the supplied password
        print_title(safeglobals.TITLE_REENCRYPT_NOTES)
        note = Safenote()
        for item in filtered_items:
            
            print_item(max_length,item.title)
            # Downloading the note
            note = get_note(note_store,access_token,item.guid,True)

            # Decrypting the note
            try:
                note.content = Safenote.get_content(note.content)
                note.decrypt(option.oldpassword)
            except Exception as e:
                print safeglobals.MSG_DECRYPT_ERROR
                continue

            # Encrypt the note with a new password
            note.encrypt(option.password)

            # Updating the note (temp, for checking)
            update_note(note_store,access_token,note)
            print safeglobals.MSG_LABEL_OK

        exit()

    else:
        print "Unsupported operation"
        exit()

elif option.which == "decrypt":
	exit()