# Import section
import argparse,os,safeglobals

# Function used to init the parser
def init_parser():
    
    # Creating argument parser
    new_parser = argparse.ArgumentParser(description="The script is used to automate Saferoom encryption procedures")
    subparsers = new_parser.add_subparsers(help='sub-command help')

    # Encrypt parser
    parser_encrypt = subparsers.add_parser('encrypt', help='Encrypt specified file and upload it to specified service')
    parser_encrypt.add_argument("--service","-s",help="Service to upload your encrypted file",default="evernote",choices=['evernote','onenote'])
    parser_encrypt.add_argument("--file","-f",help="Files to be encrypted and uploaded to specified service. If you want to attach multiple files, separate them by comma. For example, \"/home/user/test.pdf, /var/home/test2.pdf\"")
    parser_encrypt.add_argument("--title","-t",help="Note title",default="Untitled")
    parser_encrypt.add_argument("--mode","-m",help="Encryption mode: encrypt file using Master or One-Time password",default="master",choices=['master','otp'])
    parser_encrypt.add_argument("--key","-k",help="Encryption password. If mode is set to [otp], then this value is mandatory",default="")
    parser_encrypt.add_argument("--container","-c",required=True,help="Container ID. In case of Evernote service this is Notebook's GUID. In case of Onenote service, it is a Section GUID. Notebook GUID can be found using 'list --service evernote --type notebooks' command. List of sections GUID can be found using 'list --service onenote --type sections' command",default="")
    parser_encrypt.set_defaults(which='encrypt')


    # Note parser
    parser_notes = subparsers.add_parser('notes', help='The operations with the notes',usage='notes [operation] [options]\n\n Supported operations are the following:\n\n    >> list: list the notes from specified notebook\n       Example: python cli.py notes list --container <notebook_guid>\n\n    >> encrypt: encrypt the existing notes in the specified notebook. If note GUID is not specified, the application will encrypt all notes in notebook\n       Example: python cli.py notes encrypt --container <notebook_guid> --guid <note_guid>\n\n    >> restore: restore the notes from the backups. Backups are generated in static/tmp/backups folder in the format [<note_guid>.pickle]. \n       If note GUID is not specified, then all notes that have backups will be restored \n\n       Example: python cli.py notes restore --container <notebook_guid> --guid <note_guid>\n\n    >> reencrypt: reencrypt the note(s) with a new password\n       If note GUID is not specified, then all notes in the specified notebook will be reencrypted \n\n       Example: python cli.py notes reencrypt --container <notebook_guid> --guid <note_guid> --password <new_password> --oldpassword <old_password>')
    parser_notes.add_argument("operation",nargs='?',help="The operation to perform on notes. Supported operations are: list, encrypt, restore, reencrypt")
    parser_notes.add_argument("--container","-c",required=True,help="Evernote notebook's GUID")
    parser_notes.add_argument("--name","-n",help="Specify the name of note to display. You can type a part of note's name to find it",default="")
    parser_notes.add_argument("--guid","-g",help="The GUID of the note you want to encrypt. If GUID is not specified, all unencrypted notes will be encrypted",default="")
    parser_notes.add_argument("--password", "-p",help="Password used to encrypt the notes. If not specified, master password will be used instead", default="")
    parser_notes.add_argument("--oldpassword","-o",help="If you want to encrypt notes with a new password, this parameter is used to specify the decryption password, i.e the password used to encrypt these notes before (old master or OTP password)",default="")
    parser_notes.set_defaults(which='notes')


    # List parser
    parser_list = subparsers.add_parser('list', help='List the Evernote/Onenote notebooks and sections')
    parser_list.add_argument("--service","-s",help="Specify service for which you want to retrieve a list of notebooks or sections",default="evernote",choices=['evernote','onenote'])
    parser_list.add_argument("--type","-t",help="Specify the type of returned information",default="notebooks",choices=['sections','notebooks'])
    parser_list.add_argument("--refresh","-r",help="By default downloaded all notebooks and sections are cached. If this option is 'true' the application will ignore the cached values and download data from the remote server. By default all values are read from cache",default=False,choices=[True,False],type=bool)
    parser_list.add_argument("--name","-n",help="Specify the name of notebook to display. You can type a part of notebook's name to find it",default="",type=str)

    parser_list.set_defaults(which='list')

    return new_parser