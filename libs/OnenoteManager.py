# Import section
import safeglobals,time,json,os,requests,uuid,hashlib,binascii
from libs.functions import log_message,stringMD5,log_message,encryptNote, encryptData,fileMD5,getMime,is_backed_up,getIcon
from bs4 import BeautifulSoup
from libs.FavouritesManager import is_favourite
from flask import render_template
from evernote.edam.type.ttypes import NoteSortOrder, Note, Resource,Data, ResourceAttributes
from libs.Safenote import Safenote

'''
  ============================================================
            Notebooks functions
  ============================================================
'''

def list_on_notebooks(accessToken,forceRefresh):
    notebooks = []
    if forceRefresh == True:
        notebooks = load_notebooks(accessToken)
        return notebooks
    # Checking if notebooks are cached
    try:
        f = open(safeglobals.path_notebooks_onenote,"r")
        notebooks = json.loads(f.read())
        f.close()
    except Exception as e:
        notebooks = load_notebooks(accessToken)
    return notebooks

def load_notebooks(accessToken):
	
	notebooks = []
	try:

		# Creating a POST request
		headers = {"Authorization":"Bearer "+accessToken,"Content-Type":"application/json"}
		r = requests.get(safeglobals.url_notebooks,headers=headers)
		if (r.status_code == 401):
			log_message(safeglobals.MSG_UNAUTHORIZED)
			return notebooks

		response = json.loads(r.text)
		for notebook in response['value']:
			notebooks.append({"text":"  "+notebook['name'],"href":"/on/sections/"+notebook['id']+"/json","icon": "glyphicon glyphicon-book","guid":notebook['id']})

		# Saving notebooks to cache
		cache_notebooks(notebooks)
		return notebooks

	except Exception as e:
		log_message(str(e))
		return notebooks

def cache_notebooks(notebooks):
    f = open(safeglobals.path_notebooks_onenote,"w")
    f.write(json.dumps(notebooks))
    f.close()


'''
  ============================================================
            Section functions
  ============================================================
'''

def list_sections(accessToken,forceRefresh,guid):
    sections = []
    if forceRefresh == True:
        sections = load_sections(accessToken,guid)
        return sections

    # Checking if notebooks are cached
    try:
        f = open(safeglobals.path_sections % (guid),"r")
        sections = json.loads(f.read())
        f.close()
    except Exception as e:
        sections = load_sections(accessToken,guid)
    return sections

def load_sections(accessToken,guid):

    sections = []
    
    # Creating a POST request
    headers = {"Authorization":"Bearer "+accessToken,"Content-Type":"application/json"}
    r = requests.get(safeglobals.url_sections % (guid),headers=headers)
    if (r.status_code == 401):
    	log_message(safeglobals.MSG_UNAUTHORIZED)
    	return sections

    # Getting response
    response = json.loads(r.text)
    for section in response['value']:
    	sections.append({"text":"  "+section['name'],"href":"/on/list/"+section['id']+"/list","icon": "glyphicon glyphicon-folder-open","guid":section['id']})

    # Saving sections
    cache_sections(guid,sections)
    return sections

def list_sections_all(access_token,forceRefresh):
    sections = []
    if forceRefresh == True:
        sections = load_sections_all(access_token)
        return sections

    # Checking if notebooks are cached
    try:
        with open(safeglobals.path_sections % ("all"),"r") as f:
            sections = json.loads(f.read())
    except Exception as e:
        sections = load_sections_all(access_token)
    return sections

def load_sections_all(access_token):

    sections = []
    # Creating a POST request
    headers = {"Authorization":"Bearer "+access_token,"Content-Type":"application/json"}
    r = requests.get(safeglobals.url_sections_all,headers=headers)
    if (r.status_code == 401):
        log_message(safeglobals.MSG_UNAUTHORIZED)
        return sections

    # Getting response
    response = json.loads(r.text)
    for section in response['value']:
        sections.append({"parent":section['parentNotebook']['name'],"text":"  "+section['name'],"href":"/on/list/"+section['id']+"/list","icon": "glyphicon glyphicon-folder-open","guid":section['id']})
    
    # Caching sections
    cache_sections("all",sections)

    return sections

def cache_sections(guid,sections):
    f = open(safeglobals.path_sections % (guid),"w")
    f.write(json.dumps(sections))
    f.close()




'''
  ============================================================
            Notes functions (List)
  ============================================================
'''

