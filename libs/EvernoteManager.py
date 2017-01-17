from flask import render_template,jsonify
from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import NoteSortOrder, Note, Resource,Data, ResourceAttributes
from libs.functions import millisToDate,str_to_bool,stringMD5,encryptNote, encryptData, fileMD5, handle_exception, getMime,getIcon,decryptNote, decryptFileData, is_backed_up
import evernote.edam.userstore.constants as UserStoreConstants
from evernote.edam.error.ttypes import EDAMUserException, EDAMSystemException, EDAMNotFoundException,EDAMErrorCode
import os,json,hashlib,binascii,base64,safeglobals,shutil,copy,pickle
from libs.FavouritesManager import is_favourite
from bs4 import BeautifulSoup, Tag
from libs.ConfigManager import get_access_token
from libs.Safenote import Safenote


'''
  ============================================================
            Store functions
  ============================================================
'''

def get_note_store(access_token):
    client = EvernoteClient(token=access_token,sandbox=False)
    return client.get_note_store()


'''
  ============================================================
            Notebooks functions
  ============================================================
'''

# Function used to get the list of notebooks
def list_notebooks(note_store,accessToken,forceRefresh):
    notebooks = []
    if forceRefresh == True:
        notebooks = load_notebooks(note_store,accessToken)
        return notebooks

    # Checking if notebooks are cached
    try:
        f = open("cache/notebooks.json","rb")
        notebooks = json.loads(f.read())
        f.close()
    except Exception as e:
        notebooks = load_notebooks(note_store,accessToken)

    return notebooks

# Function used to load the list of notebooks from Evernote server
def load_notebooks(note_store,accessToken):
    
    # Connecting to Evernote client
    notebooks = []
    response = note_store.listNotebooks()
    for notebook in response:
        notebooks.append({"name":unicode(notebook.name, "utf8"),"guid":unicode(notebook.guid, "utf8"),"service":safeglobals.service_evernote})

    # Saving notebooks to cache
    cache_notebooks(notebooks)

    return notebooks

def cache_notebooks(notebooks):
    f = open(safeglobals.path_notebooks_evernote,"w")
    f.write(json.dumps(notebooks))
    f.close()


'''
  ============================================================
            Notes functions
  ============================================================
'''

def list_notes(note_store,accessToken,forceRefresh,type,guid,display):

    # Initializing variables
    notes = []
    
    # Checking if the notes for specified GUID have been cached
    if forceRefresh == True:
    	notes = load_notes(note_store,accessToken,type,guid,display)
        return notes    
    try:
        if (type == "search"):
            filename = safeglobals.path_notes_evernote % (stringMD5(guid),type)
        else:
            filename = safeglobals.path_notes_evernote % (guid,type)        
        with open(filename,"r") as f:
            notes = json.loads(f.read())
    except:
        notes = load_notes(note_store,accessToken,type,guid,display)

    return notes

def load_notes(note_store,accessToken,type,guid,display):

	# Connecting to Evernote
    notes = []
    offset = 0
    maxNotes = 100
    # Creating NoteFilter
    if (type == "search"):
    	noteFilter = NoteFilter(order=NoteSortOrder.UPDATED,words=guid)
    elif (type == "tag"):
    	noteFilter = NoteFilter(order=NoteSortOrder.UPDATED,tagGuids=[guid])
    else:
    	noteFilter = NoteFilter(order=NoteSortOrder.UPDATED,notebookGuid=guid)

        if int(display) == safeglobals.NOTES_ENCRYPTED_ONLY:
            noteFilter.words = safeglobals.ENCRYPTED_PREFIX[:-2]
        elif int(display) == safeglobals.NOTES_UNENCRYPTED_ONLY:
            noteFilter.words = "-%s" % safeglobals.ENCRYPTED_PREFIX[:-2]

    # Creating ResultSpec
    result_spec = NotesMetadataResultSpec(includeTitle=True,includeCreated=True,includeUpdated=True,includeNotebookGuid=True)
    
    # Getting the result
    response = note_store.findNotesMetadata(accessToken, noteFilter, offset, maxNotes, result_spec)

    # Parsing the list of NotesMetadata
    for metadata in response.notes:
        notes.append({"guid":metadata.guid,"updated":millisToDate(metadata.updated),"created":millisToDate(metadata.created),"title":metadata.title})

    # Caching notes
    cache_notes(notes,type,guid)
    return notes

