ACCESS_TOKEN = "<developer_token>"
NOTE_URL = "https://www.evernote.com/shard/s401/notestore"
ERROR_LOG_FILE = "error.log"

# Paths
path_favourites = "notes/favourites/favourites.json"
path_quicklinks = "notes/favourites/quicklinks.json"
path_password = ".saferoompwd"

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

# Response types
TYPE_JSON = "json"
TYPE_TABLE = "table"
TYPE_SELECT = "select"
TYPE_LIST = "list"

