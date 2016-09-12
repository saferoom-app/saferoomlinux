# Import section
from flask import Blueprint, jsonify,abort,request,render_template
from libs.EvernoteManager import list_notebooks
from libs.OnenoteManager import list_on_notebooks,get_access_token,list_sections,is_access_token_valid
import safeglobals
from libs.functions import str_to_bool,handle_exception,send_response
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
            return handle_exception(responseType,safeglobals.http_bad_request,safeglobals.MSG_NO_DEVTOKEN)

        forceRefresh = False
        if request.args.get("refresh"):
            forceRefresh = str_to_bool(request.args.get("refresh"))
            
        # Getting a list of notebooks
        notebooks = list_notebooks(access_token,forceRefresh)

        # Returning response based on specified format
        return send_response(notebooks,responseType,{safeglobals.TYPE_SELECT:"select.notebooks.html",safeglobals.TYPE_HTML:"list.notebooks.html"})
        
    except Exception as e:
        return handle_exception(responseType,safeglobals.http_internal_server,str(e))

@mod_notebook.route("/on/list/<string:responseType>",methods=["GET"])
def list_onenote_notebooks(responseType):
    try:
        forceRefresh = False
        if request.args.get("refresh"):
            forceRefresh = str_to_bool(request.args.get("refresh"))
        # Checking the access token
        if is_access_token_valid() == False:
            if responseType == safeglobals.TYPE_JSON:
                return jsonify(status=safeglobals.http_unauthorized,message=safeglobals.MSG_NO_TOKENS)
            elif responseType == safeglobals.TYPE_SELECT:
                return send_response([{"guid":"","text":"Access token expired or doesn't exist"}],responseType,{"default":"onenote.select.notebooks.html"})
            else:
                return render_template("onenote.token.expired.html")

        # Getting access token and getting a list of notebooks
        access_token = get_access_token()
        notebooks = list_on_notebooks(access_token,forceRefresh)
        
        # Returning response based on specified format
        return send_response(notebooks,responseType,{"default":"onenote.select.notebooks.html"})
        
    except Exception as e:
        return handle_exception(responseType,safeglobals.http_internal_server,str(e))


@mod_notebook.route("/on/sections/<string:guid>/<string:responseType>",methods=["GET"])
def list_on_sections(guid,responseType):
    try:
        forceRefresh = False
        if request.args.get("refresh"):
            forceRefresh = str_to_bool(request.args.get("refresh"))

        # Listing the Onenote notebooks
        if is_access_token_valid() == False:
            if responseType == safeglobals.TYPE_JSON:
                return jsonify(status=safeglobals.http_unauthorized,message=safeglobals.MSG_NO_TOKENS)
            elif responseType == safeglobals.TYPE_SELECT:
                return send_response([{"guid":"","name":"Access token expired or doesn't exist"}],responseType,{"default":"select.sections.html"})
            else:
                return render_template("onenote.token.expired.html"),401

        # Getting a list of sections
        access_token = get_access_token()
        sections = list_sections(access_token,forceRefresh,guid)

        # Returning response based on specified format
        return send_response(sections,responseType,{"default":"select.sections.html"})
        
    except Exception as e:
        return handle_exception(responseType,safeglobals.http_internal_server,str(e))