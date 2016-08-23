# Import section
from flask import Blueprint, jsonify,abort,request,render_template
import config
import os
import json
from libs.functions import encryptNote,stringMD5,decryptNote,decryptFileData,getMime,getIcon,millisToDate,fileMD5
import xml.etree.ElementTree as ET
import re
from bs4 import BeautifulSoup, Tag
from libs.EvernoteManager import list_notes,create_note,get_note

# Initializing the blueprint
mod_note = Blueprint("mod_note",__name__)

# Initializing routes


@mod_note.route("/list",methods=['POST','GET'])
def notes():

    try:
        # Getting a list of notes
        notes = list_notes(config.ACCESS_TOKEN,request.form['refresh'],request.form["type"],request.form['guid'])

        # Sending response based on specified format
        if (request.args.get('format') == "select"):
            return ""        
        elif (request.args.get('format') == "json"):
            return jsonify(notes)
        else:
            return render_template('list.notes.html',notes=notes)
    except:
        raise


@mod_note.route("/create",methods=['POST'])
def create_note():

    try:
        # Checking provided data
        if not request.form['title']:
            abort(400)
        title = request.form['title']
        if not request.form['content']:
            abort(400)
        if not request.form['guid']:
            abort(400)
        guid = request.form['guid']
        content = request.form['content']
        if "en-media" in content and not request.form['filelist']:
            abort(400)
        fileList = json.loads(request.form['filelist'])
        #print fileList
        tags = []
        if request.form['tags']:
            tags = request.form['tags'].split(",")


        # Filtering data
        content = content.replace("<p id=\"evernoteAttach\"><br></p>","").replace("<br>","").replace("id=\"evernoteAttach\"","").replace("></en-media>","/>")
   
        # Creating a note
        create_note(config.ACCESS_TOKEN,title,content,guid,fileList,tags)

    except Exception as e:
    	raise
    
    return jsonify(status=200,msg=config.MSG_NOTECREATE_OK)


@mod_note.route("/decrypt",methods=['POST'])
def decrypt_note():

    try:
        # Checking the GUID
        if not request.form['guid']:
            abort(400)
        guid = request.form['guid']


        # Checking that encrypted note is saved on local machine
        if (os.path.exists("notes/"+guid+"/") == False):
            abort(404)

        # Checking that "content.json" is there
        if (os.path.isfile("notes/"+guid+"/content.json") == False):
            abort(404)

        # Reading the "content.json"
        with open("notes/"+guid+"/content.json","r") as f:
            note = json.loads(f.read())

        # Getting a list of resources
        resources = []
        hash = ""
        data = None
        path = "notes/"+guid+"/"
        tmp_path = "static/tmp/"
        for filename in os.listdir("notes/"+guid+"/"):
            if "content.json" not in filename:
            
                # Reading file data into variale
                with open(path+filename,"rb") as f:
                    data = f.read()

                # Decrypting data
                data = decryptFileData(data,"testtest")

                # Writing data to temporary file
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
        tree = ET.fromstring(note.get('content'))
        noteContent = "".join( [ tree.text ] + [ ET.tostring(e) for e in tree.getchildren() ]);
        noteContent = decryptNote(noteContent,"testtest")
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
                    elif "application" in match['type']:
                        tag = soup.new_tag('a',href="/static/tmp/"+resource['name'])
                        tag.string = resource['name']
                    match.replaceWith(tag)        
        return soup.prettify()

    except Exception as e:
    	raise



@mod_note.route("/<string:GUID>",methods=['POST','GET'])
def note(GUID):
    try:
        if not GUID or GUID == "":
            abort(400)
            
        if request.method == "GET":
            return render_template("view.html",title="Application :: View note",guid=GUID)
        else:
            # Getting note
            note = get_note(config.ACCESS_TOKEN,GUID,False)
            return jsonify(note)
    except:
        raise