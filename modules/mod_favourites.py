# Import section
from flask import Blueprint, jsonify,abort,request,render_template
import libs.FavouritesManager
import config


# Initializing the blueprint
mod_favourites = Blueprint("mod_favourites",__name__)

# Initializing routes
@mod_favourites.route("/list")
def list_favourites():
	return "List of favourites"

@mod_favourites.route("/add",methods=['POST'])
def add_favourite():

    # Validating request
    if not request.form['guid']:
        abort(400)
    if not request.form['title']:
        abort(400)
    if not request.form['service']:
        abort(400)

    # Generating item
    item = {"guid":request.form['guid'],"title":request.form['title'],"service":request.form['service'],"updated":request.form['updated'],"created":request.form['created']}
    
    # Saving to favourites
    FavouritesManager.add_to_favourites(item)

    # Sending response
    return jsonify(status=200,msg="")

@mod_favourites.route("/remove",methods=['POST'])
def remove_favourites():

    # Validating request
    if not request.form['guid']:
        abort(400)

    # Removing from favourites
    FavouritesManager.remove_from_favourites(request.form['guid'])

    return jsonify(status=200,msg="")

@mod_favourites.route("/quick/list",methods=['GET'])
def list_quick_links():

    responseType = ""
    if request.args.get('format'):
        responseType = request.args.get('format')


    # Getting links
    links = FavouritesManager.list_quick_links()

    if (responseType == config.TYPE_TABLE):
        return ""
    elif responseType == config.TYPE_JSON:
        return jsonify(links)

    elif responseType == config.TYPE_SELECT:
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
        FavouritesManager.add_quick_link(request.form['name'],request.form['link'])
        return jsonify(status=200,msg=config.MSG_LINKCREATE_OK)

    except:
        raise
