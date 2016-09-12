# Import section
from flask import Blueprint, jsonify,abort,request,render_template
import safeglobals
import requests
import httplib
import json
import time
import os
import datetime
from libs.OnenoteManager import save_tokens
from libs.functions import log_message
from libs.ConfigManager import get_client_id, get_client_secret,get_scopes,get_redirect_uri,get_services

# Initializing the blueprint
mod_onenote = Blueprint("mod_onenote",__name__)

@mod_onenote.route("/login",methods=["GET"])
def login():
	# Creating HTTP GET to Login Live URL
    try:
        
        # Getting Client ID, Client Secret and Scopes
        client_id = get_client_id()
        client_secret = get_client_secret()
        scopes = get_scopes()
        redirect_uri = get_redirect_uri()

        if client_id == "" or client_secret == "" or scopes == "" or redirect_uri == "":
            return render_template("dialog.onenote.result.html",success=False,message=safeglobals.MSG_ONDATA_MISSING,title="Onenote result")
        
        # Sending HTTP GET request to Onenote service
        conn = httplib.HTTPSConnection(safeglobals.on_hostname)
        conn.request("GET",safeglobals.on_path % (client_id,scopes,safeglobals.on_response_type,redirect_uri))
        response = conn.getresponse()
                
        # Processing the response
        if response.status != safeglobals.http_ok:
            return render_template("dialog.onenote.result.html",success=False,message=safeglobals.MSG_RESPONSE_ERROR % (str(response.status),response.read()),title="Onenote result")
        return response.read()

    except Exception as e:
        log_message(str(e))
        return render_template("dialog.onenote.result.html",success=False,message=safeglobals.MSG_INTERNAL_ERROR,title="Onenote result")


@mod_onenote.route("/callback",methods=["GET"])
def callback():
    try:
        if not request.args.get("code"):
            return render_template("dialog.onenote.result.html",success=False,message=safeglobals.MSG_MANDATORY_MISSING,title="Onenote result")
        # Getting the authorization code
        code = request.args.get("code")

        # Getting Client ID, Client Secret and Scopes
        client_id = get_client_id()
        client_secret = get_client_secret()
        redirect_uri = get_redirect_uri()

        # Checking mandatory data
        if client_id == "" or client_secret == "" or redirect_uri == "":
            return render_template("dialog.onenote.result.html",success=False,message=safeglobals.MSG_ONDATA_MISSING,title="Onenote result")

        # Sending HTTP POST request for Access Token and Refresh Tokens
        r = requests.post(safeglobals.on_token_url, data={'grant_type': 'authorization_code', 'client_id': client_id, 'client_secret': client_secret,'code':code,'redirect_uri':redirect_uri})

        # Checking the response (it should be in JSON format)
        response = json.loads(r.text)
        
        # Calculating the expiration date
        current = int(time.time())
        expires_in = int(response['expires_in'])+current
        tokens = {"access":response['access_token'],"refresh":response['refresh_token'],"expires":str(expires_in)}
        
        # Writing tokens to file
        with open(safeglobals.path_tokens,"w") as f:
            f.write(json.dumps(tokens))
        return render_template("dialog.onenote.result.html",success=True,message=safeglobals.MSG_ONLOGIN_OK,title="Onenote result")
    except Exception as e:
        log_message(str(e))
        return render_template("dialog.onenote.result.html",success=False,message=safeglobals.MSG_INTERNAL_ERROR,title="Onenote result")

@mod_onenote.route("/user",methods=["GET"])
def user():

    # Getting service status
    service = get_services()
    
    # If service is disabled, send the special template
    if service['onenote'] == False:
        return render_template("service.disabled.html",service="Onenote")

    tokens = {"access":False,"refresh":False,"expired":False,"expires_in":"n/a"}
    try:
        # Checking that file with tokens exists
        if os.path.exists(safeglobals.path_tokens) == False:
            return render_template("user.onenote.html",tokens=tokens)
        with open(safeglobals.path_tokens,"r") as f:
            data = json.loads(f.read())
        
        if data['access']:
            tokens['access'] = True
        if data['refresh']:
            tokens['refresh'] = True
        if data['expires']:
            
            current = int(time.time())
            expires_in = int(data['expires'])
            if (current >= expires_in):
            	tokens['expired'] = True
            	tokens['expires_in'] = "[ Expired ]"
            else:
            	tokens['expired'] = False
            	tokens['expires_in'] = datetime.datetime.fromtimestamp(expires_in).strftime('%Y-%m-%d %H:%M:%S')

        return render_template("user.onenote.html",tokens=tokens)
    except Exception as e:
    	log_message(str(e))
        return render_template("user.onenote.html",tokens=tokens)


@mod_onenote.route("/token/refresh")
def refresh():
    try:
        
        # Checking if we have the developer token
        if os.path.exists(safeglobals.path_tokens) == False:
            return render_template("dialog.onenote.result.html",success=False,message=safeglobals.MSG_NO_TOKENS,title="Onenote result")

        # Checking if refresh token is configured
        with open(safeglobals.path_tokens,"r") as f:
        	data = json.loads(f.read())
        
        if not data['refresh']:
        	return render_template("dialog.onenote.result.html",success=False,message=safeglobals.MSG_NO_TOKENS,title="Onenote result")

        # Getting Client ID, Client Secret and Scopes
        client_id = get_client_id()
        client_secret = get_client_secret()
        redirect_uri = get_redirect_uri()

        # Checking mandatory data
        if client_id == "" or client_secret == "" or redirect_uri == "":
            return render_template("dialog.onenote.result.html",success=False,message=safeglobals.MSG_ONDATA_MISSING,title="Onenote result")

        # If "Refresh Token" exists, then we need to update the access token
        r = requests.post(safeglobals.on_token_url, data={'grant_type': 'refresh_token', 'client_id': client_id, 'client_secret': client_secret,'redirect_uri':redirect_uri,'refresh_token':data['refresh']})

        # Saving tokens
        save_tokens(json.loads(r.text))
        
        return render_template("dialog.onenote.result.html",success=True,message=safeglobals.MSG_TOKENREFRESH_OK,title="Onenote result")

    except Exception as e:
    	log_message(str(e))
    	return render_template("dialog.onenote.result.html",success=False,message=safeglobals.MSG_INTERNAL_ERROR,title="Onenote result")