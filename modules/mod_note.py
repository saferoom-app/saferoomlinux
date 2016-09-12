# Import section
from flask import Blueprint, jsonify,abort,request,render_template
import safeglobals
import os
import json
from libs.functions import encryptNote,stringMD5,decryptNote,decryptFileData,getMime,getIcon,millisToDate,fileMD5,str_to_bool,handle_exception,send_response,parse_content
import xml.etree.ElementTree as ET
import re
from bs4 import BeautifulSoup, Tag
from libs.EvernoteManager import list_notes,create_note,get_note
from libs.OnenoteManager import list_on_notes,get_access_token, get_on_note,download_resources,create_on_note
from libs.PasswordManager import set_password
import requests
import re
from libs.ConfigManager import get_developer_token

# Initializing the blueprint
mod_note = Blueprint("mod_note",__name__)

# Initializing routes
@mod_note.route("/list",methods=['POST','GET'])
def notes():

    try:
        # Defining response type
        if request.form['format']:
            responseType = request.form['format']
        else:
            responseType = "json"

        # Getting developer token
        access_token = get_developer_token()
        if access_token == "":
            return handle_exception(responseType,safeglobals.http_bad_request,safeglobals.MSG_NO_DEVTOKEN)               

        # Getting a list of notes
        notes = list_notes(access_token,request.form['refresh'],request.form["type"],request.form['guid'])

        # Sending response based on specified response type
        return send_response(notes,responseType,{safeglobals.TYPE_HTML:"list.notes.html"})
        
    except Exception as e:
        return handle_exception(responseType,safeglobals.http_internal_server,str(e))


@mod_note.route("/create",methods=['POST'])
def createnote():

    try:
        # Checking provided data
        if not request.form['title'] or request.form['title'] == "":
            return handle_exception(safeglobals.TYPE_JSON,safeglobals.http_bad_request,safeglobals.MSG_MANDATORY_MISSING)
        title = request.form['title']
        if not request.form['content'] or request.form['content'] == "":
            return handle_exception(safeglobals.TYPE_JSON,safeglobals.http_bad_request,safeglobals.MSG_MANDATORY_MISSING)
        if not request.form['notebook_guid'] or request.form['notebook_guid'] == "":
            return handle_exception(safeglobals.TYPE_JSON,safeglobals.http_bad_request,safeglobals.MSG_MANDATORY_MISSING)

        if request.form['service'] == safeglobals.service_onenote and request.form['section_guid'] == "":
            return handle_exception(safeglobals.TYPE_JSON,safeglobals.http_bad_request,safeglobals.MSG_MANDATORY_MISSING)
        
        notebook_guid = request.form['notebook_guid']
        section_guid = request.form['section_guid']
        content = request.form['content']
        if "en-media" in content and not request.form['filelist']:
            return handle_exception(safeglobals.TYPE_JSON,safeglobals.http_bad_request,safeglobals.MSG_MANDATORY_MISSING)
        fileList = json.loads(request.form['filelist'])

        # Checking if mode is set to "OTP" and OTP password has been provided
        if not request.form['mode']:
            return handle_exception(safeglobals.TYPE_HTML,safeglobals.http_bad_request,safeglobals.MSG_MANDATORY_MISSING)
        if request.form['mode'] == "otp" and not request.form['pass']:
            return handle_exception(safeglobals.TYPE_HTML,safeglobals.http_bad_request,safeglobals.MSG_MANDATORY_MISSING)
        tags = []
        if request.form['tags']:
            tags = request.form['tags'].split(",")

        # Filtering data
        content = content.replace("<p id=\"saferoomAttach\"><br></p>","").replace("<br>","").replace("id=\"saferoomAttach\"","")       
        content = parse_content(request.form['service'],content)

        # Set password
        password = set_password(request.form['mode'],request.form['pass'])

        # Creating a note
        if request.form['service'] == safeglobals.service_evernote:
            access_token = get_developer_token()
            if access_token == "":
                return handle_exception(safeglobals.TYPE_JSON,safeglobals.http_bad_request,safeglobals.MSG_NO_DEVTOKEN)
            create_note(access_token,title,content,notebook_guid,fileList,tags,password)

        elif request.form['service'] == safeglobals.service_onenote:
            access_token = get_access_token()
            if access_token == "":
                return handle_exception(safeglobals.TYPE_JSON,safeglobals.http_bad_request,safeglobals.MSG_NO_TOKENS)
            create_on_note(access_token,title,content,{"guid":notebook_guid,"section":section_guid},fileList,password)    

        return jsonify(status=safeglobals.http_ok,message=safeglobals.MSG_NOTECREATE_OK)

    except Exception as e:
        return handle_exception(safeglobals.TYPE_JSON,safeglobals.http_internal_server,str(e))
    
