# Saferoom
Encryption extension to Evernote and Onenote platforms

# Installation
## Ubuntu
This section contains the instructions for installing the environment required by Saferoom app. This procedure was tested on **Ubuntu desktop 16.04**. Below we assume that everything is done under **root** user. If you're using non-root user, every command should be preceeded by **sudo**
### Checking Python version
Open terminal and check that Python is installed on your system (it should be installed by default, but nevertheless)
```
python --version
```
This application was tested with **Python 2.7** version

### Installing PIP and git

Install Python PIP utility using the following command
```
apt-get install python-pip
```
After the installation make sure that PIP has been successfully installed
```
pip --version
```

Install GIT client using the following command:
```
apt-get install git
```

### Installing Flask, Requests and Pycrypto

Saferoom is using [Flask Python microframework](http://flask.pocoo.org/). To install Flask type the following command:
```
pip install flask
```

**Requests** is a [Python module](http://docs.python-requests.org/en/master/) used to work with HTTP requests. TO install this module, type the following command:

```
pip install requests
```

Pycrypto library is needed to perform cryptographic operations (encryption and decryption). Pycrypto is installed using the following command:
```
pip install pycrypto
```

### Installing Evernote Python SDK and BeautifulSoup4

Evernote Python SDK is used to interact with Evernote API. The installation steps are the following:

```
cd /tmp
git clone https://github.com/evernote/evernote-sdk-python
cd evernote-sdk-python
python setup.py install
```

BeautifulSoup4 is the HMTL parser written in Python. The installation steps are the following:
```
pip install beautifulsoup4
```


## CentOS
This section contains the instructions for installing the environment required by Saferoom app. This procedure was tested on **CentOS 7**. Below we assume that everything is done under **root** user. If you're using non-root user, every command should be preceeded by **sudo**

### Checking Python version
Open terminal and check that Python is installed on your system (it should be installed by default, but nevertheless)
```
python --version
```
This application was tested with **Python 2.7** version

### Installing PIP and git

Install Python PIP utility using the following command
```
cd /tmp
curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
python get-pip.py
```

Or

```
yum install epel-release
yum install python-pip
```
After the installation make sure that PIP has been successfully installed
```
pip --version
```

Install GIT client using the following command:
```
yum install git
```

### Installing Flask, Requests and Pycrypto

Saferoom is using [Flask Python microframework](http://flask.pocoo.org/). To install Flask type the following command:
```
pip install flask
```

**Requests** is a [Python module](http://docs.python-requests.org/en/master/) used to work with HTTP requests. TO install this module, type the following command:

```
pip install requests
```

Pycrypto library is needed to perform cryptographic operations (encryption and decryption). Pycrypto is installed using the following command:
```
yum install python-devel
yum install gcc
pip install pycrypto
```

### Installing Evernote Python SDK and BeautifulSoup4

Evernote Python SDK is used to interact with Evernote API. The installation steps are the following:

```
cd /tmp
git clone https://github.com/evernote/evernote-sdk-python
cd evernote-sdk-python
python setup.py install
```

BeautifulSoup4 is the HMTL parser written in Python. The installation steps are the following:
```
pip install beautifulsoup4
```

## Getting started
Now, let's download the Saferoom application and start it on local machine

Clone this repository and start the server:
```
cd ~
git clone https://github.com/saferoom-app/saferoomlinux
cd saferoomlinux
python server.py
```

If everything is ok, you should see the following:
```
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
* Restarting with stat
```

Now open your browser and type the following address:
```
http://127.0.0.1:5000/
```
You should see Saferoom main page

## Generating master password

Before generating the master password, please check [this](http://help.getsaferoom.com/2015/03/28/saferoom-concepts/). 
Summarizing, the **Master password** is the password that you use to encrypt and decrypt your data. This password **is stored on your local PC and never sent anywhere**

**OTP or One-Time password** is the password that is used to encrypt/decrypt specific note. This password can be useful when you want to share the encrypted note with someone you know and you don't want to compromise your **Master password**

Master password is generated using small CLI utility. To generate the master password, please navigate to Saferoom app root folder and type the following:

```
python passwd.py
```

Then follow the intructions

# Evernote
This section contains necessary instructions how to connect Saferoom App to your Evernote account

## Getting developer token
To interact with Evernote API Saferoom app needs the developer token. This token for your specific account can be generated [here](https://www.evernote.com/api/DeveloperToken.action)

If you're not logged in, you need to login with your account. After you receive the developer token, open **config.ini** file in application root folder, find section **[tokens]** and paste your developer token as the following:
```
[tokens]
evernote_developer = <developer_token>
 ...
```
Save **config.ini**, open main Saferoom page and click Evernote icon in the upper-right corner of the page. If everything is OK, then you will see the basic info about your account.

# Onenote
This section contains instructions how to connect Saferoom app to your Onenote account

## Getting Client ID, Client Secret and Redirect URI
Client ID, Client Secret and Redirect URI are required to authtenticate Saferoom app into your Onenote account. 




