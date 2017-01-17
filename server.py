# Import section
from flask import Flask,render_template,jsonify,request,abort,send_from_directory
from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import NoteSortOrder
import json,datetime,hashlib,os,ssl,safeglobals

# Custom imports
from libs.functions import fileMD5,parse_content
from bs4 import BeautifulSoup, Tag
from libs.functions import decryptString,generateKey,send_response
from libs.OnenoteManager import is_access_token_valid
from libs.PasswordManager import get_master_password
from libs.ConfigManager import get_developer_token,get_client_id,get_client_secret,get_services

# Blueprint imports
from modules.mod_favourites import mod_favourites
from modules.mod_note import mod_note
from modules.mod_notebook import mod_notebook
from modules.mod_search import mod_search
from modules.mod_tag import mod_tag
from modules.mod_settings import mod_settings
from modules.mod_onenote import mod_onenote
from modules.mod_backups import mod_backups
from modules.mod_modal import mod_modal


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
app.register_blueprint(mod_backups,url_prefix="/backups")
app.register_blueprint(mod_modal,url_prefix="/modal")

'''
=============================================
   Routes
=============================================

'''

@app.route("/")
def index():
    
    # Getting a list of activated services
    services = get_services()
    return render_template('index.html',pageTitle="Application :: Main",services=services)

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

@app.route("/log")
def server_log():
    data = None
    with open(safeglobals.path_logfile,"r") as f:
        data = f.readlines()
    return "\n".join(data)


@app.route("/user",methods=["GET"])
def user():

	# Checking Access Token
    access_token = get_developer_token()
    if (access_token == ""):
        return safeglobals.MSG_NO_DEVTOKEN

    client = EvernoteClient(token=access_token,sandbox=False)
    userStore = client.get_user_store()
    response = userStore.getUser()

    # Setting user data
    username = response.username
    uid = response.id
    email = response.email
    privilegeLevel = safeglobals.PRIVILEGE_LEVEL[str(response.privilege)]
    premiumStatus = safeglobals.PREMIUM_STATUS[str(response.accounting.premiumServiceStatus)]
    privilege = response.privilege

    #return json.dumps(response)
    return render_template('user.evernote.html',username=username,uid=uid,email=email,premiumStatus=premiumStatus,priv=privilegeLevel)


@app.route("/install",methods=["GET"])
def install_app():
    return render_template("wizard.html",title="Saferoom :: Installation wizard")



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
        file.save(safeglobals.path_tmp+file.filename)

    for file in uploaded_files:
        hashes.append(fileMD5(safeglobals.path_tmp+file.filename))
    return jsonify(hashes)

'''
============================================
    Route for testing
============================================
'''

@app.route("/demo/",methods=['GET'])
def demo():
    from libs.Safenote import Safenote
    from libs.EvernoteManager import get_note_store,upload_note,get_raw_note
    from libs.ConfigManager import get_access_token

    # Getting access token
    access_token = get_access_token()
    guid = "5812709e-717f-45ee-a639-3be06bbeea0b";
    page_guid = "0-1281889f6000406cb8a78499a3c29959!1-F54C66CABCD50318!156"
    #note_store = get_note_store(access_token)
    #note = get_raw_note(access_token,guid,note_store)
    #note.__class__ = Safenote
    print Safenote.to_html(page_guid,safeglobals.service_onenote)

    
    return ""
        

'''
============================================
	Handling errors
============================================
'''

@app.errorhandler(400)
def custom_400(error):
    app.logger.error(error)
    return jsonify({'message': error.description['message']}),safeglobals.http_bad_request

@app.errorhandler(403)
def custom_403(error):
    return jsonify({'message': error.description['message']}),safeglobals.http_forbidden

@app.errorhandler(500)
def custom_500(error):
    return jsonify({'message': safeglobals.MSG_INTERNAL_ERROR}),safeglobals.http_internal_server

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
    app.secret_key = "afc67368-0c14-4fa6-8c35-ac150141faa6"
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(safeglobals.path_logfile, maxBytes=1024 * 1024 * 100, backupCount=20)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    # SSL server
    #context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    #context.load_cert_chain('server.crt', 'server.key')
    #app.run(ssl_context=context,threaded=True)
    app.run(threaded=True)