def cache_notes(notes,type,guid):

    if (type == "search"):
        filename = safeglobals.path_notes_evernote % (stringMD5(guid),type)
    else:
        filename = safeglobals.path_notes_evernote % (guid,type)
    with open(filename,"w") as f:
        f.write(json.dumps(notes))

def update_note(accessToken,note):

    # Connecting to Evernote
    client = EvernoteClient(token=accessToken,sandbox=False)
    note_store = client.get_note_store()

    # Updating the note
    note_store.updateNote(accessToken,note)


'''
  ============================================================
            Tags functions
  ============================================================
'''


def list_tags(accessToken,forceRefresh):

    tags = []
    if (str_to_bool(forceRefresh) == True):
        tags = load_tags(accessToken)
        return tags

    # Checking cache
    try:
        f = open(safeglobals.path_tags)
        tags = json.loads(f.read())
        f.close()
    except:
        tags = load_tags(accessToken)

    return tags

def load_tags(accessToken):

    # Connecting to Evernote client
    tags = []
    client = EvernoteClient(token=accessToken,sandbox=False)
    noteStore = client.get_note_store()
    response = noteStore.listTags(accessToken)
    for tag in response:
        tags.append({"name":unicode(tag.name, "utf8"),"guid":unicode(tag.guid, "utf8")})

    # Saving notebooks to cache
    cache_tags(tags)
    return tags

def cache_tags(tags):
    with open(safeglobals.path_tags,"w") as f:
        f.write(json.dumps(tags))
'''
  ============================================================
            Saved Searches functions
  ============================================================
'''

def list_searches(accessToken,forceRefresh):

    searches = []
    if (str_to_bool(forceRefresh) == True):
        searches = load_searches(accessToken)
        return searches
    # Checking cache
    try:
        f = open(safeglobals.path_searches)
        searches = json.loads(f.read())
        f.close()
    except:
        searches = load_searches(accessToken)
    return searches

def load_searches(accessToken):

    # Connecting to Evernote client
    searches = []
    client = EvernoteClient(token=accessToken,sandbox=False)
    noteStore = client.get_note_store()
    response = noteStore.listSearches(accessToken)
    for search in response:
        searches.append({"name":unicode(search.name, "utf8"),"guid":unicode(search.guid, "utf8"),"query":unicode(search.query, "utf8")})

    # Saving notebooks to cache
    cacheSearches(searches)
    return searches

def cacheSearches(searches):
    with open(safeglobals.path_searches,"w") as f:
        f.write(json.dumps(searches))   

'''
  ============================================================
            Note Management functions
  ============================================================
'''

# Getting the raw note from the Evernote server
def get_raw_note(note_store,access_token,guid):
    try:
        return note_store.getNote(access_token,guid,True,True,False,False)
    except:
        return None     

# Getting the processed note from Evernote server (either from cache or from the server)
def get_note(note_store,access_token,guid,forceRefresh):

    note = Safenote()

    # Checking forceRefresh
    if (forceRefresh == True):
        note = download_note(note_store,access_token,guid)

    # Checking if note is cached
    note = Safenote.get_from_backup(guid,path=safeglobals.path_note_backup)
    if not note:
        note = download_note(note_store,access_token,guid)
   
    return note

# Download the note from Evernote server and process it for proper display in Saferoom app
def download_note(note_store,access_token,guid):

    # Getting raw note from Evernote
    response = get_raw_note(note_store,access_token,guid)
    response.__class__ = Safenote

    # Backing up the note
    response.backup(safeglobals.path_note_backup)
    
    return response

# Caching the note
def cache_note(note):
    # Saving downloaded resources to temporary folder
    if os.path.exists(safeglobals.path_note % (note['guid'],"")) == False:
        os.makedirs(safeglobals.path_note % (note['guid'],""))

    # Saving content to this folder for faster access
    with open(safeglobals.path_note % (note['guid'],"content.json"),"w") as f:
        f.write(json.dumps(note))