def list_on_notes(accessToken,forceRefresh,guid):
    notes = []
    if forceRefresh == True:
        notes = load_notes(accessToken,guid)
        return notes

    # Checking if notebooks are cached
    try:
        f = open(safeglobals.path_notes % (guid),"r")
        notes = json.loads(f.read())
        f.close()
    except Exception as e:
        notes = load_notes(accessToken,guid)

    return notes

def load_notes(accessToken,guid):
	notes = []
	try:
		# Creating a POST request
		headers = {"Authorization":"Bearer "+accessToken,"Content-Type":"application/json"}
		r = requests.get(safeglobals.url_notes % (guid),headers=headers)
		if (r.status_code == 401):
			log_message(safeglobals.MSG_UNAUTHORIZED+": "+r.text)
			return notes

		# Getting response
		response = json.loads(r.text)
		for page in response['value']:
			notes.append({"title":page['title'],"guid":page['id'],"created":page['createdTime'],"updated":page['lastModifiedTime']})
		
		# Saving sections
		cache_notes(guid,notes)
		return notes

	except Exception as e:
		print e
		raise

def cache_notes(guid,notes):
    f = open(safeglobals.path_notes % (guid),"w")
    f.write(json.dumps(notes))
    f.close()


'''
  ============================================================
            Note functions (view, encrypt, decrypt)
  ============================================================
'''


def get_page(access_token,guid,forceRefresh):
    page = Safenote()
    if (forceRefresh == True):
        page = download_page(access_token,guid)
    else:
        page = Safenote.get_from_backup(guid,path=safeglobals.path_note_backup)
        if not page:
            page = download_page(access_token,guid)
    return page

def download_page(access_token,guid):

    page = Safenote()

    # Creating custom header for Onenote
    headers = {"Authorization":"Bearer "+access_token,"Content-Type":"application/json"}
    r = requests.get(safeglobals.url_note_content % (guid),headers=headers)

    # Checking the response (if not 200 or 201 => failure, write to log file)
    if r.status_code == 401:
        log_message(safeglobals.MSG_UNAUTHORIZED+": "+r.text)
        return None

    # Processing the response
    page.guid = guid
    page.content = r.text

    # Getting title
    soup = BeautifulSoup(page.content,"html.parser")
    page.title = soup.title.text
    page.resources = download_page_resources(access_token,page.content,page.guid)
    
    # Backing up page
    page.backup(safeglobals.path_note_backup)

    return page

def download_page_resources(access_token,content,guid):

    # Getting note title and content
    soup = BeautifulSoup(content,"html.parser")

    # Getting note resources
    attachments = []
    images = soup.find_all("img")
    for image in images:
        attachments.append({"name":stringMD5(image['src']),"type":image['data-src-type'],"link":image['src']})
    objects = soup.find_all("object")
    for obj in objects:
        attachments.append({"name":obj['data-attachment'],"type":obj['type'],"link":obj['data']})


    # Downloading all resources into tmp folder
    binary_data = None
    hash = None
    resources = []
    tmp_file = os.path.join(safeglobals.path_tmp,"tmp.download")
    headers = {"Authorization":"Bearer "+access_token}
    for attachment in attachments:
        if resource_exists(guid,attachment['name']) == False:
            r = requests.get(attachment['link'],headers=headers,stream=True)
            if r.ok:

                # Writing data to temporary file
                with open(tmp_file,"wb") as f:
                    for block in r.iter_content(512):
                        f.write(block)

                # Calculating hash
                with open(tmp_file,"rb") as f:
                    binary_data = f.read()
                md5 = hashlib.md5()
                md5.update(binary_data)
                hash = md5.digest()

                # Initializing the data
                data = Data()
                data.size = len(binary_data)
                data.bodyHash = hash
                data.body = binary_data

                # Adding data to resource
                resource = Resource()
                resource.mime = attachment['type']
                resource.data = data

                # Creating attributes
                attributes = ResourceAttributes()
                attributes.fileName = os.path.basename(attachment['name'])
                resource.attributes = attributes 

                resources.append(resource)


            else:
                log_message(safeglobals.ERROR_FILE_DOWNLOAD % (str(r.status_code)))

    return resources

