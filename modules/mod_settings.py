from flask import Blueprint, jsonify,abort,request,render_template
import getpass
import safeglobals
from libs.functions import encryptString, decryptString,convert_size,get_folder_size,handle_exception
import os
from libs.ConfigManager import get_services,get_default_values,save



# Initializing the blueprint
mod_settings = Blueprint("mod_settings",__name__)


# Routes
@mod_settings.route("/",methods=['GET'])
def show_page():
    return render_template("settings.html",title="Settings")

@mod_settings.route("/config",methods=["GET"])
def get_config():
    try:
        response = get_default_values()
        return jsonify(response);
    except Exception as e:
        return handle_exception(safeglobals.TYPE_JSON,safeglobals.http_internal_server,str(e))

@mod_settings.route("/save",methods=["POST"])
def save_config():
    try:
        if not request.form['config']:
            return handle_exception(safeglobals.TYPE_JSON,safeglobals.http_bad_request,safeglobals.MSG_MSG_MANDATORY_MISSING)

        # Saving configuration
        save(request.form['config'])

        return jsonify(status=safeglobals.http_ok,message=safeglobals.MSG_CONFIG_OK)

    except Exception as e:
        print e
        return handle_exception(safeglobals.TYPE_JSON,safeglobals.http_internal_server,str(e))


@mod_settings.route("/cache",methods=["GET"])
def cache_status():
    notebook_total = 0
    evernote_notebooks = 0
    onenote_notebooks = 0
    response = {}
	
	# Calculating the size of "notebooks.json" file in Kb
    if os.path.exists(safeglobals.path_notebooks_evernote) == False:
        evernote_notebooks = 0;
    else:
		evernote_notebooks = os.path.getsize(safeglobals.path_notebooks_evernote)

    if os.path.exists(safeglobals.path_notebooks_onenote) == False:
	    onenote_notebooks = 0
    else:
	    onenote_notebooks = os.path.getsize(safeglobals.path_notebooks_onenote)

    notebook_total = evernote_notebooks + onenote_notebooks
    response['notebooks'] =  str(convert_size(notebook_total))

    # Calculating the "tags.json"
    size = 0
    if os.path.exists(safeglobals.path_tags) == True:
    	size = os.path.getsize(safeglobals.path_tags)
    response['tags'] = convert_size(size)

    # Calculating "searches.json" size
    size = 0
    if os.path.exists(safeglobals.path_searches) == True:
    	size = os.path.getsize(safeglobals.path_searches)
    response['searches'] = convert_size(size)

    # Calculating "sections.json" size
    size = 0
    files = os.listdir(safeglobals.path_cache)
    for file in files:
    	if "section" in file:
    		size = size + os.path.getsize(safeglobals.path_cache+file)

    response['sections'] = convert_size(size)

    # Calculating the size of notes cache
    size = 0
    files = os.listdir(safeglobals.path_cache)
    for file in files:
    	if "notes_" in file:
    		size = size + os.path.getsize(safeglobals.path_cache+file)
    response['notes'] = convert_size(size)

    # Calculating the size of TMP folder
    size = 0
    if os.path.exists(safeglobals.path_tmp) == True:
    	size = get_folder_size(safeglobals.path_tmp)

    response['tmp'] = convert_size(size)

    return jsonify(response)



