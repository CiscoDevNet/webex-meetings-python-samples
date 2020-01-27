# Webex Meetings XML API sample script, demonstrating the following work flow:

#   AuthenticateUser
#   GetUser
#   CreateMeeting
#   LstsummaryMeeting
#   GetMeeting
#   DelMeeting 

# Configuration and setup:

# * Edit .env to provide your Webex user credentials

#   - For SSO/CI sites, provide the ACCESS_TOKEN (retrieve by logging in here: 
#       https://developer.webex.com/docs/api/getting-started)
#   - For non-SSO/CI sites, provide the PASSWORD

#   If both are provided, the sample will attempt to use the ACCESS_TOKEN

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

import requests
import datetime
from lxml import etree
import os

# Edit .env file to specify your Webex site/user details
from dotenv import load_dotenv
load_dotenv()

# Change to true to enable request/response debug output
DEBUG = True

# Once the user is authenticated, the sessionTicket for all API requests will be stored here
sessionSecurityContext = { }

# Custom exception for errors when sending requests
class SendRequestError(Exception):

    def __init__(self, result, reason):
        self.result = result
        self.reason = reason

    pass

# Generic function for sending XML API requests
#   envelope : the full XML content of the request
def sendRequest( envelope ):

    if DEBUG:
        print( envelope )

    # Use the requests library to POST the XML envelope to the Webex API endpoint
    headers = { 'Content-Type': 'application/xml'}
    response = requests.post( 'https://api.webex.com/WBXService/XMLService', envelope )

    # Check for HTTP errors
    try: 
        response.raise_for_status()
    except requests.exceptions.HTTPError as err: 
        raise SendRequestError( 'HTTP ' + str(response.status_code), response.content.decode("utf-8") )

    # Use the lxml ElementTree object to parse the response XML
    message = etree.fromstring( response.content )

    if DEBUG:
        print( etree.tostring( message, pretty_print = True, encoding = 'unicode' ) )   

    # Use the find() method with an XPath to get the 'result' element's text
    # Note: {*} is pre-pended to each element name - ignores namespaces
    # If not SUCCESS...
    if message.find( '{*}header/{*}response/{*}result').text != 'SUCCESS':

        result = message.find( '{*}header/{*}response/{*}result').text
        reason = message.find( '{*}header/{*}response/{*}reason').text

        #...raise an exception containing the result and reason element content
        raise SendRequestError( result, reason )

    return message

def AuthenticateUser( siteName, webExId, password, accessToken ):

    # If an access token is provided in .env, we'll use this form
    if ( accessToken ):
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
    else:
        # If no access token, assume a password was provided, using this form
        request = f'''<?xml version="1.0" encoding="UTF-8"?>
            <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <header>
                    <securityContext>
                        <siteName>{siteName}</siteName>
                        <webExID>{webExId}</webExID>
                        <password>{password}</password>
                    </securityContext>
                </header>
                <body>
                    <bodyContent xsi:type="java:com.webex.service.binding.user.AuthenticateUser"/>
                </body>
            </serv:message>'''

    # Make the API request
    response = sendRequest( request )

    # Return an object containing the security context info with sessionTicket
    return {
            'siteName': siteName,
            'webExId': webExId,
            'sessionTicket': response.find( '{*}body/{*}bodyContent/{*}sessionTicket' ).text
            }

def GetUser( sessionSecurityContext ):

    request = f'''<?xml version="1.0" encoding="UTF-8"?>
        <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <header>
                <securityContext>
                    <siteName>{sessionSecurityContext[ 'siteName' ]}</siteName>
                    <webExID>{sessionSecurityContext[ 'webExId' ]}</webExID>
                    <sessionTicket>{sessionSecurityContext[ 'sessionTicket' ]}</sessionTicket>
                </securityContext>
            </header>
            <body>
                <bodyContent xsi:type="java:com.webex.service.binding.user.GetUser">
                    <webExId>{sessionSecurityContext[ 'webExId' ]}</webExId>
                </bodyContent>
            </body>
        </serv:message>'''

    # Make the API request
    response = sendRequest( request )

    # Return an object containing the response
    return response
    
