from flask import Blueprint, jsonify,abort,request,render_template
import getpass
import config
from libs.functions import encryptString, decryptString,convert_size,get_folder_size
import os



# Initializing the blueprint
mod_settings = Blueprint("mod_settings",__name__)


# Routes
@mod_settings.route("/",methods=['GET'])
def show_page():
    return render_template("settings.html",title="Settings")

@mod_settings.route("/cache",methods=["GET"])
def cache_status():
    notebook_total = 0
    evernote_notebooks = 0
    onenote_notebooks = 0
    response = {}
	
	# Calculating the size of "notebooks.json" file in Kb
    if os.path.exists(config.path_notebooks_evernote) == False:
        evernote_notebooks = 0;
    else:
		evernote_notebooks = os.path.getsize(config.path_notebooks_evernote)

    if os.path.exists(config.path_notebooks_onenote) == False:
	    onenote_notebooks = 0
    else:
	    onenote_notebooks = os.path.getsize(config.path_notebooks_onenote)

    notebook_total = evernote_notebooks + onenote_notebooks
    response['notebooks'] =  str(convert_size(notebook_total))

    # Calculating the "tags.json"
    size = 0
    if os.path.exists(config.path_tags) == True:
    	size = os.path.getsize(config.path_tags)
    response['tags'] = convert_size(size)

    # Calculating "searches.json" size
    size = 0
    if os.path.exists(config.path_searches) == True:
    	size = os.path.getsize(config.path_searches)
    response['searches'] = convert_size(size)

    # Calculating "sections.json" size
    size = 0
    files = os.listdir(config.path_cache)
    for file in files:
    	if "section" in file:
    		size = size + os.path.getsize(config.path_cache+file)

    # Calculating the size of notes cache
    size = 0
    files = os.listdir(config.path_cache)
    for file in files:
    	if "notes_" in file:
    		size = size + os.path.getsize(config.path_cache+file)
    response['notes'] = convert_size(size)

    # Calculating the size of TMP folder
    size = 0
    if os.path.exists(config.path_tmp) == True:
    	size = get_folder_size(config.path_tmp)

    response['tmp'] = convert_size(size)

    return jsonify(response)



