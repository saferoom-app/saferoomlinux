'''
CLI utility used to automate some procedures

'''

# Import section
import argparse
from libs.ConfigManager import get_developer_token
from libs.PasswordManager import get_master_password
from libs.OnenoteManager import is_access_token_valid
from libs.functions import fileMD5,encryptData
import os
import safeglobals
from shutil import copyfile
from libs.EvernoteManager import list_notebooks,create_note
from libs.OnenoteManager import list_on_notebooks,get_access_token,load_sections_all
from libs.texttable import Texttable
from mimetypes import MimeTypes


# Global section
msg_no_devtoken = "[Error]: Evernote developer token not found. Please check [config.ini] file"
msg_no_onenotetokens = "[Error]: Onenote Access Token not found or expired. Please check [.tokens] file in the root folder"
msg_password_check = "Checking master password"
msg_devtoken_check = "Checking Evernote developer token"
msg_onenotetoken_check = "Checking Onenote tokens"
msg_file_notfound = "[Error]: File not found. Please check that file [%s] exists"
msg_copy_totmp = "Copying file to Saferoom temporary folder"
msg_copy_error = "[Error]: Error while copying file into Saferoom temp folder. Please try again"
msg_masterpass_notfound = "[Error]: Master password not found. Use One-Time password or generate new master password"
msg_otppass_notfound = "[Error]: One-Time password not specified. Use Master password or specify One-Time password"


# Creating argument parser
new_parser = argparse.ArgumentParser(description="The script is used to automate Saferoom encryption procedures")
subparsers = new_parser.add_subparsers(help='sub-command help')

# Encrypt parser
parser_encrypt = subparsers.add_parser('encrypt', help='Encrypt specified file and upload it to specified service')
parser_encrypt.add_argument("--service","-s",help="Service to upload your encrypted file",default="evernote",choices=['evernote','onenote'])
parser_encrypt.add_argument("--file","-f",help="File to be encrypted and uploaded to specified service")
parser_encrypt.add_argument("--title","-t",help="Note title",default="Untitled")
parser_encrypt.add_argument("--mode","-m",help="Encryption mode: encrypt file using Master or One-Time password",default="master",choices=['master','otp'])
parser_encrypt.add_argument("--key","-k",help="Encryption password. If mode is set to [otp], then this value is mandatory",default="")
parser_encrypt.add_argument("--container","-c",required=True,help="Container ID. In case of Evernote service this is Notebook's GUID. In case of Onenote service, it is a Section GUID. Notebook GUID can be found using 'list --service evernote --type notebooks' command. List of sections GUID can be found using 'list --service onenote --type sections' command",default="")
parser_encrypt.set_defaults(which='encrypt')

# List parser
parser_list = subparsers.add_parser('list', help='List the Evernote/Onenote notebooks and sections')
parser_list.add_argument("--service","-s",help="Specify service for which you want to retrieve a list of notebooks or sections",default="evernote",choices=['evernote','onenote'])
parser_list.add_argument("--type","-t",help="Specify the type of returned information",default="notebooks",choices=['sections','notebooks'])
parser_list.add_argument("--refresh","-r",help="By default downloaded all notebooks and sections are cached. If this option is 'true' the application will ignore the cached values and download data from the remote server. By default all values are read from cache",default=False,choices=[True,False],type=bool)
parser_list.add_argument("--name","-n",help="Specify the name of notebook to display. You can type a part of notebook's name to find it",default="",type=str)

parser_list.set_defaults(which='list')
option = new_parser.parse_args()
check = {}

# Functions section
def list_items(service,type,refresh):
    items = []
    notebooks = []
    sections = []
    if (service == "evernote"):
        if (type == "notebooks"):
            # Loading a list of notebooks
            notebooks = list_notebooks(get_developer_token(),refresh)

            # Collecting items
            for notebook in notebooks:
                items.append({"name":notebook['name'].encode('utf-8'),"guid":notebook['guid'].encode('utf-8')})
    elif (service == "onenote"):
        if type == "notebooks":
            notebooks = list_on_notebooks(get_access_token(),refresh)
            for notebook in notebooks:
                items.append({"name":notebook['text'],"guid":notebook['guid']})
        elif type == "sections":
            sections = list_sections_all(get_access_token())
            for section in sections:
                items.append({"name":section['text'],"guid":notebook['guid']})

    # Return items
    return items


