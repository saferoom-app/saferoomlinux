# Import section
from flask import Flask,render_template,jsonify,request,abort
from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import NoteSortOrder
import json
import datetime
import hashlib
import os


# Custom imports
import config
from libs.functions import fileMD5
from bs4 import BeautifulSoup, Tag

# Blueprint imports
from modules.mod_favourites import mod_favourites
from modules.mod_note import mod_note
from modules.mod_notebook import mod_notebook
from modules.mod_search import mod_search
from modules.mod_tag import mod_tag
from modules.mod_settings import mod_settings


# App initialization
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Registering blueprints
app.register_blueprint(mod_favourites,url_prefix="/favourites")
app.register_blueprint(mod_note,url_prefix="/note")
app.register_blueprint(mod_notebook,url_prefix="/notebooks")
app.register_blueprint(mod_tag,url_prefix="/tags")
app.register_blueprint(mod_search,url_prefix="/searches")
app.register_blueprint(mod_settings,url_prefix="/settings");

'''
=============================================
   Routes
=============================================

'''

@app.route("/")
def index():
	return render_template('index.html',pageTitle="Application :: Main")

# This route will be used to display a page that will be used to create encrypted notes
@app.route("/create")
def create():
	return render_template("create.html",pageTitle="Application :: Create note")

# This route will be used to display a page that will be used to view a list of notes, tags and Saved Searches
@app.route("/list")
def list():
	return render_template("list.html",pageTitle="Application :: View")

@app.route("/user")
def user():

	# Checking Access Token
    if (config.ACCESS_TOKEN == ""):
        abort(501)
        exit()

    client = EvernoteClient(token=config.ACCESS_TOKEN,sandbox=False)
    userStore = client.get_user_store()
    response = userStore.getUser()

    # Setting user data
    username = response.username
    uid = response.id
    email = response.email
    privilegeLevel = app.config['PRIVILEGE_LEVEL'][str(response.privilege)]
    premiumStatus = app.config['PREMIUM_STATUS'][str(response.accounting.premiumServiceStatus)]
    privilege = response.privilege

    #return json.dumps(response)
    return render_template('user.html',username=username,uid=uid,email=email,premiumStatus=premiumStatus,priv=privilegeLevel)




'''
============================================
    File uploads
============================================
'''

@app.route("/upload",methods=["POST"])
def upload():

    # Getting a list of files
    hashes = []
    uploaded_files = request.files.getlist("attach[]")
    for file in uploaded_files:
        file.save("static/tmp/"+file.filename)


    for file in uploaded_files:
        hashes.append(fileMD5("static/tmp/"+file.filename))

    return jsonify(hashes)



'''
============================================
    Route for testing
============================================
'''

@app.route("/demo",methods=['GET'])
def demo():
    #return "<embed src=\"static/tmp/sample.doc\" width=\"100%\" height=\"500\">"
    soup = BeautifulSoup("<div class=\"attachment\"></div>")
    root_div = soup.div
    
    # Creating ICON span tag
    icon_span_tag = soup.new_tag("span",style="margin-left:10px")
    icon_img_tag = soup.new_tag("img",src="static/images/icon_pdf.png")
    icon_span_tag.append(icon_img_tag)
    
    # Creating text tag
    text_span_tag = soup.new_tag("span",style="margin-left:10px")
    text_a_tag = soup.new_tag("a",href="/static/tmp/apache.pdf")
    text_a_tag.string = "apache.pdf"
    text_span_tag.append(text_a_tag)

    # Creating DIV with two spans
    div_col_10 = soup.new_tag("div",style="display:inline-block",**{"class":"col-md-10"})
    div_col_10.append(icon_span_tag)
    div_col_10.append(text_span_tag)

    # Creating div(col-md-2)
    div_col_2 = soup.new_tag("div",**{"class":"col-md-2"})
    root_div.append(div_col_10)
    root_div.append(div_col_2)


    # Combining all together
    return soup.prettify()


'''
============================================
	Handling errors
============================================
'''

@app.errorhandler(500)
def internal_server_error(e):
	app.logger.error(e)
	return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'),404

@app.errorhandler(501)
def bad_request(e):
	return render_template('501.html'),501

@app.errorhandler(400)
def custom_400(error):
    print error
    return error;


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


if __name__ == "__main__":
    app.debug = True
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(config.ERROR_LOG_FILE, maxBytes=1024 * 1024 * 100, backupCount=20)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    app.run()
