from flask import render_template
from evernote.edam.type.ttypes import NoteSortOrder, Note, Resource,Data, ResourceAttributes
import os,hashlib,safeglobals,copy,pickle,json,binascii
from libs.functions import fileMD5,getMime,stringMD5,encryptNote,encryptData,decryptNote,decryptFileData,is_backed_up,getIcon
from bs4 import BeautifulSoup, Tag
from libs.FavouritesManager import is_favourite


class Safenote(Note):
    def __init__(self):
        Note.__init__(self)

    @staticmethod
    def init_note(title,content,guid,tags=[]):

    	'''
            Function used to create the note object from the provided title, content and GUID. GUID is used to get a list of resources associated with note/page
    	'''

        # Initializing the note
        safenote = Safenote()
        safenote.title = title
        safenote.content = content

        # Adding tags if any
        if len(tags) > 0:
        	safenote.tagNames = tags

        # Checking that path exists
        resources = []
        path = safeglobals.path_note % (guid,"")
        if os.path.exists(path) == False:
        	return None

        for filename in os.listdir(path):
            if "content.json" not in filename:
                resources.append(Safenote.create_resource(os.path.join(path,filename)))

        safenote.resources = resources
        return safenote
    
    @staticmethod
    def create_resource(path):
        # Initializing variables
        hash = None 
        binary_data = None
        resource = None
        data = None

        # Checking if the file exists
        if os.path.isfile(path) == False:
        	return None

        # Reading the file content
        with open(path,"rb") as f:
        	binary_data = f.read()

        #  Calculating hash
        md5 = hashlib.md5()
        md5.update(binary_data)
        hash = md5.digest()

        # Initializing the data
        data = Data()
        data.size = len(binary_data)
        data.bodyHash = hash
        data.body = binary_data

        # Adding data to resource
        resource = Resource()
        resource.mime = getMime(os.path.basename(path))
        resource.data = data

        # Creating attributes
        attributes = ResourceAttributes()
        attributes.fileName = os.path.basename(path)
        resource.attributes = attributes

        return resource

    def encrypt(self,password,service=safeglobals.service_evernote):

    	# Temporary variable
    	content = ""

    	# Encrypting the content. Based on specified service, the content can be different
    	if service == safeglobals.service_onenote:
    		content = safeglobals.ENCRYPTED_PREFIX+stringMD5(content)+"__"+encryptNote(self.content,password)+safeglobals.ENCRYPTED_SUFFIX
    		self.content = "<html><head><title>%s</title></head><body>%s</body></html>" % (self.title,content)
    	else:
    		content = safeglobals.ENCRYPTED_PREFIX+stringMD5(content)+"__"+encryptNote(self.content,password)+safeglobals.ENCRYPTED_SUFFIX
    		self.content = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    		self.content += "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
    		self.content += "<en-note>%s</en-note>" % content

        # Encrypting the note resources
        temp_binary = None
        index = 0
        for resource in self.resources:

        	# Reading the data into temporary buffer
        	temp_binary = encryptData(resource.data.body,password)

        	# Calculating the hash of the encrypted data
        	md5 = hashlib.md5()
        	md5.update(temp_binary)
        	self.resources[index].data.bodyHash = md5.digest()
        	self.resources[index].data.size = len(temp_binary)
        	self.resources[index].data.body = temp_binary

        	index = index + 1

    def decrypt(self,password):

    	# Decrypting the content
    	self.content = decryptNote(self.content,password)

    	# Decrypting resources
    	temp_binary = None
    	decrypted_resources = []
        decrypted_resource = None
        hash = None
        index = 0

        for resource in self.resources:
            
            # Copying the existing resource into a new object
            decrypted_resource = copy.deepcopy(resource)

            # Encrypting the data
            temp_binary = decryptFileData(resource.data.body,password)
            md5 = hashlib.md5()
            md5.update(temp_binary)
            hash = md5.digest()

            # Setting a new data
            self.resources[index].data.body = temp_binary
            self.resources[index].data.bodyHash = hash
            self.resources[index].data.size = len(temp_binary)
            index = index + 1

            #with open(safeglobals.path_note % (self.guid,resource.attributes.fileName),"wb") as f:
            #	f.write(temp_binary)

    def backup(self,path=safeglobals.path_notes_backup):
    	with open(path % (self.guid),"wb") as f:
    		pickle.dump(self,f)

    def is_encrypted(self):
        if safeglobals.ENCRYPTED_SUFFIX in self.content:
            return True
        return False

    def is_backed_up(self):
        return os.path.isfile(safeglobals.path_notes_backup % self.guid)

    def is_favourite(self):
        return is_favourite(self.guid)

    # Function used to dump resources into files
    def dump_resources(self,path=safeglobals.path_tmp):
        for resource in self.resources:
            with open(os.path.join(path,resource.attributes.fileName),"wb") as f:
                f.write(resource.data.body)
    
    # Function used to render the note content into readable HTML
    def render(self,service=safeglobals.service_evernote):
        if service == safeglobals.service_onenote:
            return self.render_page()
        else:
            return self.render_note()

    # Function used to render Evernote note content into readable HTML
    def render_note(self):
        content = ""
        if self.is_encrypted() == True:
            return render_template("page.encrypted.html",service=safeglobals.service_evernote)
        else:

            # Dumping the resources
            self.dump_resources()

            # Getting the content
            content = self.content.split("<en-note>")[-1].replace("</en-note>","")

            # Parsing the content
            soup = BeautifulSoup(content,"html.parser")
            tag = None
            hash = None
            matches =  soup.find_all('en-media')

            for match in matches:
                for resource in self.resources:
                    hash = binascii.hexlify(resource.data.bodyHash)
                    if hash == match['hash'] or hash.upper() == match['hash'].upper():
                        if "image" in match['type']:
                            tag = soup.new_tag('img',style="width:100%",src="/"+os.path.join(safeglobals.path_tmp,resource.attributes.fileName))
                        elif safeglobals.MIME_PDF in match['type']:
                            tag = soup.new_tag("embed",width="100%", height="500",src="/"+os.path.join(safeglobals.path_tmp,resource.attributes.fileName)+"#page=1&zoom=50")
                        elif "application" in match['type']:
                            # Creating root div
                            tag = soup.new_tag("div",**{"class":"attachment"})

                            # Creating ICON span tag
                            icon_span_tag = soup.new_tag("span",style="margin-left:10px")
                            icon_img_tag = soup.new_tag("img",src="/static/images/"+getIcon(resource.mime))
                            icon_span_tag.append(icon_img_tag)

                            # Creating text tag
                            text_span_tag = soup.new_tag("span",style="margin-left:10px")
                            text_a_tag = soup.new_tag("a",href="/"+os.path.join(safeglobals.path_tmp,resource.attributes.fileName))
                            text_a_tag.string = resource.attributes.fileName
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

            return soup.prettify()                  

    # Function used to render Onenote page into readable HTML
    def render_page(self):
        content = ""
        if self.is_encrypted() == True:
            return render_template("page.encrypted.html",service=safeglobals.service_onenote)
        else:

            # Dumping the resources
            self.dump_resources()

            # Parsing the content
            soup = BeautifulSoup(self.content,"html.parser")
            matches = soup.find_all(["object","img"])
            hash = None
            resource = None
            tag = None
            
            for match in matches:
                if "img" in match.name:

                    # Getting hash
                    hash = match['src'].split(":")[1]

                    # Getting resource with a specific hash
                    resource = self.get_resource(hash)
                    if resource:
                        tag = soup.new_tag('img',style="width:100%",src="/"+os.path.join(safeglobals.path_tmp,resource.attributes.fileName))
                    else:
                        tag = soup.new_tag('img',style="width:100%",src="/"+os.path.join(safeglobals.path_tmp,"noimage.jpg"))

                elif "object" in match.name:

                    # Getting hash
                    hash = match['data'].split(":")[1]
                    
                    # Getting resource
                    resource = self.get_resource(hash)

                    if "image" in match['type']:
                        if resource:
                            tag = soup.new_tag('img',style="width:100%",src="/"+os.path.join(safeglobals.path_tmp,hash))
                        else:
                            tag = soup.new_tag('img',style="width:100%",src="/"+os.path.join(safeglobals.path_tmp,"noimage.jpg"))
                    elif "application" in match['type']:
                        
                        if resource:
                            
                            # Creating root div
                            tag = soup.new_tag("div",**{"class":"attachment"})

                            # Creating ICON span tag
                            icon_span_tag = soup.new_tag("span",style="margin-left:10px")
                            icon_img_tag = soup.new_tag("img",src="/static/images/"+getIcon(resource.mime))
                            icon_span_tag.append(icon_img_tag)

                            # Creating text tag
                            text_span_tag = soup.new_tag("span",style="margin-left:10px")
                            text_a_tag = soup.new_tag("a",href="/"+os.path.join(safeglobals.path_tmp,resource.attributes.fileName))
                            text_a_tag.string = resource.attributes.fileName
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
                        else:
                            tag = soup.new_tag('img',style="width:100%",src="/"+os.path.join(safeglobals.path_tmp,"noimage.jpg"))

                        

                match.replaceWith(tag)
            print soup.prettify()
            return soup.prettify()
            
    def get_resource(self,hash):
        for resource in self.resources:
            if binascii.hexlify(resource.data.bodyHash).upper() == hash.upper():
                return resource
        return None

    @staticmethod
    def get_from_backup(guid,path=safeglobals.path_notes_backup):
    	note = None
    	try:
            # Getting the note object from Backup file
            with open(path % (guid),"rb") as f:
            	note = pickle.load(f)
            return note
        except:
        	return note

    @staticmethod
    def to_html(guid,service=safeglobals.service_evernote):
        
        # Step 1. Checking the note has been saved on the local machine
        if os.path.exists(safeglobals.path_note % (guid,"")) == False:
        	return {"status":safeglobals.http_not_found,\
        	"note":None, \
        	"message":safeglobals.MSG_NOTE_MISSING % safeglobals.path_note % (guid,"")}

        # Step 2. Check if the "content.json" is there. If true, reading its content
        if os.path.isfile(safeglobals.path_note % (guid,"content.json")) == False:
        	return {"status":safeglobals.http_not_found,\
        	"note":None, \
        	"message":safeglobals.MSG_NOTE_MISSING % safeglobals.path_note % (guid,"content.json")}

    	if service == safeglobals.service_onenote:
    		return Safenote.page_to_html(guid)
    	else:
    		return Safenote.note_to_html(guid)
    
    @staticmethod
    def note_to_html(guid):
    	'''
            Function converts the downloaded note into readable HTML code
    	'''
    	note = None
    	with open(safeglobals.path_note % (guid,"content.json"),"r") as f:
    		note = json.loads(f.read())

    	# Checking if note is encrypted or not
    	if safeglobals.ENCRYPTED_SUFFIX in note['content']:
    		note['content'] = render_template("page.encrypted.html",service=safeglobals.service_evernote)
    		note['encrypted'] = True
        else:
        	
        	# Step 3. Getting a list of attachments (if any)
            resources = []
            path = safeglobals.path_note % (guid,"")
            for filename in os.listdir(path):
                if "content.json" not in filename:
                # Adding to the list of resources
                    resources.append({"name":filename,\
                	    "hash":fileMD5(os.path.join(path,filename)),\
                	    "mime":getMime(os.path.join(path,filename))})

            # Step 4. Rendering the note content
            note['content'] = prepare_content(service_evernote,note['content'],resources,path="/static/tmp/"+guid+"/")
            note['encrypted'] = False

        # Checking if the note is in Favourites and whether it is backed up
        note['favourite'] = is_favourite(guid)
        note['backup'] = is_backed_up(guid)
        return note

    @staticmethod
    def page_to_html(guid):

    	# Reading the "content.json"
    	note = None
    	with open(safeglobals.path_note % (guid,"content.json"),"r") as f:
    		note = json.loads(f.read())

        # Checking if note is encrypted or not
        if safeglobals.ENCRYPTED_SUFFIX in note['content']:
        	note['content'] = render_template("page.encrypted.html",service=safeglobals.service_onenote)
        	note['encrypted'] = True
        else:
            # Step 4. Rendering the note content
            note['content'] = note['content'].replace("></embed>","/>")
            note['encrypted'] = False

        # Checking if the note is in Favourites and whether it is backed up
        note['favourite'] = is_favourite(guid)
        note['backup'] = is_backed_up(guid)        

        # Sending the response
        return {"status":safeglobals.http_ok,"note":note, "message":""}

    @staticmethod
    def from_file(path,service=safeglobals.service_evernote):
        '''
            Function used to create the note object from text file
        '''

        temp = None
        
        # Checking if path exists
        if os.path.exists(os.path.join(path)) == False:
            return None

        # Checking if "content.json" exists
        if os.path.isfile(os.path.join(path,"content.json")) == False:
            return None

        # Reading the file content into temp variable
        with open(os.path.join(path,"content.json")) as f:
            temp = json.loads(f.read())
        
        # Initializing the note
        note = Safenote()
        note.title = temp['title']
        note.content = Safenote.get_content(temp['content'])
        
        # Reading resources
        note.resources = []
        for filename in os.listdir(path):
            if "content.json" not in filename:
                note.resources.append(Safenote.create_resource(os.path.join(path,filename)))

        return note
    
    @staticmethod
    def get_content(content):        
        return content[content.find(safeglobals.ENCRYPTED_PREFIX)+len(safeglobals.ENCRYPTED_PREFIX):content.find(safeglobals.ENCRYPTED_SUFFIX)].strip();