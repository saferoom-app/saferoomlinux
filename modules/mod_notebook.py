# Import section
from flask import Blueprint, jsonify,abort,request,render_template
from libs.EvernoteManager import list_notebooks
from libs.OnenoteManager import list_on_notebooks,get_access_token,list_sections,is_access_token_valid
import libs.globals
from libs.functions import str_to_bool,handle_exception
from libs.ConfigManager import get_developer_token

# Initializing the blueprint
mod_notebook = Blueprint("mod_notebook",__name__)

# Initializing "notebooks" route
@mod_notebook.route("/list/<string:responseType>")
def notebooks(responseType):
    try:

        # Checking Access Token
        access_token = get_developer_token()
        if access_token == "":
            return handle_exception(responseType,libs.globals.http_bad_request,libs.globals.MSG_NO_DEVTOKEN)

        forceRefresh = False
        if request.args.get("refresh"):
            forceRefresh = str_to_bool(request.args.get("refresh"))
            
        # Getting a list of notebooks
        notebooks = list_notebooks(access_token,forceRefresh)

        # Returning response based on specified format
        if responseType == libs.globals.TYPE_JSON:
            return jsonify(notebooks)
        elif responseType == libs.globals.TYPE_SELECT:
            return render_template("select.notebooks.html",notebooks=notebooks)
        else:
            return render_template('list.notebooks.html',notebooks=notebooks)
    except Exception as e:
        return handle_exception(responseType,libs.globals.http_internal_server,str(e))

@mod_notebook.route("/on/list/<string:responseType>",methods=["GET"])
def list_onenote_notebooks(responseType):
    forceRefresh = False
    if request.args.get("refresh"):
        forceRefresh = str_to_bool(request.args.get("refresh"))

    # Listing the Onenote notebooks
    if is_access_token_valid() == False:
        if responseType == libs.globals.TYPE_JSON:
            return jsonify(status=libs.globals.http_unauthorized,message=libs.globals.MSG_NO_TOKENS)
        else:
            return render_template("onenote.token.expired.html")
    
    # Getting access token
    access_token = get_access_token()
    notebooks = list_on_notebooks(access_token,False)
    
    # Returning response based on specified format
    if responseType == libs.globals.TYPE_JSON:
        return jsonify(status=200,message=notebooks)
    elif responseType == libs.globals.TYPE_SELECT:
        return render_template("select.notebooks.html",notebooks=notebooks)
    else:
        return render_template('list.notebooks.html',notebooks=notebooks)


@mod_notebook.route("/on/sections/<string:guid>/<string:responseType>",methods=["GET"])
def list_on_sections(guid,responseType):
    forceRefresh = False
    if request.args.get("refresh"):
        forceRefresh = str_to_bool(request.args.get("refresh"))

    # Listing the Onenote notebooks
    if is_access_token_valid() == False:
        if responseType == libs.globals.TYPE_JSON:
            return jsonify(status=libs.globals.http_unauthorized,message=libs.globals.MSG_NO_TOKENS)
        else:
            return render_template("onenote.token.expired.html"),401

    # Getting a list of sections
    access_token = get_access_token()
    sections = list_sections(access_token,False,guid)

    # Returning response based on specified format
    if responseType == libs.globals.TYPE_JSON:
        return jsonify(status=libs.globals.http_ok, message=sections)
    elif responseType == libs.globals.TYPE_SELECT:
        return render_template("select.notebooks.html",notebooks=notebooks)
    else:
        return render_template('list.notebooks.html',notebooks=notebooks)