@mod_note.route("/decrypt",methods=['POST'])
def decrypt_note():

    try:
        # Checking the GUID
        if not request.form['guid']:
            return handle_exception(safeglobals.TYPE_HTML,safeglobals.http_bad_request,safeglobals.MSG_MANDATORY_MISSING)
        guid = request.form['guid']

        # Checking if mode is set to "OTP" and OTP password has been provided
        if not request.form['mode']:
            return handle_exception(safeglobals.TYPE_HTML,safeglobals.http_bad_request,safeglobals.MSG_MANDATORY_MISSING)
        if request.form['mode'] == "otp" and not request.form['pass']:
            return handle_exception(safeglobals.TYPE_HTML,safeglobals.http_bad_request,safeglobals.MSG_MANDATORY_MISSING)


        # Checking that encrypted note is saved on local machine
        if os.path.exists(safeglobals.path_note % (guid,"")) == False:
            return handle_exception(safeglobals.TYPE_HTML,safeglobals.http_not_found,safeglobals.MSG_NOTE_MISSING % safeglobals.path_note % (guid,"") )

        # Checking that "content.json" is there
        if os.path.isfile(safeglobals.path_note % (guid,"content.json")) == False:
            return handle_exception(safeglobals.TYPE_HTML,safeglobals.http_not_found,safeglobals.MSG_NOTE_MISSING % safeglobals.path_note % (guid,"content.json") )

        # Reading the "content.json"
        with open(safeglobals.path_note % (guid,"content.json"),"r") as f:
            note = json.loads(f.read())

        # Setting decryption password
        password = set_password(request.form['mode'],request.form['pass'])

        # Getting a list of resources
        resources = []
        hash = ""
        data = None
        path = safeglobals.path_note % (guid,"")
        tmp_path = safeglobals.path_tmp
        for filename in os.listdir(path):
            if "content.json" not in filename:
            
                # Reading file data into variale
                with open(path+filename,"rb") as f:
                    data = f.read()

                # Decrypting data
                data = decryptFileData(data,password)

                # Writing data to temporary file
                filename = filename.replace("%20","")
                with open(tmp_path+filename,"wb") as f:
                    f.write(data)

                # Calculating hash of written file
                if (os.path.exists(tmp_path+filename)):
                    hash = fileMD5(tmp_path+filename)

                # Getting file MIME
                mime = getMime(filename)

                # Adding to collection
                resources.append({"name":filename,"hash":hash,"mime":mime}) 

        # Getting note content (within <en-note> tag)
        noteContent = note.get('content')
        noteContent = noteContent[noteContent.find(safeglobals.ENCRYPTED_PREFIX)+len(safeglobals.ENCRYPTED_PREFIX):noteContent.find(safeglobals.ENCRYPTED_SUFFIX)].strip();
        noteContent = decryptNote(safeglobals.ENCRYPTED_PREFIX + noteContent + safeglobals.ENCRYPTED_SUFFIX,password)
        noteContent.replace("></en-media>","/>")
        
        # Finding all <en-media> tags within the note content       
        soup = BeautifulSoup(noteContent,"html.parser")
        tag = None
        matches =  soup.find_all('en-media')
        for match in matches:
            for resource in resources:
                if resource['hash'] == match['hash'] or resource['hash'].upper() == match['hash'].upper():

                    if "image" in match['type']:
                        tag = soup.new_tag('img',style="width:100%",src="/static/tmp/"+resource['name'])

                    elif safeglobals.MIME_PDF in match['type']:
                        
                        tag = soup.new_tag("embed",width="100%", height="500",src="/static/tmp/"+resource['name']+"#page=1&zoom=50")

                    elif "application" in match['type']:
                        
                        # Creating root div
                        tag = soup.new_tag("div",**{"class":"attachment"})

                        # Creating ICON span tag
                        icon_span_tag = soup.new_tag("span",style="margin-left:10px")
                        icon_img_tag = soup.new_tag("img",src="/static/images/"+getIcon(resource['mime']))
                        icon_span_tag.append(icon_img_tag)

                        # Creating text tag
                        text_span_tag = soup.new_tag("span",style="margin-left:10px")
                        text_a_tag = soup.new_tag("a",href="/static/tmp/"+resource['name'])
                        text_a_tag.string = resource['name']
                        text_span_tag.append(text_a_tag)

                        # Creating DIV with two spans
                        div_col_10 = soup.new_tag("div",style="display:inline-block",**{"class":"col-md-10"})
                        div_col_10.append(icon_span_tag)
                        div_col_10.append(text_span_tag)

                        # Creating div(col-md-2)
                        div_col_2 = soup.new_tag("div",**{"class":"col-md-2"})

                        # Creating div row
                        div_row = soup.new_tag("div",**{"class":"row"})
                        div_row.append(div_col_10)
                        div_row.append(div_col_2)

                        # Combining all together
                        tag.append(div_row)
                        
                    match.replaceWith(tag)
        
        noteContent = soup.prettify()
        noteContent = noteContent.replace("></embed>","/>")
        return noteContent

    except Exception as e:
    	return handle_exception(safeglobals.TYPE_HTML,safeglobals.http_internal_server,str(e))



