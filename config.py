# Services
services = {"evernote":True,"onenote":True}
service_evernote = 0 # Evernote Service ID
service_onenote = 1  # Onenote Service ID
 
# Evernote credentials
ACCESS_TOKEN = "<developer_token>"
NOTE_URL = "https://www.evernote.com/shard/s401/notestore"
  
# Onenote credentials
on_client_secret = "<client_secret>"
on_client_id = "<client_id>"
on_redirect_uri = "https://www.saferoomapp.com:5000/onenote/callback"
on_token_redirect_uri = "https://www.saferoomapp.com:5000/onenote/token"
on_scopes = "wl.signin%20Office.onenote%20wl.offline_access%20Office.onenote_create"
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
path_note = "static/tmp/%s/%s"
path_cache = "cache/"
path_tmp = "static/tmp/"
path_notes_evernote = "cache/notes_%s_%s.json"

 
# Onenote URLs
url_notebooks = "https://www.onenote.com/api/v1.0/me/notes/notebooks"
url_sections = "https://www.onenote.com/api/v1.0/me/notes/notebooks/%s/sections"
url_notes = "https://www.onenote.com/api/v1.0/me/notes/sections/%s/pages"
url_note = "https://www.onenote.com/api/v1.0/me/notes/pages/%s"
url_note_content = "https://www.onenote.com/api/v1.0/me/notes/pages/%s/content"

# Evernote variables
PREMIUM_STATUS = {"0": "None","1":"Pending","2":"Active","3":"FAILED","4":"Cancellation pending","5":"CANCELLED"}
PRIVILEGE_LEVEL = {"1":"Normal","3":"Premium"}
  
# Saferoom variables (do not change it. Otherwise you won't be able to decrypt notes on other platforms)
ENCRYPTED_PREFIX = "TUFNTU9USEVOQ1JZUFRFRE5PVEU=__"
ENCRYPTED_SUFFIX = "__TUFNTU9USEVOQ1JZUFRFRE5PVEU="
  
# HTML templates
html_attach = "<div class=\"attachment\"><div class=\"row\"><div class=\"col-md-10\" style=\"display:inline-block\"><span style=\"margin-left:10px\"><img src=\"/static/images/::fileicon::\"/></span><span style=\"margin-left:10px\"><a href=\"static/tmp/::filename::\">::filename::</a></span></div><div class=\"col-md-2\"></div></div></div><br/>"
  
# Success messages
MSG_NOTECREATE_OK = "Note has been successfully created and uploaded to the server"
MSG_LINKCREATE_OK = "Quick link has been successfully created"
MSG_INTERNAL_ERROR = "Internal server error. Please check logs"
MSG_NO_TOKENS = "No tokens founds or your Access Token has expired. Please check that ["+path_tokens+"] file exists or check the refresh token inside this file. Refresh token is needed to get a new access token. If you don't have access and refresh tokens, please login to your Onenote account"
MSG_ONLOGIN_OK = "You've successfully connected your application to your Onenote account. All tokens were saved into ["+path_tokens+"] file. Please don't update and delete this file. If you accidentally lost it, you can always get new tokens by initiating the login procedure"
MSG_TOKENREFRESH_OK = "Access token has been successfully refreshed"
MSG_UNAUTHORIZED = "Server returned '401 Unauthorized' to your request. Please check if your Access Token expires or not"
MSG_RESPONSE_ERROR = "Error while processing your request. Server response: %s -  %s"
MSG_MANDATORY_MISSING = "Mandatory data is missing"
MSG_NOTE_MISSING = "Note content is missing. Please make sure that encrypted note exists in [ %s ]"
ERROR_FILE_DOWNLOAD = "Error while downloading file. Response code: %s"
  
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

# HTTP response
http_ok = 200
http_unauthorized = 401
http_not_found = 404
http_forbidden = 403
http_internal_server = 500
http_bad_request = 400