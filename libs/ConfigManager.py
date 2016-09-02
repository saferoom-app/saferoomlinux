# Import section
import ConfigParser
import json
from libs.functions import log_message

# Functions

def init():
	config = ConfigParser.RawConfigParser()
	config.read("config.ini")
	return config


def get_services():

    # Initializing config
    config = init()
    # Getting current service status
    services = {}
    services['evernote'] = config.getboolean("services","evernote")
    services['onenote'] = config.getboolean("services","onenote")
    # Return value
    return services

def get_value(section,key,type):
    try:
        # Initializing the config
        config = init()

        if (type == "boolean"):
        	return config.getboolean(section,key)
        elif type == "int":
        	return config.getint(section,key)
        elif type == "float":
        	return config.getfloat(section,key)
        else:
        	return config.get(section,key)
    except Exception as e:
    	log_message(str(e))
    	return None

def set_value(section,key,value):

	# Initializing config
	config = init()

	# Setting value
	config.set(section,key,value)

	# Saving config
	with open("config.ini","w") as configfile:
		config.write(configfile)

def get_developer_token():

    # Getting developer token
    token = get_value('tokens','evernote_developer','string')
    if token == None:
        return ""
    return token

def get_client_id():
    client_id = get_value('tokens','client_id','string')
    if client_id == None:
        return ""
    return client_id

def get_client_secret():
    client_secret = get_value('tokens','client_secret','string')
    if client_secret == None:
        return ""
    return client_secret

def get_scopes():
    scopes = get_value('scopes','scopes','string')
    if scopes == None:
        return ""
    return scopes

def get_redirect_uri():
    redirect_uri = get_value('uris','redirect_uri','string')
    if redirect_uri == None:
        return ""
    return redirect_uri