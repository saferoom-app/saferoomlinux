# Import section
from flask import Blueprint, jsonify,abort,request,render_template,session
import json, safeglobals


# Initializing the blueprint
mod_modal = Blueprint("mod_modal",__name__)

# Routes
@mod_modal.route("/encrypt/progress",methods=["GET"])
def display_encrypt_progress():
	return render_template("dialog.progress.html",title="Encrypting notes")