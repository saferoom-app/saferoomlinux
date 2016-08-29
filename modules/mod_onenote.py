# Import section
from flask import Blueprint, jsonify,abort,request,render_template
import config
import requests
import httplib
import json
import time
import os
import datetime
from libs.OnenoteManager import save_tokens

# Initializing the blueprint
mod_onenote = Blueprint("mod_onenote",__name__)

@mod_onenote.route("/login",methods=["GET"])
def login():

	# Creating HTTP GET to Login Live URL
	try:
	    conn = httplib.HTTPSConnection(config.on_hostname)
	    conn.request("GET",config.on_path % (config.on_client_id,config.on_scopes,config.on_response_type,config.on_redirect_uri))
	    response = conn.getresponse()
	    return response.read()
	except Exception as e:
		return config.MSG_INTERNAL_ERROR


@mod_onenote.route("/callback",methods=["GET"])
def callback():
	try:
		if not request.args.get("code"):
			abort(400)

		# Getting the authorization code
		code = request.args.get("code")
		r = requests.post(config.on_token_url, data={'grant_type': 'authorization_code', 'client_id': config.on_client_id, 'client_secret': config.on_client_secret,'code':code,'redirect_uri':config.on_redirect_uri})

		# Checking the response (it should be in JSON format)
		response = json.loads(r.text)
		
		# Calculating the expiration date
		current = int(time.time())
		expires_in = int(response['expires_in'])+current
		tokens = {"access":response['access_token'],"refresh":response['refresh_token'],"expires":str(expires_in)}

		# Writing tokens to file
		with open(config.path_tokens,"w") as f:
			f.write(json.dumps(tokens))

		return render_template("dialog.onenote.result.html",success=True,message=config.MSG_ONLOGIN_OK,title="Onenote result")

	except Exception as e:
		return render_template("dialog.onenote.result.html",success=False,message=config.MSG_INTERNAL_ERROR,title="Onenote result")

@mod_onenote.route("/user",methods=["GET"])
def user():
    tokens = {"access":False,"refresh":False,"expired":False,"expires_in":"n/a"}
    try:
        # Checking that file with tokens exists
        if os.path.exists(config.path_tokens) == False:
            return render_template("user.onenote.html",tokens=tokens)
        with open(config.path_tokens,"r") as f:
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
    	print e
        return render_template("user.onenote.html",tokens=tokens)


@mod_onenote.route("/token/refresh")
def refresh():
    try:
        
        # Checking if we have the developer token
        if os.path.exists(config.path_tokens) == False:
            return render_template("dialog.onenote.result.html",success=False,message=config.MSG_NO_TOKENS,title="Onenote result")

        # Checking if refresh token is configured
        with open(config.path_tokens,"r") as f:
        	data = json.loads(f.read())
        
        if not data['refresh']:
        	return render_template("dialog.onenote.result.html",success=False,message=config.MSG_NO_TOKENS,title="Onenote result")

        # If "Refresh Token" exists, then we need to update the access token
        r = requests.post(config.on_token_url, data={'grant_type': 'refresh_token', 'client_id': config.on_client_id, 'client_secret': config.on_client_secret,'redirect_uri':config.on_redirect_uri,'refresh_token':data['refresh']})

        # Saving tokens
        save_tokens(json.loads(r.text))
        
        return render_template("dialog.onenote.result.html",success=True,message=config.MSG_TOKENREFRESH_OK,title="Onenote result")

    except Exception as e:
    	print e
    	return render_template("dialog.onenote.result.html",success=False,message=config.MSG_INTERNAL_ERROR,title="Onenote result")




