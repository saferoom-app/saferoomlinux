from flask import Blueprint, jsonify,abort,request,render_template
import getpass
import config
from libs.functions import encryptString, decryptString 



# Initializing the blueprint
mod_settings = Blueprint("mod_settings",__name__)


# Routes
@mod_settings.route("/",methods=['GET'])
def show_page():
    return render_template("settings.html",title="Settings")