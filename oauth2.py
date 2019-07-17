# Webex Meetings OAuth2 sample, demonstrating how to authenticate a
# Webex Meetings OAuth user using Python + Authlib, then use the 
# resulting access token to make a Meetings GetUser request

# Note, this sample only works with Webex OAuth enabled sites;

#   https://api.webex.com/v1/oauth2/authorize
#   https://api.webex.com/v1/oauth2/token
#   GetUser

# Install Python3

#   On Windows, choose the option to add to PATH environment variable

# Script dependencies:

#   requests==2.21.0
#   Authlib==0.11
#   Flask==1.0.2
#   lxml==4.3.3

# Dependency installation (you may need to use `pip3` on Linux or Mac):

#   $ pip3 install -r requirements.txt

# Configuration and setup:

#   1. Edit creds.py with your Webex site name and the target Webex ID (user@email.com)

#   2. Register a Webex OAuth integration per the steps here: 

#        https://developer.cisco.com/docs/webex-meetings/#!integration
#        https://developer.cisco.com/site/webex-integration/
  
#        Be sure to login using the 'Login with Webex Meetings' option.
#        You will need to login as a Webex site admin to create the integration 

#        Set the Redirect URL to: https://localhost:5000/authorize

#        Select the read_all and modify_meetings scopes 
#        (note the actual scope name is meeting_modify)

#   3. Place the integration client_id and client_secret values into creds.py

#   4. Generate the self-signed certificate used to serve the Flask web app with HTTPS.

#      This requires OpenSSL tools be installed (the command below was used on Ubuntu 19.04.)

#      From a terminal at the repo root:  

#        openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Launching the app with Visual Studio Code:

#   1. Open the repo root folder with VS Code

#   2. Edit creds.py as needed (see above)

#   3. Open the command palette (View/Command Palette), and find 'Python: select interpreter'

#        Select the Python 3 interpreter you want (should be the one associated with the pip used above)

#   3. From the debug pane, select the launch option 'Python: Launch oauth2.py'

#   4. Open a browser and navigate to:  https://localhost:5000/login

#  The application will start the OAuth2 flow, then redirect to the /GetUser URL to display the
#  target user's Webex Meetings API details in XML format

# Copyright (c) 2019 Cisco and/or its affiliates.
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from flask import Flask, url_for, redirect, session, make_response
from authlib.flask.client import OAuth
from lxml import etree
import requests

# Edit credentials.py to specify your Webex site/user details
import creds

# Instantiate the Flask application
app = Flask(__name__)

# This key is used to encrypt the Flask user session data store,
# you might want to make this more secret
app.secret_key = "CHANGEME"

# Create an Authlib OAuth object to handle OAuth2 authentication
oauth = OAuth(app)

# This simple function returns the authentication token object stored in the Flask
# user session data store
# It is used by the webex_meetings RemoteApp object below to retrieve the access token when
# making API requests on the session user's behalf
def fetch_token():

    return session[ 'token' ]

# Register a RemoteApplication for the Webex Meetings XML API and OAuth2 service
# The code_challenge_method will cause it to use the PKCE mechanism with SHA256
# The client_kwargs sets the requested Webex Meetings integration scopes (may need to adjust)
# and the token_endpoint_auth_method to use when exchanging the auth code for the
# access token
webex_meetings = oauth.register(

    name = 'webex_meetings',
    client_id = creds.CLIENT_ID,
    client_secret = creds.CLIENT_SECRET,
    access_token_url = 'https://api.webex.com/v1/oauth2/token',
    refresh_token_url = 'https://api.webex.com/v1/oauth2/token',
    authorize_url = 'https://api.webex.com/v1/oauth2/authorize',
    api_base_url = 'https://api.webex.com/WBXService/XMLService',
    client_kwargs = { 'scope': 'all_read meeting_modify',
        'token_endpoint_auth_method': 'client_secret_post' 
        },
    code_challenge_method = 'S256',
    fetch_token=fetch_token
)

# The following section handles the Webex Meetings XML API calls

# Custom exception for errors when sending Meetings API requests
class SendRequestError(Exception):

    def __init__(self, result, reason):
        self.result = result
        self.reason = reason

    pass

