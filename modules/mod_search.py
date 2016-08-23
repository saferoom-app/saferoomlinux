# Import section
from flask import Blueprint, jsonify,abort,request,render_template
from libs.EvernoteManager import list_searches
import config

# Initializing the blueprint
mod_search = Blueprint("mod_search",__name__)

# Initializing "tags" route
@mod_search.route("/list/<string:responseType>")
def searches(responseType):
    try:
        # Getting a list of Saved Searches
        searches = list_searches(config.ACCESS_TOKEN,False)

        # Returing the response based on specified format
        if responseType == "json":
            return jsonify(searches)
        elif responseType == "select":
            return ""
        else:
            return render_template('list.searches.html',searches=searches)

    except:
        raise