@mod_note.route("/on/decrypt",methods=['POST'])
def decrypt_onenote_note():
    try:
        # Checking the GUID
        if not request.form['guid']:
            return handle_exception(safeglobals.TYPE_HTML,safeglobals.http_bad_request,safeglobals.MSG_MANDATORY_MISSING)
        guid = request.form['guid']

        # Checking if mode is set to "OTP" and OTP password has been provided
        if not request.form['mode']:
            return handle_exception(safeglobals.TYPE_HTML,safeglobals.http_bad_request,safeglobals.MSG_MANDATORY_MISSING)
        if request.form['mode'] == "otp" and not request.form['pass']:
            return handle_exception(safeglobals.TYPE_HTML,safeglobals.http_bad_request,safeglobals.MSG_MANDATORY_MISSING)

        # Checking that encrypted note is saved on local machine
        if os.path.exists(safeglobals.path_note % (guid,"")) == False:
            return handle_exception(safeglobals.TYPE_HTML,safeglobals.http_not_found,safeglobals.MSG_NOTE_MISSING % safeglobals.path_note % (guid,"") )

        # Checking that "content.json" is there
        if os.path.isfile(safeglobals.path_note % (guid,"content.json")) == False:
            return handle_exception(safeglobals.TYPE_HTML,safeglobals.http_not_found,safeglobals.MSG_NOTE_MISSING % safeglobals.path_note % (guid,"content.json") )

        # Setting decryption password
        password = set_password(request.form['mode'],request.form['pass'])

        # Getting the note content
        content = ""
        with open(safeglobals.path_note % (guid,"content.json"),"r") as f:
            content = f.read()

        # Decrypting note content
        content = content[content.find(safeglobals.ENCRYPTED_PREFIX)+len(safeglobals.ENCRYPTED_PREFIX):content.find(safeglobals.ENCRYPTED_SUFFIX)].strip();
        content = decryptNote(safeglobals.ENCRYPTED_PREFIX + content + safeglobals.ENCRYPTED_SUFFIX,password)

        # Decrypting downloaded resources and put them into TMP dir
        path = safeglobals.path_note % (guid,"")
        tmp_path = safeglobals.path_tmp
        for filename in os.listdir(path):
            if "content.json" not in filename:
            
                # Reading file data into variale
                with open(path+filename,"rb") as f:
                    data = f.read()

                # Decrypting data
                print password
                data = decryptFileData(data,password)

                # Writing data to temporary file
                filename = filename.replace("%20","")
                with open(tmp_path+filename,"wb") as f:
                    f.write(data)                  

        
        # Parsing the content and make it readable. First find <object> tags
        document = BeautifulSoup(content,"html.parser")
        matches = document.find_all(["object","img"])
        for match in matches:
            if "img" in match:
                print "Image"
            
            else:

                # If we have PDF we display the <embed>
                if safeglobals.MIME_PDF in match['type']:
                    tag = document.new_tag("embed",width="100%", height="500",src="/static/tmp/"+match['data-attachment']+"#page=1&zoom=50")

                else:
                    # Creating root div
                    tag = document.new_tag("div",**{"class":"attachment"})

                    # Creating ICON span tag
                    icon_span_tag = document.new_tag("span",style="margin-left:10px")
                    icon_img_tag = document.new_tag("img",src="/static/images/"+getIcon(match['type']))
                    icon_span_tag.append(icon_img_tag)

                    # Creating text tag
                    text_span_tag = document.new_tag("span",style="margin-left:10px")
                    text_a_tag = document.new_tag("a",href="/static/tmp/"+match['data-attachment'])
                    text_a_tag.string = match['data-attachment']
                    text_span_tag.append(text_a_tag)

                    # Creating DIV with two spans
                    div_col_10 = document.new_tag("div",style="display:inline-block",**{"class":"col-md-10"})
                    div_col_10.append(icon_span_tag)
                    div_col_10.append(text_span_tag)

                    # Creating div(col-md-2)
                    div_col_2 = document.new_tag("div",**{"class":"col-md-2"})

                    # Creating div row
                    div_row = document.new_tag("div",**{"class":"row"})
                    div_row.append(div_col_10)
                    div_row.append(div_col_2)

                    # Combining all together
                    tag.append(div_row)

                # Replace the match with the tag
                match.replaceWith(tag)

        print document.prettify()
        return document.prettify()
    except Exception as e:
        return handle_exception(safeglobals.TYPE_HTML,safeglobals.http_internal_server,str(e))


