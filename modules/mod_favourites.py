# Import section
from flask import Blueprint, jsonify,abort,request,render_template
from libs.FavouritesManager import add_to_favourites,remove_from_favourites,add_quick_link,list_quick_links,list_favourites
import safeglobals
import json


# Initializing the blueprint
mod_favourites = Blueprint("mod_favourites",__name__)

# Initializing routes
@mod_favourites.route("/list",methods=['GET'])
def list():

    responseType = safeglobals.TYPE_LIST
    if request.args.get('format'):
        responseType = request.args.get('format')

    # Getting list of favourites
    favourites = list_favourites()

    # Sending response
    if (responseType == safeglobals.TYPE_JSON):
        return jsonify(favourites)
    else:
        return render_template("list.favourites.html",favourites=favourites)	

@mod_favourites.route("/add",methods=['POST'])
def add_favourite():

    # Validating request
    favourites = request.get_json()
    if favourites is None:
        abort(400)

    # Saving to favourites
    add_to_favourites(favourites)

    # Sending response
    return jsonify(status=200,msg="")

@mod_favourites.route("/remove",methods=['POST'])
def remove_favourites():

    # Validating request
    favourites = request.get_json()
    if favourites is None:
        abort(400)

    # Removing from favourites
    remove_from_favourites(favourites)

    # Getting a new list of favourites
    favourites = list_favourites()

    # Sending response
    return jsonify(status=200,msg="")
    

@mod_favourites.route("/quick/list",methods=['GET'])
def list_qlinks():

    responseType = ""
    if request.args.get('format'):
        responseType = request.args.get('format')

    # Getting links
    links = list_quick_links()

    if (responseType == safeglobals.TYPE_LIST):
        return render_template("list.links.html",links=links);
    elif responseType == safeglobals.TYPE_JSON:
        return jsonify(links)
    elif responseType == safeglobals.TYPE_SELECT:
        return render_template("select.links.html",links=links)

@mod_favourites.route("/quick/add",methods=['GET'])
def add_to_quick():
    return render_template("content.quickadd.html")


@mod_favourites.route("/quick/create",methods=['POST'])
def create_quick_link():

    if not request.form['name']:
        abort(400)
    if not request.form['link']:
        abort(400)

    try:
        # Creating a link
        add_quick_link(request.form['name'],request.form['link'])
        return jsonify(status=200,msg=safeglobals.MSG_LINKCREATE_OK)
    except:
        raise

@mod_favourites.route("/",methods=['GET'])
def index():
    return render_template("favourites.html",title="Favourites")