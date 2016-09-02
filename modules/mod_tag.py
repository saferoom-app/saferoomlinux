# Import section
from flask import Blueprint, jsonify,abort,request,render_template
from libs.EvernoteManager import list_tags
from libs.functions import str_to_bool,handle_exception
import libs.globals
from libs.ConfigManager import get_developer_token

# Initializing the blueprint
mod_tag = Blueprint("mod_tag",__name__)

# Initializing "tags" route
@mod_tag.route("/list/")
def tags():
    try:
        # Default values
        forceRefresh = False
        responseType = "html"

        # Checking request parameters
        if request.args.get("refresh"):
            forceRefresh = request.args.get("refresh")
        if request.args.get("format"):
            responseType = request.args.get("format")

        # Getting access token
        access_token = get_developer_token()
        if access_token == "":
            return handle_exception(responseType,libs.globals.http_bad_request,libs.globals.MSG_NO_DEVTOKEN)

        # Getting a list of tags
        tags = list_tags(access_token,forceRefresh)

        # Returning response based on specified format
        if responseType == libs.globals.TYPE_JSON:
            return jsonify(notebooks)
        elif responseType == libs.globals.TYPE_SELECT:
            return render_template("select.tags.html",tags=tags)
        else:
            return render_template('list.tags.html',tags=tags)
    except Exception as e:
        return handle_exception(responseType,libs.globals.http_internal_server,str(e))
