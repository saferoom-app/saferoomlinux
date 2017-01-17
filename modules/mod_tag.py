# Import section
from flask import Blueprint, jsonify,abort,request,render_template
from libs.EvernoteManager import list_tags
from libs.functions import str_to_bool,handle_exception,send_response
import safeglobals
from libs.ConfigManager import get_access_token

# Initializing the blueprint
mod_tag = Blueprint("mod_tag",__name__)

# Initializing "tags" route
@mod_tag.route("/list/")
def tags():
    
    # Default values
    forceRefresh = False
    responseType = "html"

    # Checking request parameters
    if request.args.get("refresh"):
        forceRefresh = request.args.get("refresh")
    if request.args.get("format"):
        responseType = request.args.get("format")

    # Getting access token
    access_token = get_access_token()
    if access_token == "":
        abort(safeglobals.http_bad_request,{"message":safeglobals.ERROR_NO_TOKEN})

    # Getting a list of tags
    tags = list_tags(access_token,forceRefresh)

    # Returning response based on specified format
    return send_response(tags,responseType,{safeglobals.TYPE_SELECT:"select.tags.html",safeglobals.TYPE_HTML:'list.tags.html'})