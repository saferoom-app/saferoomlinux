# Import section
import datetime
import hashlib
import binascii
import rncryptor
import base64
import config


def millisToDate(timestamp):
	millis = float(timestamp)
	s = millis/1000.0
	return datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f')[:-7]

def str_to_bool(s):
    if s == 'True':
        return True
    elif s == 'False':
        return False

def stringMD5(source):
    m = hashlib.md5()
    m.update(source)
    return m.hexdigest()

def fileMD5(filename):
    with open(filename,"rb") as f:
        data = f.read()
        md5 = hashlib.md5()
        md5.update(data)
        hash = md5.digest()
        return binascii.hexlify(hash)


def encryptString(string,key):
    cryptor = rncryptor.RNCryptor()
    encrypted_string = cryptor.encrypt(string,key)
    return base64.b64encode(encrypted_string)

def decryptString(string,key):
    cryptor = rncryptor.RNCryptor()
    encrypted_string = base64.b64decode(string)
    decrypted_string = cryptor.decrypt(encrypted_string,key)
    return decrypted_string

def encryptNote(noteContent,password):
    cryptor = rncryptor.RNCryptor()
    encrypted_data = cryptor.encrypt(noteContent,password)
    return base64.b64encode(encrypted_data)

def encryptData(data,password):
    cryptor = rncryptor.RNCryptor()
    encrypted_data = cryptor.encrypt(data,password)
    return encrypted_data

def decryptNote(noteContent,password):

    # Filtering content
    noteContent = noteContent.replace(config.ENCRYPTED_PREFIX,"").replace(config.ENCRYPTED_SUFFIX,"");
    array = noteContent.split("__")
    noteContent = array[1]

    cryptor = rncryptor.RNCryptor()
    content = base64.b64decode(noteContent)
    decrypted_data = cryptor.decrypt(content,password)
    return decrypted_data

def decryptFileData(data,password):
    cryptor = rncryptor.RNCryptor()
    decrypted_data = cryptor.decrypt(data,password)
    return decrypted_data


def getMime(fileName):

    # Getting file extension
    array = fileName.split(".")
    extension = array[-1]

    # Getting MIME
    if (extension == "pdf"):
        return "application/pdf"
    elif extension == "doc" or extension == "docx":
        return ""
    elif extension == "xls" or extension == "xlsx":
        return ""
    elif extension == "ppt" or extension == "pptx":
        return ""
    elif extension == "jpg" or extension == "jpeg":
        return "image/jpeg"
    elif extension == "gif":
        return "image/gif"
    elif extension == "png":
        return "image/png"

def getIcon(mime):

    if mime == config.MIME_PDF:
        return "icon_pdf.png"
    elif mime == config.MIME_DOC or mime == config.MIME_DOCX:
        return "icon_word.png"
    elif mime == config.MIME_XLS or mime == config.MIME_XLSX:
        return "icon_excel.png"
    elif mime == config.MIME_PPT or mime == config.MIME_PPTX:
        return "icon_ppt.png"
    else:
        return "icon_doc.png"


def generateKey(os,user,salt):
    m = hashlib.md5()
    m.update(os+user+salt)
    return m.hexdigest()