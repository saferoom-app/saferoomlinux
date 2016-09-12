# Import section
import safeglobals
import time
import json
import os
import requests
from libs.functions import log_message,stringMD5,log_message,encryptNote, encryptData
from bs4 import BeautifulSoup
import uuid

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

def get_on_note(accessToken,guid,forceRefresh):
	note = ""
	if (forceRefresh == True):
		note = download_note(accessToken,guid)

    # Checking if note has been cached already
	try:
		with open(safeglobals.path_note % (guid,"content.json"),"r") as f:
			note = f.read()
		return note
	except:
		# Note is not cached, thus we need to download it
	    note = download_note(accessToken,guid)
       
	return note

def download_note(access_token,guid):
	note = ""

	# Creating custom header for Onenote
	headers = {"Authorization":"Bearer "+access_token,"Content-Type":"application/json"}
	r = requests.get(safeglobals.url_note_content % (guid),headers=headers)

	# Checking the response (if not 200 or 201 => failure, write to log file)
	if r.status_code == 401:
		log_message(safeglobals.MSG_UNAUTHORIZED+": "+r.text)
		return note

	# Processing the response
	note = r.text

	# Saving note
	cache_note(guid,note)

	# Sending response
	return note

def download_resources(access_token,noteContent,guid):
    
    # Getting note title and content
    soup = BeautifulSoup(noteContent,"html.parser")
    
    # Getting note resources
    resources = []
    images = soup.find_all("img")
    for image in images:
        resources.append({"name":stringMD5(image['src']),"type":image['data-src-type'],"link":image['src']})
    objects = soup.find_all("object")
    for obj in objects:
        resources.append({"name":obj['data-attachment'],"type":obj['type'],"link":obj['data']})

    # Downloading all resources into tmp folder
    headers = {"Authorization":"Bearer "+access_token}
    for resource in resources:
    	if resource_exists(guid,resource['name']) == False:
    	    r = requests.get(resource['link'],headers=headers,stream=True)
    	    if r.ok:
    	        with open(safeglobals.path_note % (guid,resource['name']),"wb") as f:
    			    for block in r.iter_content(1024):
    				    f.write(block)
    	    else:
    	    	log_message(safeglobals.ERROR_FILE_DOWNLOAD % (str(r.status_code)))

    # Changing the content
    matches = soup.find_all(['img','object'])
    index = 0
    for match in matches:
    	if "img" in match.name:
    		tag = soup.new_tag('img',style="width:100%",src="/static/tmp/"+guid+"/"+resources[index]['name'])
    	elif "object" in match.name:
    		tag = soup.new_tag('a',href="/static/tmp/"+guid+"/"+resources[index]['name'])
    		tag.string = resources[index]['name']
        match.replaceWith(tag)
        index = index + 1

    # Getting page body 
    matches = soup.find_all("body")
    for match in matches:
        content = match.decode_contents(formatter="html")
        break

    return {"title":soup.title.string,"content":content,"service":safeglobals.service_onenote}

def create_on_note(access_token,title,content,guids,files,password):

    data = None

    # Encrypting note content
    content = safeglobals.ENCRYPTED_PREFIX+stringMD5(content)+"__"+encryptNote(content,password)+safeglobals.ENCRYPTED_SUFFIX    
    nBody = "<html>"
    nBody += "<head><title>%s</title></head>" % (title)
    nBody += "<body>%s</body>" % (content)
    
    # First we need to prepare a list of files to upload
    resources = []
    for file in files:

        # First we need to encrypt these files
        with open(safeglobals.path_tmp+file['name'],"rb") as f:
            data = f.read()

        # Encrypting data
        data = encryptData(data,password)

        # Writing encrypted data back to original file
        with open(safeglobals.path_tmp + file['name'],"wb") as f:
            f.write(data)

        # Appending file to the list of resources
        resources.append((file['hash'],(file['name'],open(safeglobals.path_tmp+file['name'],'rb'),file['mime'])))

        # Appending to the content, so the files can be uploaded
        if "image" in file['mime']:
            nBody += safeglobals.html_onenote_image % (file['hash'])
        else:
            nBody += safeglobals.html_onenote_object % (file['name'],file['hash'],file['mime'])
    
    nBody += "</html>"
    resources.append(('Presentation',(None,nBody,'text/html')))

    # Preparing POST request
    headers = {"Authorization":"Bearer "+access_token}
    r = requests.post(safeglobals.url_post_page % (guids['section']),headers=headers,files=resources)
    print r.text

    

def cache_note(guid,noteContent):
    
    if os.path.exists(safeglobals.path_note % (guid,"")) == False:
        os.makedirs(safeglobals.path_note % (guid,""))
	with open(safeglobals.path_note % (guid,"content.json"), "w") as f:
	    f.write(noteContent) 

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
		print e
		return ""

def resource_exists(guid,name):
	return os.path.exists(safeglobals.path_note % (guid,name))