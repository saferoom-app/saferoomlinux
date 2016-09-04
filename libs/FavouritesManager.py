import safeglobals
import json
import os


# Getting a list of favourites
def list_favourites():
	favourites = []

	# Checking if "favourites.json" exist
	if os.path.isfile(safeglobals.path_favourites) == False:
		return favourites

	# Loading a list of favourites
	with open(safeglobals.path_favourites,"r") as f:
		favourites = json.loads(f.read())

	return favourites


def add_to_favourites(item):

	# Getting a list of favourites
	favourites = list_favourites()

	# Adding new item
	favourites.append(item)

	# Saving new list of favourites
	with open(safeglobals.path_favourites,"w") as f:
		f.write(json.dumps(favourites))


def remove_from_favourites(guid):

	# Getting a list of favourites
	favourites = list_favourites()

	# Removing the Favourite Item with selected ID
	index = 0
	for item in favourites:
		if guid == item['guid']:
			favourites.pop(0)

	# Saving list of favourites back into file
	with open(safeglobals.path_favourites,"w") as f:
		f.write(json.dumps(favourites))



def is_favourite(guid):

	# Getting a list of favourites
	favourites = list_favourites()

	# Checking if it is in favourites
	for item in favourites:
	    if item['guid'] == guid:
	        return True 
	return False


def list_quick_links():

	links = []
	try:
		with open(safeglobals.path_quicklinks,"r") as f:
			links = json.loads(f.read())
		return links
	except:
		return links

def add_quick_link(name,link):

	# Get current list of quick links (if exists)
	links = list_quick_links()

	# Add a new link to the list
	links.append({"name":name,"link":link})

	# Saving links to file
	save_quick_links(links)


def save_quick_links(links):

	try:
		with open(safeglobals.path_quicklinks,"w") as f:
			f.write(json.dumps(links))
	except Exception as e:
		pass