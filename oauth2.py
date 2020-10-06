# Webex Meetings OAuth2 sample, demonstrating how to authenticate a
# Webex Meetings OAuth user using Python + Authlib, then use the 
# resulting access token to make a Meetings XML GetUser request

# Note, this sample works with Webex OAuth enabled sites, and uses either:

#   * Webex Teams integration mechanism
#   * Webex Meetings integration mechanism

# Configuration and setup:

#   1. Rename .env.example to .env, and edit with your Webex site name/target 
#        Webex ID (user@email.com)

#   2. Register a Webex Teams OAuth integration per the steps at:

#        * Webex Teams integration mechanism: https://developer.webex.com/docs/integrations
#        * Webex Meetings integration mechanism: https://developer.cisco.com/docs/webex-meetings/#!integration

#        Set the Redirect URL to: https://127.0.0.1:5000/authorize

#        For Webex Teams integration, select the 'spark:all' scope

#   3. Place the integration client_id and client_secret values into .env

#   4. Generate the self-signed certificate used to serve the Flask web app with HTTPS.

#      This requires that OpenSSL tools are installed (the command below was used on Ubuntu Linux 19.04.)

#      From a terminal at the repo root:  

#        openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Launching the app with Visual Studio Code:

#   1. Open the repo root folder with VS Code

#   2. Open the command palette (View/Command Palette), and find 'Python: select interpreter'

#        Select the Python3 interpreter desired (e.g. a 'venv' environment)

#   3. From the Debug pane, select the launch option 'Python: Launch oauth2.py'

#   4. Open a browser and navigate to:  https://127.0.0.1:5000

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

from flask import Flask, url_for, redirect, session, make_response, request
from authlib.integrations.flask_client import OAuth
from lxml import etree
import requests
from furl import furl
import json
import os

# Edit .env file to specify your Webex integration client ID / secret
from dotenv import load_dotenv
load_dotenv( override=True ) # Prefer variables in .env file

# Enable Authlib and API request/response debug output in .env
DEBUG = os.getenv('DEBUG_ENABLED') == 'True'

# Instantiate the Flask application
app = Flask(__name__)

# This key is used to encrypt the Flask user session data store,
# you might want to make this more secret
app.secret_key = "CHANGEME"

# Create an Authlib registry object to handle OAuth2 authentication
oauth = OAuth(app)

# This simple function returns the authentication token object stored in the Flask
# user session data store
# It is used by the webex RemoteApp object below to retrieve the access token when
# making API requests on the session user's behalf
def fetch_token():

    return session[ 'token' ]

# Webex returns no 'token_type' in its /authorize response.
# This authlib compliance fix adds its as 'bearer'
def webex_compliance_fix( session ):

    def _fix( resp ):

        token = resp.json()

        token[ 'token_type' ] = 'bearer'

        resp._content = json.dumps( token ).encode( 'utf-8' )

        return resp

    session.register_compliance_hook('access_token_response', _fix)

# Register a RemoteApplication for the Webex Meetings XML API and OAuth2 service
# The code_challenge_method will cause it to use the PKCE mechanism with SHA256
# The client_kwargs sets the requested Webex Meetings integration scope
# and the token_endpoint_auth_method to use when exchanging the auth code for the
# access token

if ( os.getenv( 'OAUTH_TYPE') == 'MEETINGS' ):
    authUrl = 'https://api.webex.com/v1/oauth2/authorize'
    tokenUrl = 'https://api.webex.com/v1/oauth2/token'
    refreshUrl = 'https://api.ciscospark.com/v1/authorize'
    scopes = 'all_read+user_modify+meeting_modify+recording_modify+setting_modify'
else:
    authUrl = 'https://api.ciscospark.com/v1/authorize'
    tokenUrl = 'https://api.ciscospark.com/v1/access_token'
    refreshUrl = 'https://api.webex.com/v1/oauth2/token'
    scopes = 'spark:all'

if DEBUG:
    import logging
    import sys
    log = logging.getLogger('authlib')
    log.addHandler(logging.StreamHandler(sys.stdout))
    log.setLevel(logging.DEBUG)

