# Services
service_evernote = "0" # Evernote Service ID
service_onenote = "1"  # Onenote Service ID
 
# Evernote credentials
NOTE_URL = "https://www.evernote.com/shard/s401/notestore"

# Evernote/Onenote service variables
evernote_offset = 0
evernote_maxnotes = 100
  
# Onenote credentials
on_response_type = "code"
on_path = "/oauth20_authorize.srf?client_id=%s&scope=%s&response_type=%s&redirect_uri=%s"
on_token_url = "https://login.live.com/oauth20_token.srf"
on_hostname = "login.live.com"
  
# Common credentials
ERROR_LOG_FILE = "error.log"
SALT = "c2e828e0-79f8-41cc-8155-02ab40699714"
  
# Paths
path_favourites = "notes/favourites/favourites.json"
path_quicklinks = "notes/favourites/quicklinks.json"
path_password = ".saferoompwd"
path_tokens = ".tokens"
path_notebooks_evernote = "cache/notebooks.json"
path_notebooks_onenote = "cache/notebooks_on.json"
path_tags = "cache/tags.json"
path_searches = "cache/searches.json"
path_sections = "cache/section_%s.json"
path_notes = "cache/notes_%s.json"
path_logfile = "logs/server.log"
path_note_backup = "static/tmp/%s.pickle"
path_note = "static/tmp/%s/%s"
path_cache = "cache/"
path_tmp = "static/tmp/"
path_notes_evernote = "cache/notes_%s_%s.json"
path_notes_backup = "static/backups/%s.pickle"
path_notes_encryptedbackups = "static/tmp/%s.encrypted.pickle"

 
# Onenote URLs
url_api = "https://www.onenote.com/api/v1.0/me/"
url_notebooks = "https://www.onenote.com/api/v1.0/me/notes/notebooks"
url_sections = "https://www.onenote.com/api/v1.0/me/notes/notebooks/%s/sections"
url_sections_all = "https://www.onenote.com/api/v1.0/me/notes/sections"
url_notes = "https://www.onenote.com/api/v1.0/me/notes/sections/%s/pages"
url_note = "https://www.onenote.com/api/v1.0/me/notes/pages/%s"
url_note_content = "https://www.onenote.com/api/v1.0/me/notes/pages/%s/content"
url_post_page = "https://www.onenote.com/api/v1.0/me/notes/sections/%s/pages"
url_patch_page = "https://www.onenote.com/api/v1.0/me/notes/pages/%s/content"
url_delete_page = "https://www.onenote.com/api/v1.0/me/notes/pages/%s"

# Evernote variables
PREMIUM_STATUS = {"0": "None","1":"Pending","2":"Active","3":"FAILED","4":"Cancellation pending","5":"CANCELLED"}
PRIVILEGE_LEVEL = {"1":"Normal","3":"Premium"}
  
# Saferoom variables (do not change it. Otherwise you won't be able to decrypt notes on other platforms)
ENCRYPTED_PREFIX = "TUFNTU9USEVOQ1JZUFRFRE5PVEU=__"
ENCRYPTED_SUFFIX = "__TUFNTU9USEVOQ1JZUFRFRE5PVEU="
ONENOTE_PAGE_PREFIX = "<html><head><title></title><link type=\"text/css\" rel=\"stylesheet\" href=\"/static/css/bootstrap.min.css\"/></head><body style='font-size:12px'>%s</body></html>"

# Display modes
NOTES_ENCRYPTED_ONLY = 0
NOTES_UNENCRYPTED_ONLY = 1
NOTES_ALL = 2
  
# HTML templates
html_attach = "<div class=\"attachment\"><div class=\"row\"><div class=\"col-md-10\" style=\"display:inline-block\"><span style=\"margin-left:10px\"><img src=\"/static/images/::fileicon::\"/></span><span style=\"margin-left:10px\"><a href=\"static/tmp/::filename::\">::filename::</a></span></div><div class=\"col-md-2\"></div></div></div><br/>"
html_onenote_image = "<img src=\"name:%s\"/>"
html_onenote_object = "<object data-attachment=\"%s\" data=\"name:%s\" type=\"%s\"/>"
html_image_template = "<img src='name:%s' data-filename='%s'/>"
  
