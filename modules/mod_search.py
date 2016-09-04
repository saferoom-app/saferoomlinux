# Import section
from flask import Blueprint, jsonify,abort,request,render_template
from libs.EvernoteManager import list_searches
import safeglobals
from libs.functions import handle_exception,send_response
from libs.ConfigManager import get_developer_token

# Initializing the blueprint
access_token = ""
mod_search = Blueprint("mod_search",__name__)
# Initializing "tags" route
@mod_search.route("/list/<string:responseType>")
def searches(responseType):
    try:
        # Getting access token
        access_token = get_developer_token()
        if access_token == "":
            return handle_exception(safeglobals.TYPE_HTML,safeglobals.http_bad_request,safeglobals.MSG_NO_DEVTOKEN)        

        # Getting a list of Saved Searches
        searches = list_searches(access_token,False)

        # Returing the response based on specified format
        return send_response(searches,responseType,{safeglobals.TYPE_HTML:'list.searches.html'})

    except Exception as e:
        return handle_exception(responseType,safeglobals.http_internal_server,str(e))