def CreateMeeting( sessionSecurityContext,
                   meetingPassword,
                   confName,
                   meetingType,
                   agenda,
                   startDate ):

    request = f'''<?xml version="1.0" encoding="UTF-8"?>
        <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <header>
                <securityContext>
                    <siteName>{sessionSecurityContext["siteName"]}</siteName>
                    <webExID>{sessionSecurityContext["webExId"]}</webExID>
                    <sessionTicket>{sessionSecurityContext["sessionTicket"]}</sessionTicket>  
                </securityContext>
            </header>
            <body>
                <bodyContent
                    xsi:type="java:com.webex.service.binding.meeting.CreateMeeting">
                    <accessControl>
                        <meetingPassword>{meetingPassword}</meetingPassword>
                    </accessControl>
                    <metaData>
                        <confName>{confName}</confName>
                        <meetingType>{meetingType}</meetingType>
                        <agenda>{agenda}</agenda>
                    </metaData>
                    <enableOptions>
                        <chat>true</chat>
                        <poll>true</poll>
                        <audioVideo>true</audioVideo>
                        <supportE2E>TRUE</supportE2E>
                        <autoRecord>TRUE</autoRecord>
                    </enableOptions>
                    <schedule>
                        <startDate>{startDate}</startDate>
                        <openTime>900</openTime>
                        <joinTeleconfBeforeHost>false</joinTeleconfBeforeHost>
                        <duration>20</duration>
                        <timeZoneID>4</timeZoneID>
                    </schedule>
                    <telephony>
                        <telephonySupport>CALLIN</telephonySupport>
                        <extTelephonyDescription>
                            Call 1-800-555-1234, Passcode 98765
                        </extTelephonyDescription>
                    </telephony>
                </bodyContent>
            </body>
        </serv:message>'''

    response = sendRequest( request )

    return response

def LstsummaryMeeting( sessionSecurityContext,
    maximumNum,
    orderBy,
    orderAD,
    hostWebExId,
    startDateStart ):

    request = f'''<?xml version="1.0" encoding="UTF-8"?>
        <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <header>
                <securityContext>
                    <siteName>{sessionSecurityContext["siteName"]}</siteName>
                    <webExID>{sessionSecurityContext["webExId"]}</webExID>
                    <sessionTicket>{sessionSecurityContext["sessionTicket"]}</sessionTicket>  
                </securityContext>
            </header>
            <body>
                <bodyContent xsi:type="java:com.webex.service.binding.meeting.LstsummaryMeeting">
                    <listControl>
                        <maximumNum>{maximumNum}</maximumNum>
                        <listMethod>AND</listMethod>
                    </listControl>
                    <order>
                        <orderBy>{orderBy}</orderBy>
                        <orderAD>{orderAD}</orderAD>
                    </order>
                    <dateScope>
                        <startDateStart>{startDateStart}</startDateStart>
                        <timeZoneID>4</timeZoneID>
                    </dateScope>
                    <hostWebExID>{hostWebExId}</hostWebExID>
                </bodyContent>
            </body>
        </serv:message>'''

    response = sendRequest( request )

    return response

def GetMeeting( sessionSecurityContext, meetingKey ):

    request = f'''<?xml version="1.0" encoding="ISO-8859-1"?>
        <serv:message
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:serv="http://www.webex.com/schemas/2002/06/service">
            <header>
                <securityContext>
                    <siteName>{sessionSecurityContext["siteName"]}</siteName>
                    <webExID>{sessionSecurityContext["webExId"]}</webExID>
                    <sessionTicket>{sessionSecurityContext["sessionTicket"]}</sessionTicket>  
                </securityContext>
            </header>
            <body>
                <bodyContent xsi:type="java:com.webex.service.binding.meeting.GetMeeting">
                    <meetingKey>{meetingKey}</meetingKey>
                </bodyContent>
            </body>
        </serv:message>'''

    response = sendRequest( request )

    return response

def DelMeeting( sessionSecurityContext, meetingKey ):

    request = f'''<?xml version="1.0" encoding="ISO-8859-1"?>
        <serv:message
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:serv="http://www.webex.com/schemas/2002/06/service">
            <header>
                <securityContext>
                    <siteName>{sessionSecurityContext["siteName"]}</siteName>
                    <webExID>{sessionSecurityContext["webExId"]}</webExID>
                    <sessionTicket>{sessionSecurityContext["sessionTicket"]}</sessionTicket>  
                </securityContext>
            </header>
            <body>
            <bodyContent xsi:type="java:com.webex.service.binding.meeting.DelMeeting">
                <meetingKey>{meetingKey}</meetingKey>
            </bodyContent>
            </body>
        </serv:message>'''

    response = sendRequest( request )

    return response

