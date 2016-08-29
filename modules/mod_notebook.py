# Import section
from flask import Blueprint, jsonify,abort,request,render_template
from libs.EvernoteManager import list_notebooks
from libs.OnenoteManager import list_on_notebooks,get_access_token,list_sections
import config
from libs.functions import str_to_bool,log_message

# Initializing the blueprint
mod_notebook = Blueprint("mod_notebook",__name__)

# Initializing "notebooks" route
@mod_notebook.route("/list/<string:responseType>")
def notebooks(responseType):
    try:

        forceRefresh = False
        if request.args.get("refresh"):
            forceRefresh = str_to_bool(request.args.get("refresh"))
            
        # Getting a list of notebooks
        notebooks = list_notebooks(config.ACCESS_TOKEN,forceRefresh)

        # Returning response based on specified format
        if responseType == "json":
            return jsonify(notebooks)
        elif responseType == "select":
            return render_template("select.notebooks.html",notebooks=notebooks)
        else:
            return render_template('list.notebooks.html',notebooks=notebooks)
    except:
        raise

@mod_notebook.route("/on/list/<string:responseType>",methods=["GET"])
def list_onenote_notebooks(responseType):
    forceRefresh = False
    if request.args.get("refresh"):
        forceRefresh = str_to_bool(request.args.get("refresh"))

    # Listing the Onenote notebooks
    access_token = get_access_token()
    notebooks = list_on_notebooks(access_token,False)
    
    # Returning response based on specified format
    if responseType == "json":
        return jsonify(notebooks)
    elif responseType == "select":
        return render_template("select.notebooks.html",notebooks=notebooks)
    else:
        return render_template('list.notebooks.html',notebooks=notebooks)


@mod_notebook.route("/on/sections/<string:guid>/<string:responseType>",methods=["GET"])
def list_on_sections(guid,responseType):
    forceRefresh = False
    if request.args.get("refresh"):
        forceRefresh = str_to_bool(request.args.get("refresh"))

    # Getting a list of sections
    access_token = get_access_token()
    sections = list_sections(access_token,False,guid)

    # Returning response based on specified format
    if responseType == "json":
        return jsonify(sections)
    elif responseType == "select":
        return render_template("select.notebooks.html",notebooks=notebooks)
    else:
        return render_template('list.notebooks.html',notebooks=notebooks)