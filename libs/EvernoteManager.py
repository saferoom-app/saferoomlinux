from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import NoteSortOrder, Note, Resource,Data, ResourceAttributes
import json
from libs.functions import millisToDate,str_to_bool,stringMD5,encryptNote, encryptData
import os
import evernote.edam.userstore.constants as UserStoreConstants
from evernote.edam.error.ttypes import EDAMUserException, EDAMSystemException, EDAMNotFoundException,EDAMErrorCode
import hashlib
import binascii
import base64
import config
from libs.FavouritesManager import is_favourite


'''
  ============================================================
            Notebooks functions
  ============================================================
'''

# Function used to get the list of notebooks
def list_notebooks(accessToken,forceRefresh):
    notebooks = []
    if forceRefresh == True:
        notebooks = load_notebooks(accessToken)
        return notebooks

    # Checking if notebooks are cached
    try:
        f = open("cache/notebooks.json","rb")
        notebooks = json.loads(f.read())
        f.close()
    except Exception as e:
        notebooks = load_notebooks(accessToken)

    return notebooks


# Function used to load the list of notebooks from Evernote server
def load_notebooks(accessToken):
    
    # Connecting to Evernote client
    notebooks = []
    client = EvernoteClient(token=accessToken,sandbox=False)
    noteStore = client.get_note_store()
    response = noteStore.listNotebooks()
    for notebook in response:
        notebooks.append({"name":unicode(notebook.name, "utf8"),"guid":unicode(notebook.guid, "utf8")})

    # Saving notebooks to cache
    cache_notebooks(notebooks)

    return notebooks
    

def cache_notebooks(notebooks):
    f = open("cache/notebooks.json","w")
    f.write(json.dumps(notebooks))
    f.close()



'''
  ============================================================
            Notes functions
  ============================================================
'''

def list_notes(accessToken,forceRefresh,type,guid):

    # Initializing variables
    notes = []
    #print forceRefresh
    # Checking if the notes for specified GUID have been cached
    if (str_to_bool(forceRefresh) == True):
    	print "Loaded from Evernote"
        notes = load_notes(accessToken,type,guid)
        return notes    
    try:
        if (type == "search"):
            filename = "cache/"+stringMD5(guid)+"_"+type+".json"
        else:
            filename = "cache/"+guid+"_"+type+".json"        
        f = open(filename,"r")
        notes = json.loads(f.read())
        f.close()
    except:
        notes = load_notes(accessToken,type,guid)

    return notes


def load_notes(accessToken,type,guid):

	# Connecting to Evernote
    notes = []
    offset = 0
    maxNotes = 100
    client = EvernoteClient(token=accessToken,sandbox=False)
    note_store = client.get_note_store()

    # Creating NoteFilter
    if (type == "search"):
    	noteFilter = NoteFilter(order=NoteSortOrder.UPDATED,words=guid)
    elif (type == "tag"):
    	noteFilter = NoteFilter(order=NoteSortOrder.UPDATED,tagGuids=[guid])
    else:
    	noteFilter = NoteFilter(order=NoteSortOrder.UPDATED,notebookGuid=guid)

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
        filename = "cache/"+stringMD5(guid)+"_"+type+".json"
    else:
        filename = "cache/"+guid+"_"+type+".json"
    f = open(filename,"w")
    f.write(json.dumps(notes))
    f.close()


'''
  ============================================================
            Tags functions
  ============================================================
'''


def list_tags(accessToken,forceRefresh):

    tags = []
    if (str_to_bool(forceRefresh) == True):
        tags = loadTags(accessToken)
        return tags

    # Checking cache
    try:
        f = open("cache/tags.json")
        tags = json.loads(f.read())
        f.close()
    except:
        tags = loadTags(accessToken)

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
    f = open("cache/tags.json","w")
    f.write(json.dumps(tags))
    f.close()

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
        f = open("cache/searches.json")
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

    return tags


def cacheSearches(searches):
    f = open("cache/searches.json","w")
    f.write(json.dumps(searches))
    f.close()

'''
  ============================================================
            Note Management functions
  ============================================================
'''
def get_note(accessToken,guid,forceRefresh):

    # Checking forceRefresh
    if (str_to_bool(forceRefresh) == True):
        note = download_note(accessToken,guid)
        return 

    # Checking if note is cached
    try:
        f = open("notes/"+guid+"/content.json")
        note = json.loads(f.read())
        f.close()
    except:
        note = download_note(accessToken,guid)

    # Checking if it is in favourites
    note['favourite'] = is_favourite(guid)

    return note


def download_note(accessToken,guid):

    # Connecting to Evernote
    note = {}
    client = EvernoteClient(token=accessToken,sandbox=False)
    noteStore = client.get_note_store()


    # Getting specified note
    response = noteStore.getNote(accessToken,guid,True,True,False,False)
    
    # Getting note with all the data
    note = {"title":unicode(response.title, "utf8"),"content":unicode(response.content, "utf8"),"created":millisToDate(response.created),"updated":millisToDate(response.updated)}

    # Saving downloaded resources to temporary folder
    if os.path.exists("notes/"+guid) == False:
        os.makedirs("notes/"+response.guid)

    # Saving content to this folder for faster access
    f = open("notes/"+guid+"/content.json","w")
    f.write(json.dumps(note))
    f.close()


    # Saving resources for faster access
    if (response.resources != None):
        for resource in response.resources:
            with open("notes/"+str(guid)+"/"+str(resource.attributes.fileName),"wb") as f:
                f.write(resource.data.body)
    
    return note


def create_note(accessToken,title,content,notebookGuid,files,tags):

    # Generating note body
    content = config.ENCRYPTED_PREFIX+stringMD5(content)+"__"+encryptNote(content,"testtest")+config.ENCRYPTED_SUFFIX
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
                binaryData = encryptData(f.read(),"testtest")
                md5 = hashlib.md5()
                md5.update(binaryData)
                hash = md5.digest()

                # Creating Evernote data object
                
                data = Data()
                data.size = len(binaryData)
                data.bodyHash = hash
                data.body = binaryData
                print binascii.hexlify(hash)

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

    
    try:
        # Connecting to Evernote
        client = EvernoteClient(token=accessToken,sandbox=False)
        noteStore = client.get_note_store()
        noteStore.createNote(accessToken,note)
    except EDAMUserException, edue:
        print "EDAMUserException:", edue
        return None
    except EDAMNotFoundException, endfe:
        print "EDAMNotFoundException: Invalid parent notebook GUID"
        return None
    
    return note