if __name__ == "__main__":

    # AuthenticateUser and get sesssionTicket
    try:
        sessionSecurityContext = AuthenticateUser(
            os.getenv( 'SITENAME'),
            os.getenv( 'WEBEXID'),
            os.getenv( 'PASSWORD'),
            os.getenv( 'ACCESS_TOKEN' )
        )

    # If an error occurs, print the error details and exit the script
    except SendRequestError as err:
        print(err)
        raise SystemExit

    print( )
    print( 'Session Ticket:', '\n' )
    print( sessionSecurityContext[ 'sessionTicket' ] )
    print( )

    # Wait for the uesr to press Enter
    input( 'Press Enter to continue...' )

    # GetSite - this will allow us to determine which meeting types are
    # supported by the user's site.  Then we'll parse/save the first type.

    try:
        response = GetUser( sessionSecurityContext )

    except SendRequestError as err:
        print(err)
        raise SystemExit

    meetingType = response.find( '{*}body/{*}bodyContent/{*}meetingTypes')[ 0 ].text
    
    print( )
    print( f'First meetingType available: {meetingType}' )
    print( )

    input( 'Press Enter to continue...' )

    # CreateMeeting - some options will be left out, some hard-coded in the XML
    # and some can be specified with variables

    # Use the datetime package to create a variable for the meeting time, 'now' plus 300 sec
    timestamp = datetime.datetime.now() + datetime.timedelta( seconds = 300 )

    # Create a string variable with the timestamp in the specific format required by the API
    strDate =  timestamp.strftime( '%m/%d/%Y %H:%M:%S' )

    try:
        response = CreateMeeting( sessionSecurityContext,
            meetingPassword = 'C!sco123',
            confName = 'Test Meeting',
            meetingType = meetingType,
            agenda = 'Test meeting creation',
            startDate = strDate )

    except SendRequestError as err:
        print(err)
        raise SystemExit

    print( )
    print( 'Meeting Created:', '\n')
    print( '    Meeting Key:', response.find( '{*}body/{*}bodyContent/{*}meetingkey').text )
    print( )

    input( 'Press Enter to continue...' )

    # LstsummaryMeeting for all upcoming meetings for the user
    try:
        response = LstsummaryMeeting( sessionSecurityContext,
            maximumNum = 10,
            orderBy = 'STARTTIME',
            orderAD = 'ASC',
            hostWebExId = os.getenv('WEBEXID'),
            startDateStart = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') )

    except SendRequestError as err:
        print(err)
        raise SystemExit

    print( )
    print( 'Upcoming Meetings:', '\n')

    print( '{0:22}{1:25}{2:25}'.format( 'Start Time', 'Meeting Name', 'Meeting Key' ) )
    print( '{0:22}{1:25}{2:25}'.format( '-' * 10, '-' * 12, '-' * 11 ) )

    nextMeetingKey = response.find( '{*}body/{*}bodyContent/{*}meeting/{*}meetingKey').text

    for meeting in response.iter( '{*}meeting' ):

        print( '{0:22}{1:25}{2:25}'.format( meeting.find( '{*}startDate' ).text,
            meeting.find( '{*}confName' ).text,
            meeting.find( '{*}meetingKey' ).text ) )

    print( )
    input( 'Press Enter to continue...' )

    try:
        response = GetMeeting( sessionSecurityContext, nextMeetingKey )
    except SendRequestError as err:
        print(err)
        raise SystemError

    print( )
    print( 'Next Meeting Details:', '\n')
    print( '    Meeting Name:', response.find( '{*}body/{*}bodyContent/{*}metaData/{*}confName').text )  
    print( '     Meeting Key:', response.find( '{*}body/{*}bodyContent/{*}meetingkey').text )    
    print( '      Start Time:', response.find( '{*}body/{*}bodyContent/{*}schedule/{*}startDate').text )    
    print( '       Join Link:', response.find( '{*}body/{*}bodyContent/{*}meetingLink').text )    
    print( '        Password:', response.find( '{*}body/{*}bodyContent/{*}accessControl/{*}meetingPassword').text )    

    print( )
    input( 'Press Enter to continue...' )

    try:
        response = DelMeeting( sessionSecurityContext, nextMeetingKey )
    except SendRequestError as err:
        print(err)
        raise SystemError    

    print( )
    print( 'Next Meeting Delete: SUCCESS', '\n')