oauth.register(

    name = 'webex',
    client_id = os.getenv( 'CLIENT_ID' ),
    client_secret = os.getenv( 'CLIENT_SECRET' ),
    authorize_url = authUrl,
    access_token_url = tokenUrl,
    refresh_token_url = refreshUrl,
    api_base_url = 'https://api.webex.com/WBXService/XMLService',
    client_kwargs = { 
        'scope': scopes,
        'token_endpoint_auth_method': 'client_secret_post' 
    },
    code_challenge_method = 'S256',
    fetch_token = fetch_token,
    compliance_fix=webex_compliance_fix
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
def sendRequest( envelope, debug = False ):

    # Use the webex_meetings RemoteApplication object to POST the XML envelope to the Meetings API endpoint
    # Note, this object is based on the Python requests library object and can accept similar kwargs
    headers = { 'Content-Type': 'application/xml'}
    response = oauth.webex.post( url = '', data = envelope, headers = headers )

    if DEBUG:
        print( response.request.headers )
        print( response.request.body )

    # Check for HTTP errors, if we got something besides a 200 OK
    try: 
        response.raise_for_status()
    except requests.exceptions.HTTPError as err: 
        raise SendRequestError( 'HTTP ' + str(response.status_code), response.content.decode("utf-8") )

    # Use the lxml ElementTree object to parse the response XML
    message = etree.fromstring( response.content )

    # If debug mode has been requested, pretty print the XML to console
    if DEBUG:
        print( response.headers )
        print( etree.tostring( message, pretty_print = True, encoding = 'unicode' ) )   

    # Use the find() method with an XPath to get the <result> element's text
    # Note: {*} is pre-pended to each element name - matches any namespace.
    # If not SUCCESS...
    if message.find( '{*}header/{*}response/{*}result').text != 'SUCCESS':

        result = message.find( '{*}header/{*}response/{*}result').text
        reason = message.find( '{*}header/{*}response/{*}reason').text

        #...raise an exception containing the result and reason element content
        raise SendRequestError( result, reason )

    # Return the XML message
    return message

def WebexAuthenticateUser( siteName, webExId, accessToken ):

    # Use f-string literal formatting to substitute {variables} into the XML string
    request = f'''<?xml version="1.0" encoding="UTF-8"?>
        <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <header>
                <securityContext>
                    <siteName>{siteName}</siteName>
                    <webExID>{webExId}</webExID>
                </securityContext>
            </header>
            <body>
                <bodyContent xsi:type="java:com.webex.service.binding.user.AuthenticateUser">
                    <accessToken>{accessToken}</accessToken>
                </bodyContent>
            </body>
        </serv:message>'''

    # Make the API request
    response = sendRequest( request )

    # Return an object containing the security context info with sessionTicket
    return response.find( '{*}body/{*}bodyContent/{*}sessionTicket' ).text

def WebexGetUser( sessionSecurityContext, webExId ):

    # Use f-string literal formatting to substitute {variables} into the XML template string
    request = f'''<?xml version="1.0" encoding="UTF-8"?>
        <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <header>
                 { sessionSecurityContext }
            </header>
            <body>
                <bodyContent xsi:type="java:com.webex.service.binding.user.GetUser">
                    <webExId>{webExId}</webExId>
                </bodyContent>
            </body>
        </serv:message>
        '''

    # Make the API request
    response = sendRequest( request, debug = True )

    # Return an object containing the security context info with sessionTicket
    return response

# The Flask web app routes start below

# This is the entry point of the app - navigate to https://localhost:5000 to start
@app.route('/')
def login():

    # Create the URL pointing to the web app's /authorize endpoint
    redirect_uri = url_for( 'authorize', _external=True)

    # Use the URL as the destination to receive the auth code, and
    # kick-off the Authclient OAuth2 login flow/GetUser
    return oauth.webex.authorize_redirect( redirect_uri )

# This URL handles receiving the auth code after the OAuth2 flow is complete
@app.route('/authorize')
def authorize():

    # Go ahead and exchange the auth code for the access token
    # and store it in the Flask user session object
    try:
        session[ 'token' ] = oauth.webex.authorize_access_token()

    except Exception as err:

        response = 'Error exchanging auth code for access token:<br>'
        response += f'<ul><li>Error: HTTP { err.code } { err.name }</li>'
        response += f'<li>Description: { err.description }</li></ul>'

        return response, 500        

    # Now that we have the API access token, redirect the the URL for making a
    # Webex Meetings API GetUser request
    return redirect( url_for( 'GetUser' ), code = '302' )

# Make a Meetings API GetUser request and return the raw XML to the browser
@app.route('/GetUser')
def GetUser():

    if ( os.getenv( 'OAUTH_TYPE' ) == 'MEETINGS' ):
        sessionSecurityContext = f'''
            <securityContext>
                <siteName>{ os.getenv( 'SITENAME' ) }</siteName>
                <webExID>{ os.getenv( 'WEBEXID' ) }</webExID>
                <webExAccessToken>{ session[ 'token' ][ 'access_token' ] }</webExAccessToken>
            </securityContext>'''

    else:
        # Call AuthenticateUser to transform the Webex Teams access token into a 
        # Webex Meetings session ticket
        try:
            sessionTicket = WebexAuthenticateUser(
                os.getenv( 'SITENAME' ),
                os.getenv( 'WEBEXID' ),
                session[ 'token' ][ 'access_token' ]
            )

            sessionSecurityContext = f'''
                <securityContext>
                    <siteName>{ os.getenv( 'SITENAME' ) }</siteName>
                    <webExID>{ os.getenv( 'WEBEXID' ) }</webExID>
                    <sessionTicket>{ sessionTicket }</sessionTicket>
                </securityContext>'''

        except SendRequestError as err:

            response = 'Error making AuthenticateUser request:<br>'
            response += '<ul><li>Result: ' + err.result + '</li>'
            response += '<li>Reason: ' + err.reason + '</li></ul>'

            return response, 500

    # Call the function we created above, grabbing siteName and webExId from .env, and the
    # access_token from the token object in the session store
    try:

        reply = WebexGetUser(
            sessionSecurityContext,
            os.getenv( 'WEBEXID' )
        )

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