# Creating a new note based on user's provided data
def create_note(accessToken,title,content,notebookGuid,files,tags,password):

    # Generating note body
    content = safeglobals.ENCRYPTED_PREFIX+stringMD5(content)+"__"+encryptNote(content,password)+safeglobals.ENCRYPTED_SUFFIX
    nBody = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    nBody += "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
    nBody += "<en-note>%s</en-note>" % content
    tagNames = []

    # Creating note object
    note = Note()
    note.title = title.strip()
    note.content = nBody
    note.notebookGuid = notebookGuid
    for tag in tags:
        tagNames.append(str(tag).strip())
    note.tagNames = tagNames

    # Processing resources
    resources = []
    for file in files:
        if (file.get('name') and file.get('mime')):
            with open("static/tmp/"+file.get('name'),"rb") as f:
                
                # Calculating hash
                binaryData = encryptData(f.read(),password)
                md5 = hashlib.md5()
                md5.update(binaryData)
                hash = md5.digest()

                # Creating Evernote data object
                
                data = Data()
                data.size = len(binaryData)
                data.bodyHash = hash
                data.body = binaryData

                # Creating resource
                resource = Resource()
                resource.mime = file.get('mime')
                resource.data = data

                # Creating attributes
                attributes = ResourceAttributes()
                attributes.fileName = file.get('name')

                # Adding the resource to resource collection
                resource.attributes = attributes
                resources.append(resource)

    note.resources = resources
    return note

def render_note(guid):
    '''
        Function used to render the Evernote note into HTML readable format. The rendering consists of the following steps. 

        1. Checking if the note has been successfully saved on the local machine (every note is automatically saved on local machine for faster access)

        2. Checking if the "content.json" file is there. If it is there, read the content

        3. Getting a list of attachments and calculating their hashes

        4. Inserting the attachments as the clickable links into a page content

        Return: dictionary with status, message and note object 
    '''
    # Step 1. Checking the note has been saved on the local machine
    if os.path.exists(safeglobals.path_note % (guid,"")) == False:
        return {"status":safeglobals.http_not_found,\
        "note":None, \
        "message":safeglobals.MSG_NOTE_MISSING % safeglobals.path_note % (guid,"")}

    # Step 2. Check if the "content.json" is there. If true, reading its content
    if os.path.isfile(safeglobals.path_note % (guid,"content.json")) == False:
        return {"status":safeglobals.http_not_found,\
        "note":None, \
        "message":safeglobals.MSG_NOTE_MISSING % safeglobals.path_note % (guid,"content.json")}        

    # Reading the "content.json"
    note = None
    with open(safeglobals.path_note % (guid,"content.json"),"r") as f:
        note = json.loads(f.read())
    
    # Checking if note is encrypted or not
    if safeglobals.ENCRYPTED_SUFFIX in note['content']:
        note['content'] = render_template("page.encrypted.html",service=safeglobals.service_evernote)
        note['encrypted'] = True
    else:
        # Step 3. Getting a list of attachments (if any)
        resources = []
        path = safeglobals.path_note % (guid,"")
        for filename in os.listdir(path):
            if "content.json" not in filename:           
                # Adding to the list of resources
                resources.append({"name":filename,\
                    "hash":fileMD5(os.path.join(path,filename)),\
                    "mime":getMime(os.path.join(path,filename))})
                


        # Step 4. Rendering the note content
        note['content'] = prepare_content(note['content'],resources,path="/static/tmp/"+guid+"/")
        note['encrypted'] = False

    # Checking if the note is in Favourites and whether it is backed up
    note['favourite'] = is_favourite(guid)
    note['backup'] = is_backed_up(guid)


    # Sending the response
    return {"status":safeglobals.http_ok,"note":note, "message":""}

