# Import section
from flask import Flask,render_template,jsonify,request,abort
from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import NoteSortOrder
import json
import datetime
import hashlib
import os
import ssl

# Custom imports
import libs.globals
from libs.functions import fileMD5
from bs4 import BeautifulSoup, Tag
from libs.functions import decryptString,generateKey,send_response
from libs.OnenoteManager import is_access_token_valid
from libs.PasswordManager import get_master_password
from libs.ConfigManager import get_developer_token,get_client_id,get_client_secret

# Blueprint imports
from modules.mod_favourites import mod_favourites
from modules.mod_note import mod_note
from modules.mod_notebook import mod_notebook
from modules.mod_search import mod_search
from modules.mod_tag import mod_tag
from modules.mod_settings import mod_settings
from modules.mod_onenote import mod_onenote


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
app.register_blueprint(mod_onenote,url_prefix="/onenote");

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

@app.route("/on/list")
def on_list():
    return render_template("onenote.list.html",pageTitle="Application :: View")

@app.route("/user")
def user():

	# Checking Access Token
    access_token = get_developer_token()
    if (access_token == ""):
        abort(501)
        exit()

    client = EvernoteClient(token=access_token,sandbox=False)
    userStore = client.get_user_store()
    response = userStore.getUser()

    # Setting user data
    username = response.username
    uid = response.id
    email = response.email
    privilegeLevel = libs.globals.PRIVILEGE_LEVEL[str(response.privilege)]
    premiumStatus = libs.globals.PREMIUM_STATUS[str(response.accounting.premiumServiceStatus)]
    privilege = response.privilege

    #return json.dumps(response)
    return render_template('user.evernote.html',username=username,uid=uid,email=email,premiumStatus=premiumStatus,priv=privilegeLevel)




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
        file.save(libs.globals.path_tmp+file.filename)

    for file in uploaded_files:
        hashes.append(fileMD5(libs.globals.path_tmp+file.filename))
    return jsonify(hashes)

'''
============================================
    Route for testing
============================================
'''

@app.route("/demo",methods=['GET'])
def demo():
    send_response([{"name":"test"},{"name":"test2"}],"json",{"json":"json.html","select":"select.html","html":"html.html"})
    return "demo page"

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
    file_handler = RotatingFileHandler(libs.globals.ERROR_LOG_FILE, maxBytes=1024 * 1024 * 100, backupCount=20)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    # SSL server
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain('server.crt', 'server.key')
    app.run(ssl_context=context)
    #app.run()