def create_on_note(access_token,note,hashes):

    data = None
   
    # First we need to prepare a list of files to upload
    resources = []
    index = 0
    for resource in note.resources:
        
        # Writing encrypted data back to original file
        with open(os.path.join(safeglobals.path_tmp,resource.attributes.fileName),"wb") as f:
            f.write(resource.data.body)

        # Appending file to the list of resources
        resources.append((binascii.hexlify(resource.data.bodyHash),\
            (resource.attributes.fileName,\
            resource.data.body,\
            resource.mime)))

        # Appending to the content, so the files can be uploaded
        if "image" in resource.mime:
            note.content += safeglobals.html_image_template % (binascii.hexlify(resource.data.bodyHash),resource.attributes.fileName)
        else:
            note.content += safeglobals.html_onenote_object % (resource.attributes.fileName,binascii.hexlify(resource.data.bodyHash),resource.mime)

        index = index + 1
    
    resources.append(('Presentation',(None,note.content,'text/html')))
       

    # Preparing POST request
    headers = {"Authorization":"Bearer "+access_token}
    r = requests.post(safeglobals.url_post_page % (note.notebookGuid),headers=headers,files=resources)
    print r.text

def cache_note(guid,note):
    if os.path.exists(safeglobals.path_note % (guid,"")) == False:
        os.makedirs(safeglobals.path_note % (guid,""))
	with open(safeglobals.path_note % (guid,"content.json"), "w") as f:
	    f.write(json.dumps(note))

def render_page(guid):
    
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
        note['content'] = render_template("page.encrypted.html",service=safeglobals.service_onenote)
        note['encrypted'] = True
    else:
        # Step 4. Rendering the note content
        note['content'] = note['content'].replace("></embed>","/>")
        note['encrypted'] = False


    # Checking if the note is in Favourites and whether it is backed up
    note['favourite'] = is_favourite(guid)
    note['backup'] = is_backed_up(guid)
    print note['content']

    # Sending the response
    return {"status":safeglobals.http_ok,"note":note, "message":""}

def backup_page(note):
    # Dumping the whole note into PICKLE file
    with open(safeglobals.path_notes_backup % (note.guid),"wb") as f:
        pickle.dump(note,f)

def init_note(guid,content):

    # Initializing the note object
    note = Note()
    note.content = content
    note.guid = guid

    # Getting note title
    soup = BeautifulSoup(content,"html.parser")
    note.title = soup.title.text

    # Initializing variables
    resources = []
    resource = None
    data = None
    binaryData = None
    hash = None
    
    # Getting note resources
    path = safeglobals.path_note % (guid,"")
    for filename in os.listdir(path):
        if "content.json" not in filename:
            
            # Reading binary data
            with open(os.path.join(path,filename),"rb") as f:
                binaryData = f.read()

            # Calculating hash
            md5 = hashlib.md5()
            md5.update(binaryData)
            hash = md5.digest()

            # Creating data
            data = Data()
            data.size = len(binaryData)
            data.bodyHash = hash
            data.body = binaryData

            # Create a new resource
            resource = Resource()
            resource.mime = getMime(filename)
            resource.data = data

            # Creating attributes
            attributes = ResourceAttributes()
            attributes.fileName = filename

            # Adding the resource to resource collection
            resource.attributes = attributes
            resources.append(resource)

    # Adding resources to the specified note
    note.resources = resources
    return note



'''
  ============================================================
            Token functions
  ============================================================
'''

def save_tokens(responseJson):

    # Calculating the expires time
    current = int(time.time())
    expires_in = int(responseJson['expires_in'])+current

	# Creating the dictionary
    tokens = {"access":responseJson['access_token'],"refresh":responseJson['refresh_token'],"expires":str(expires_in)}

    # Saving tokens into ".tokens" file
    with open(safeglobals.path_tokens,"w") as f:
    	f.write(json.dumps(tokens))

def is_access_token_valid():

	# Checking that file exists
	if os.path.exists(safeglobals.path_tokens) == False:
		return False

	# Checking that Access Token exists in the file
	try:
		with open(safeglobals.path_tokens,"r") as f:
			tokens = json.loads(f.read())

		# Checking that token exists and has somve values
		if not tokens['access']:
			return False

		# Checking "expires" key
		if not tokens['expires']:
			return False

		# Checking that Access Token didn't expire
		if is_token_expired(tokens['expires']) == True:
			return False

		return True


	except Exception as e:
		return False

def is_token_expired(expires):
	current = int(time.time())
	return current > int(expires)

def get_access_token():
    try:
        with open(safeglobals.path_tokens,"r") as f:
            data = json.loads(f.read())
        return data['access']
    except Exception as e:
        return ""

def resource_exists(guid,name):
	return os.path.exists(safeglobals.path_note % (guid,name))