# Generic function for sending Meetings XML API requests
#   envelope : the full XML content of the request
#   debug : (optional) print the XML of the request / response
def sendWebexRequest( envelope, debug = False ):

    if debug:
        print( envelope )

    # Use the webex_meetings RemoteApplication object to POST the XML envelope to the Meetings API endpoint
    # Note, this object is based on the Python requests library object and can accept similar kwargs
    headers = { 'Content-Type': 'application/xml'}
    response = webex_meetings.post( url = '', data = envelope, headers = headers )

    # Check for HTTP errors, if we got something besides a 200 OK
    try: 
        response.raise_for_status()
    except requests.exceptions.HTTPError as err: 
        raise SendRequestError( 'HTTP ' + str(response.status_code), response.content.decode("utf-8") )

    # Use the lxml ElementTree object to parse the response XML
    message = etree.fromstring( response.content )

    # If debug mode has been requested, pretty print the XML to console
    if debug:
        print( etree.tostring( message, pretty_print = True, encoding = 'unicode' ) )   

    # Use the find() method with an XPath to get the 'result' element's text
    # Note: {*} is pre-pended to each element name - ignores namespaces
    # If not SUCCESS...
    if message.find( '{*}header/{*}response/{*}result').text != 'SUCCESS':

        result = message.find( '{*}header/{*}response/{*}result').text
        reason = message.find( '{*}header/{*}response/{*}reason').text

        #...raise an exception containing the result and reason element content
        raise SendRequestError( result, reason )

    # Return the XML message
    return message

def WebexGetUser( siteName, webExId, webExAccessToken, debug = False):

    # Use string literal formatting to substitute {variables} into the XML template string
    # Note using <webExAccessToken> instead of <password>
    request = '''<?xml version="1.0" encoding="UTF-8"?>
        <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <header>
                <securityContext>
                    <siteName>{siteName}</siteName>
                    <webExID>{webExId}</webExID>
                    <webExAccessToken>{webExAccessToken}</webExAccessToken>  
                </securityContext>
            </header>
            <body>
                <bodyContent xsi:type="java:com.webex.service.binding.user.GetUser">
                    <webExId>{webExId}</webExId>
                </bodyContent>
            </body>
        </serv:message>
        '''.format( siteName = siteName, webExId = webExId, webExAccessToken = webExAccessToken )

    # Make the API request
    response = sendWebexRequest( request, debug )

    # Return an object containing the security context info with sessionTicket
    return response

# The Flask web app routes start below

# This is the entry point of the app - navigate to https://localhost:5000/login to start
@app.route('/login')
def login():

    # Create the URL pointing to the web app's /authorize endpoint
    redirect_uri = url_for('authorize', _external=True)

    # Use the URL as the destination to receive the auth code, and
    # kick-off the Authclient OAuth2 login flow
    return webex_meetings.authorize_redirect(redirect_uri)

# This URL handles receiving the auth code after the OAuth2 flow is complete
@app.route('/authorize')
def authorize():

    # Go ahead and exchange the auth code for the access token
    # and store it in the user session object
    try:
        session['token'] = webex_meetings.authorize_access_token()

    except Exception as err:

        response = 'Error exchanging auth code for access token:<br>'
        response += '<ul><li>Error: ' + err.error + '</li>'
        response += '<li>Description: ' + err.description + '</li></ul>'

        return response, 500        

    # Now that we have the API access token, redirect the the URL for making a
    # Webex Meetings API GetUser request
    return redirect(url_for('GetUser'), code='302')

# Make a Meetings API GetUser request and return the raw XML to the browser
@app.route('/GetUser')
def GetUser():

    # Call the function we created above, grabbing siteName and webExId from creds.py, and the
    # access_token from the token object in the session store
    try:

        reply = WebexGetUser( creds.SITENAME_OAUTH, creds.WEBEXID_OAUTH, session[ 'token' ][ 'access_token' ], debug = False )

    except SendRequestError as err:

        response = 'Error making Webex Meeting API request:<br>'
        response += '<ul><li>Result: ' + err.result + '</li>'
        response += '<li>Reason: ' + err.reason + '</li></ul>'

        return response, 500

    # Create a Flask Response object, with content of the pretty-printed XML text
    response = make_response( etree.tostring( reply, pretty_print = True, encoding = 'unicode' ) )
    # Mark the response as XML via the Content-Type header
    response.headers[ 'Content-Type' ] = 'application/xml'

    return response