# Success messages
MSG_NOTECREATE_OK = "Note has been successfully created and uploaded to the server"
MSG_LINKCREATE_OK = "Quick link has been successfully created"
MSG_INTERNAL_ERROR = "Internal server error. Please check logs"
MSG_NO_DEVTOKEN = "Developer token not found. Please make sure that correct Evernote developer token is specified in [config.ini]"
MSG_NO_TOKENS = "No tokens founds or your Access Token has expired. Please check that ["+path_tokens+"] file exists and it contains access and refresh tokens. Refresh token is needed to get a new access token. If you don't have access and refresh tokens, please login to your Onenote account"
MSG_ONLOGIN_OK = "You've successfully connected your application to your Onenote account. All tokens were saved into ["+path_tokens+"] file. Please don't update and delete this file. If you accidentally lost it, you can always get new tokens by initiating the login procedure"
MSG_TOKENREFRESH_OK = "Access token has been successfully refreshed"
MSG_UNAUTHORIZED = "Server returned '401 Unauthorized' to your request. Please check if your Access Token expires or not"
MSG_RESPONSE_ERROR = "Error while processing your request. Server response: %s -  %s"
MSG_MANDATORY_MISSING = "Mandatory data is missing"
MSG_NOTE_MISSING = "Note content is missing. Please make sure that encrypted note exists in [ %s ]"
MSG_ONDATA_MISSING = "Mandatory data missing. To login to Onenote account you need to specify Client ID, Client Secret, Scopes and Redirect URI in [config.ini] file"
MSG_CONFIG_OK = "Configuration has been successfully saved"
MSG_UPDATENOTE_OK = "Note has been successfully updated. Click [Update] to download the latest version"
MSG_PASSWORD_CHECK = "Checking master password"
MSG_TOKEN_CHECK =  "Checking %s tokens"
MSG_FILE_NOTFOUND = "[Error]: File not found. Please check that file [%s] exists"
MSG_COPY_TOTMP = "Copying file to Saferoom temporary folder"
MSG_COPY_ERROR = "[Error]: Error while copying file into Saferoom temp folder. Please try again"
MSG_MASTERPASS_NOTFOUND = "[Error]: Master password not found. Use One-Time password or generate new master password"
MSG_OTPPASS_NOTFOUND = "[Error]: One-Time password not specified. Use Master password or specify One-Time password"
MSG_DOWNLOAD_NOTES = "Downloading a list of notes to be encrypted/restored/reencrypted"
MSG_BACKUP_CHECK = "Checking that backups have been created"
MSG_BACKUP_CREATED = "[INFO] Backups have been created (%s)"
MSG_NOENCRYPTED_NOTES = "No unencrypted notes found"
MSG_NO_PASSWORDS = "\n    [ERROR]: Current and/or new password are not specified. Please use --password and --oldpassword options to specify passwords. For more information type 'python cli.py notes -h'"
MSG_LABEL_OK = "[OK]\n"
MSG_LABEL_DONE = "[Done]"
MSG_LABEL_NOK = "[NOK]\n"
MSG_CREATE_NOTE = "Creating encrypted note"
MSG_INIT = "Initializing"
MSG_ENCRYPT_NOTE = "Encrypting <strong><u>%s</u></strong>"
MSG_DOWN_BACKUP = "Downloading and backing up notes"
MSG_DECRYPT_ERROR = "[Wrong password]"

# Error messages
ERROR_FILE_DOWNLOAD = "Error while downloading file. Response code: %s"
ERROR_NO_TOKEN = "No access token found. Please check the [config.ini] for Evernote token or [.tokens] file for Onenote tokens"
ERROR_NO_PASSWORD = "No password specified. Either you have not generated Master password or you have specified empty OTP password"
ERROR_NO_BACKUP = "[Error]: [%s] backup not found"
ERROR_BACKUP_NOK = "[NOK: Backup not found]"

# Titles
TITLE_PRELIM_CHECK = "Performing preliminary check"
TITLE_ENCRYPT_FILE = "Encrypting file"
TITLE_DOWNLOAD_BACKUP_NOTES = "Downloading and backing up specified notes"
TITLE_CHECK_BACKUPS = "Checking that backups are created"
TITLE_ENCRYPT_NOTES = "Encrypting notes"
TITLE_RESTORE_NOTES = "Restoring notes from the backup"
TITLE_REENCRYPT_NOTES = "Downloading and encrypting notes with a new password"
 
# Response types
TYPE_JSON = "json"
TYPE_TABLE = "table"
TYPE_SELECT = "select"
TYPE_LIST = "list"
TYPE_HTML = "html"

# MIME types
MIME_PDF = "application/pdf"
MIME_DOC = "application/msword"
MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MIME_XLS = "application/vnd.ms-excel"
MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
MIME_PPT = "application/vnd.ms-powerpoint"
MIME_PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
MIME_JPEG = "image/jpeg"
MIME_GIF = "image/gif"
MIME_PNG = "image/png"
MIME_DEFAULT = "text/*"

# Collection of MIMES
MIME_TYPES = {"pdf":MIME_PDF,"docx":MIME_DOCX,"doc":MIME_DOC,"xls":MIME_XLSX,"xlsx":MIME_XLSX,\
"ppt":MIME_PPT,"pptx":MIME_PPTX,"jpeg":MIME_JPEG,"jpg":MIME_JPEG,"gif":MIME_GIF,"png":MIME_PNG}

# HTTP response
http_ok = 200
http_unauthorized = 401
http_not_found = 404
http_forbidden = 403
http_internal_server = 500
http_bad_request = 400

