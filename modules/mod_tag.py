# Import section
from flask import Blueprint, jsonify,abort,request,render_template
from libs.EvernoteManager import list_tags
import config
from libs.functions import str_to_bool,handle_exception

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

        # Getting a list of tags
        tags = list_tags(config.ACCESS_TOKEN,forceRefresh)

        # Returning response based on specified format
        if responseType == "json":
            return jsonify(notebooks)
        elif responseType == "select":
            return render_template("select.tags.html",tags=tags)
        else:
            return render_template('list.tags.html',tags=tags)
    except Exception as e:
        return handle_exception(responseType,config.http_internal_server,str(e))
