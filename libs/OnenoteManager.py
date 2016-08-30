# Import section
import config
import time
import json
import os
import requests
from libs.functions import log_message

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
        f = open(config.path_notebooks_onenote,"r")
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
		r = requests.get(config.url_notebooks,headers=headers)
		if (r.status_code == 401):
			log_message(config.MSG_UNAUTHORIZED)
			return notebooks

		response = json.loads(r.text)
		for notebook in response['value']:
			notebooks.append({"text":"  "+notebook['name'],"href":"/on/sections/"+notebook['id']+"/json","icon": "glyphicon glyphicon-book"})

		# Saving notebooks to cache
		cache_notebooks(notebooks)
		return notebooks

	except Exception as e:
		print e
		return notebooks

		


def cache_notebooks(notebooks):
    f = open(config.path_notebooks_onenote,"w")
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
        f = open(config.path_sections % (guid),"r")
        sections = json.loads(f.read())
        f.close()
    except Exception as e:
        sections = load_sections(accessToken,guid)

    return sections


def load_sections(accessToken,guid):
	sections = []
	try:
		# Creating a POST request
		headers = {"Authorization":"Bearer "+accessToken,"Content-Type":"application/json"}
		r = requests.get(config.url_sections % (guid),headers=headers)
		if (r.status_code == 401):
			log_message(config.MSG_UNAUTHORIZED)
			return sections

		# Getting response
		response = json.loads(r.text)
		for section in response['value']:
			sections.append({"text":"  "+section['name'],"href":"/on/list/"+section['id']+"/list","icon": "glyphicon glyphicon-folder-open"})

		# Saving sections
		cache_sections(guid,sections)

		return sections


	except Exception as e:
		print e
		raise

def cache_sections(guid,sections):
    f = open(config.path_sections % (guid),"w")
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
        f = open(config.path_notes % (guid),"r")
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
		r = requests.get(config.url_notes % (guid),headers=headers)
		if (r.status_code == 401):
			log_message(config.MSG_UNAUTHORIZED+": "+r.text)
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
    f = open(config.path_notes % (guid),"w")
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
		with open(config.path_note % (guid),"r") as f:
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
	r = requests.get(config.url_note_content % (guid),headers=headers)

	# Checking the response (if not 200 or 201 => failure, write to log file)
	if r.status_code == 401:
		log_message(config.MSG_UNAUTHORIZED+": "+r.text)
		return note

	# Processing the response
	note = r.text

	# Saving note to cache for faster load
	cache_note(guid,note)

	# Sending response
	return note

def cache_note(guid,note):
	with open(config.path_note % (guid),"w") as f:
		f.write(note)

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
    with open(config.path_tokens,"w") as f:
    	f.write(json.dumps(tokens))

def is_access_token_valid():

	# Checking that file exists
	if os.path.exists(config.path_tokens) == False:
		return False

	# Checking that Access Token exists in the file
	try:
		with open(config.path_tokens,"r") as f:
			tokens = json.loads(f.read())

		# Checking that token exists and has somve values
		if not tokens['access']:
			return False

		# Checking "expires" key
		if not tokens['expires']:
			return False

		# Checking that Access Token didn't expire
		if is_token_expired(tokens['expires']) == False:
			return False

		return True


	except Exception as e:
		return False


def is_token_expired(expires):
	current = int(time.time())
	return current > int(expires)


def get_access_token():
	try:
		with open(config.path_tokens,"r") as f:
			data = json.loads(f.read())
		return data['access']
	except Exception as e:
		print e
		return ""