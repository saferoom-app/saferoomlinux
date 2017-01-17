# Import section
import safeglobals,binascii,base64,pickle
from libs.EvernoteManager import get_from_backup
from bs4 import BeautifulSoup, Tag
from libs.functions import getIcon

# Functions section
def render_backup(guid,service):

	if service == safeglobals.service_evernote:
		return render_evernote_backup(guid)
	elif service == safeglobals.service_onenote:
		return render_onenote_backup(guid)
	else:
		return None

def render_evernote_backup(guid):
    """ Function used to render the Evernote backup into readable HTML """

    # Getting the note from the backup
    note = get_from_backup(guid)
    if not note:
        return None
 
    # Getting the note content (real content with stripped <en-note> tags)
    content = note.content.split("<en-note>")[-1].replace("</en-note>","")
    
    # Parsing resources
    soup = BeautifulSoup(content,"html.parser")
    tag = None
    hash = ""
    matches =  soup.find_all('en-media')
    for match in matches:
        for resource in note.resources:
            hash = binascii.hexlify(resource.data.bodyHash)
            if  hash == match['hash'] or hash.upper() == match['hash'].upper():
                if "image" in match['type']:
                    tag = soup.new_tag('img',style="width:100%",src="data:%s;base64,%s" % (resource.mime,base64.b64encode(resource.data.body)))
                elif safeglobals.MIME_PDF in match['type']:
                    tag = soup.new_tag("embed",width="100%", height="500",src="data:application/pdf;base64,%s" % base64.b64encode(resource.data.body) )
                elif "application" in match['type']:
                    # Creating root div
                    tag = soup.new_tag("div",**{"class":"attachment"})

                    # Creating ICON span tag
                    icon_span_tag = soup.new_tag("span",style="margin-left:10px")
                    icon_img_tag = soup.new_tag("img",src="/static/images/"+getIcon(resource.mime))
                    icon_span_tag.append(icon_img_tag)

                    # Creating text tag
                    text_span_tag = soup.new_tag("span",style="margin-left:10px")
                    text_a_tag = soup.new_tag("a",href="")
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