@mod_note.route("/<string:GUID>",methods=['POST','GET'])
def note(GUID):
    try:
        responseType = "html"
        if not GUID or GUID == "":
            return handle_exception(responseType,safeglobals.http_bad_request,safeglobals.MSG_MANDATORY_MISSING)
            
        if request.method == "GET":
            return render_template("view.html",title="Application :: View note",guid=GUID)
        else:
            # Getting note
            responseType = "json"

            # Checking developer token
            access_token = get_developer_token()
            if access_token == "":
                return handle_exception(responseType,safeglobals.http_bad_request,safeglobals.MSG_NO_DEVTOKEN)

            # Getting note    
            note = get_note(access_token,GUID,False)
            return jsonify(status=safeglobals.http_ok,message=note)
    except Exception as e:
        return handle_exception(responseType,safeglobals.http_internal_server,str(e))


@mod_note.route("/save",methods=["GET"])
def save_note_as():
    return request.args.get("format")


@mod_note.route("/on/list/<string:guid>/<string:responseType>")
def list_onenote_notes(guid,responseType):
    forceRefresh = False
    if request.args.get("refresh"):
        forceRefresh = str_to_bool(request.args.get("refresh"))

    # Getting a list of sections
    access_token = get_access_token()
    notes = list_on_notes(access_token,forceRefresh,guid)

    # Returning response based on specified format
    return send_response(notes,responseType,{"default":"onenote.list.notes.html"})    

@mod_note.route("/on/<string:guid>",methods=["GET","POST"])
def get_onenote_note(guid):
    try:
        if request.method == "GET":
            return render_template("onenote.view.html",title="Application :: View note",guid=guid)

        else:
            content = ""
            # Checking the request
            forceRefresh = False
            if not guid or guid == "":
                return handle_exception(lib.globals.TYPE_JSON,safeglobals.http_bad_request,safeglobals.MSG_MANDATORY_MISSING)
            if request.args.get("refresh"):
                forceRefresh = str_to_bool(request.args.get("refresh"))
            
            # Getting access token
            access_token = get_access_token()
            if (access_token == ""):
                log_message(safeglobals.MSG_NO_TOKENS)
                return handle_exception(responseType,safeglobals.http_bad_request,safeglobals.MSG_NO_TOKENS)               

            # Downloading note
            note = get_on_note(access_token,guid,forceRefresh)

            # Downloading resources and processing the note content for proper display
            note = download_resources(access_token,note,guid)
            return jsonify(status=safeglobals.http_ok,message=note);

    except Exception as e:
        return handle_exception(responseType,safeglobals.http_internal_server,str(e))
    return guid