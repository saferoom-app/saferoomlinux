# Import section
from flask import Blueprint, jsonify,abort,request,render_template
from libs.EvernoteManager import list_notebooks
import config
from libs.functions import str_to_bool

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