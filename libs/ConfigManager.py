# Import section
import ConfigParser
import json
from libs.functions import log_message
import safeglobals

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

def get_default_values():

    response = {"system":{},"evernote":{},"onenote":{}}
    
    # Getting general system info
    response['system']['default_service'] = get_value('defaults','default_service','int')

    # Getting Evernote service status, default notebook and default tags
    response['evernote']['status'] = get_value('services','evernote','boolean')
    response['evernote']['default_notebook'] = get_value('defaults','default_evernote_notebook','string')
    response['evernote']['token'] = {}
    if (get_developer_token() == ""):
        response['evernote']['token']['status'] = 0
        response['evernote']['token']['message'] = safeglobals.MSG_NO_DEVTOKEN
    else:
        response['evernote']['token']['status'] = 1
        response['evernote']['token']['message'] = ""

    # Getting default tags (if any)
    response['evernote']['default_tags'] = get_value('defaults','default_tags','string')

    # Getting Onenote 
    response['onenote']['status'] = get_value('services','onenote','boolean')
    response['onenote']['client_id'] = {}
    response['onenote']['client_secret'] = {}
    response['onenote']['redirect_uri'] = {}
    response['onenote']['scopes'] = {}

    # Checking Client ID
    if get_client_id() == "":
        response['onenote']['client_id']['status'] = 0
        response['onenote']['client_id']['message'] = safeglobals.MSG_ONDATA_MISSING
    else:
        response['onenote']['client_id']['status'] = 1
        response['onenote']['client_id']['message'] = ""

    # Checking Client Secret
    if get_client_secret() == "":
        response['onenote']['client_secret']['status'] = 0
        response['onenote']['client_secret']['message'] = safeglobals.MSG_ONDATA_MISSING
    else:
        response['onenote']['client_secret']['status'] = 1
        response['onenote']['client_secret']['message'] = ""

    # Checking Redirect URI
    response['onenote']['redirect_uri'] = get_redirect_uri();
    response['onenote']['scopes'] = get_scopes()
    
    # Getting default section and default notebook
    response['onenote']['default_notebook'] = get_value('defaults','default_onenote_notebook','string')
    response['onenote']['default_section'] = get_value('defaults','default_onenote_section','string')
    return response


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

def save(configString):

    # Parsing JSON config
    configObject = json.loads(configString)

    # Iterating for items
    config = init()
    save_to_ini(config,"",configObject)

def save_to_ini(config,section,d):
    
    # Iterating through all keys and values
    for k, v in d.iteritems():
        if isinstance(v, dict):
            section = k
            save_to_ini(config,section,v)
        else:
            #print "Section: %s, Key: %s, Value: %s" (section,k,v)
            print section+":"+k+":"+v
            config.set(section,k,v)

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