def prepare_content(content,resources,path="/static/tmp/"):
    '''
        Function used to generate readable HTML content from Evernote note content and its resources

        Input:
            > content: Note content
            > resources: List of resources attached to this note

        Returns:
            note content in readable HTML format

    '''

    # Finding all <en-media> tags within the note content
    content = content.split("<en-note>")[-1].replace("</en-note>","")
    soup = BeautifulSoup(content,"html.parser")
    tag = None
    matches =  soup.find_all('en-media')

    # Listing all resources
    for match in matches:
        for resource in resources:
            if resource['hash'] == match['hash'] or resource['hash'].upper() == match['hash'].upper():
                if "image" in match['type']:
                        tag = soup.new_tag('img',style="width:100%",src=path+resource['name'])
                elif safeglobals.MIME_PDF in match['type']:                        
                        tag = soup.new_tag("embed",width="100%", height="500",src=path+resource['name']+"#page=1&zoom=50")

                elif "application" in match['type']:
                    # Creating root div
                    tag = soup.new_tag("div",**{"class":"attachment"})

                    # Creating ICON span tag
                    icon_span_tag = soup.new_tag("span",style="margin-left:10px")
                    icon_img_tag = soup.new_tag("img",src="/static/images/"+getIcon(resource['mime']))
                    icon_span_tag.append(icon_img_tag)

                    # Creating text tag
                    text_span_tag = soup.new_tag("span",style="margin-left:10px")
                    text_a_tag = soup.new_tag("a",href=path+resource['name'])
                    text_a_tag.string = resource['name']
                    text_span_tag.append(text_a_tag)

                    # Creating DIV with two spans
                    div_col_10 = soup.new_tag("div",style="display:inline-block",**{"class":"col-md-10"})
                    div_col_10.append(icon_span_tag)
                    div_col_10.append(text_span_tag)

                    # Creating div(col-md-2)
                    div_col_2 = soup.new_tag("div",**{"class":"col-md-2"})

                    # Creating div row
                    div_row = soup.new_tag("div",**{"class":"row"})
                    div_row.append(div_col_10)
                    div_row.append(div_col_2)

                    # Combining all together
                    tag.append(div_row)

                match.replaceWith(tag)

    content = soup.prettify()
    content = content.replace("></embed>","/>")
    return content

def encrypt_note(note,password):
    
    # Encrypting the content with provided password and generating a new body
    content = note.content.split("<en-note>")[-1].replace("</en-note>","")
    content = safeglobals.ENCRYPTED_PREFIX+stringMD5(content)+"__"+encryptNote(content,password)+safeglobals.ENCRYPTED_SUFFIX
       
    note.content = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    note.content+= "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
    note.content+= "<en-note>%s</en-note>" % content

    # Encrypting resources
    binaryData = None
    hash = None
    encrypted_resources = []
    encrypted_resource = None
    if (note.resources != None):
        for resource in note.resources:
            
            encrypted_resource = copy.deepcopy(resource)
            # Encrypting the data
            binaryData = encryptData(resource.data.body,password)
            md5 = hashlib.md5()
            md5.update(binaryData)
            hash = md5.digest()

            # Setting a new data
            encrypted_resource.data.body = binaryData
            encrypted_resource.data.bodyHash = hash
            encrypted_resource.data.size = len(binaryData)

            # Appending to a new encrypted_resources list
            encrypted_resources.append(encrypted_resource)            

    # Updating the note
    note.resources = encrypted_resources
    return note

def decrypt_note(note, password):

    try:
        # Getting the real note content
        content = note.content.split("<en-note>")[-1].replace("</en-note>","")
        
        # Decrypting the content
        content = decryptNote(content,password)
        nBody = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        nBody += "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
        nBody += "<en-note>%s</en-note>" % content
        note.content = nBody
        #print note.content
        
        # Decrypting resources
        decrypted_resources = []
        decrypted_resource = None
        if note.resources != None:
            for resource in note.resources:
                
                # Copying the existing resource into a new object
                decrypted_resource = copy.deepcopy(resource)
                
                # Encrypting the data
                binaryData = decryptFileData(resource.data.body,password)
                md5 = hashlib.md5()
                md5.update(binaryData)
                hash = md5.digest()

                # Setting a new data
                decrypted_resource.data.body = binaryData
                decrypted_resource.data.bodyHash = hash
                decrypted_resource.data.size = len(binaryData)

                # Appending to a new encrypted_resources list
                decrypted_resources.append(decrypted_resource)  
        
        note.resources = decrypted_resources
        return note
    except Exception as e:
        print "[%s]" % e.message
        return None

def backup_note(note):

    '''
        Method creates a backup of a note in [static/tmp/backups] folder. The backup is created using the Python Pickle module used to serialize the objects
    '''
    # Dumping the whole note into PICKLE file
    with open(safeglobals.path_notes_backup % (note.guid),"wb") as f:
        pickle.dump(note,f)

def update_note(note_store,access_token,note):
    note_store.updateNote(access_token,note)

def upload_note(note_store,access_token,note):
    note_store.createNote(access_token,note)

def get_from_backup(guid):
    note = None
    try:
        # Dumping the whole note into PICKLE file
        with open(safeglobals.path_notes_backup % (guid),"rb") as f:
            note = pickle.load(f)
        return note
    except:
        return note