''' 
Performing preliminary check
 1. Checking if master password has been created
 2. Checking Evernote developer token
 3. Checking Onenote tokens and if they exist, check if not expired

'''

print ""
print "============================================="
print "         Performing preliminary check        "
print "============================================="

# Checking Master password
print ""
print("    "+msg_password_check+" ......"),
check['master_password'] = (get_master_password() != "")
if check['master_password'] == True:
	print "[OK]"
else:
	print "[NOK]"
print ""

# Checking Evernote developer token
print("    "+msg_devtoken_check+" ......"),
check['developer_token'] = (get_developer_token() != "")
if check['developer_token'] == True:
	print "[OK]"
else:
	print "[NOK]"
print ""

# Checking Onenote tokens
print("    "+msg_onenotetoken_check+" ......"),
check['onenote_token'] = is_access_token_valid()
if check['onenote_token'] == True:
	print "[OK]"
else:
	print "[NOK]"
print ""

# Executing command

'''
  ============================================================
            Encryption block
  ============================================================
'''
if option.which == "encrypt":
    print ""
    print "============================================="
    print "         Encrypting file                     "
    print "============================================="

    # Checking that specified file exists
    if os.path.isfile(option.file) == False:
        print "\n    "+msg_file_notfound % (option.file)+"\n"
        exit()

    # Copying file to Saferoom temp folder
    dst_path = os.path.join(os.getcwd(),safeglobals.path_tmp,os.path.basename(option.file));
    print ""
    print("    "+msg_copy_totmp+" ......"),
    copyfile(option.file,dst_path)
    if os.path.isfile(dst_path) == True:
        print "[OK]\n"
    else:
        print "[NOK]\n"
        print msg_copy_error
        exit()

    # Calculating original file hash (this is needed for Evernote and Onenote services)
    mime_type = MimeTypes()
    fileList = [{"name":os.path.basename(option.file),"hash":fileMD5(dst_path),"mime":mime_type.guess_type(option.file)[0]}]
    
    # Checking password
    print("    Creating a note ......"),
    if option.mode == "master":
        if check['master_password'] == False:
            print "[NOK]"
            print "    "+msg_masterpass_notfound
            exit()
        password = get_master_password()
    elif option.mode == "otp":
        if option.key == "":
            print "[NOK]\n    "+ msg_otppass_notfound
            exit()
        password = option.key

    # Creating a content
    content = []
    data = None
    for file in fileList:
        content.append("<en-media type=\""+file['mime']+"\" hash=\""+file['hash']+"\"/><br/>")

    # Creating a note
    create_note(get_developer_token(),option.title,"".join(content),option.container,fileList,[],password)

elif option.which == "list":
    # Checking the developer token
    if option.service == "evernote" and check['developer_token'] == False:
        print ""
        print "    "+msg_no_devtoken
        print ""
        exit()

    # Checking the Onenote access tokens
    if option.service == "onenote" and check['onenote_token'] == False:
    	print ""
        print "    "+msg_no_onenotetokens
        print ""
        exit()

    # Getting items
    items = list_items(option.service,option.type,option.refresh)
    
    # Displaying a table
    table = Texttable()
    table.set_cols_align(["c", "c"])
    table.set_cols_valign(["m", "m"])
    table.add_row(["Name", "GUID"])
    for item in items:
    	if (option.name != ""):
    		if option.name in item['name'].encode("utf-8"):
    			table.add_row([item['name'].encode("utf-8"),item['guid'].encode("utf-8")])
    	else:
    		table.add_row([item['name'].encode("utf-8"),item['guid'].encode("utf-8")])
    print table.draw()

elif option.which == "decrypt":
	exit()