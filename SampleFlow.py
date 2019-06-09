import requests
import datetime
from lxml import etree

SITENAME = 'apidemoeu'
WEBEXID = 'dstaudt'
PASSWORD = 'Horseface12.'

sessionSecurityContext = { }

class SendRequestError(Exception):

    def __init__(self, result, reason):
        self.result = result
        self.reason = reason

    pass

def sendRequest( envelope, debug = False ):

    if debug:
        print( envelope )

    headers = { 'Content-Type': 'application/xml'}
    response = requests.post( 'https://api.webex.com/WBXService/XMLService', envelope )

    try: 
        response.raise_for_status()
    
    except requests.exceptions.HTTPError as err: 
        raise SendRequestError( 'HTTP ' + response.status_code, response.conent )

    message = etree.fromstring( response.content )

    if debug:
        print( etree.tostring( message, pretty_print = True, encoding = 'unicode' ) )   

    if message.find( '{*}header/{*}response/{*}result').text != 'SUCCESS':

        result = message.find( '{*}header/{*}response/{*}result').text
        reason = message.find( '{*}header/{*}response/{*}reason').text

        raise SendRequestError( result, reason )

    return message

def AuthenticateUser( siteName, webExId, password, debug = False):

    request = '''<?xml version="1.0" encoding="UTF-8"?>
        <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <header>
                <securityContext>
                    <siteName>{0}</siteName>
                    <webExID>{1}</webExID>
                    <password>{2}</password>  
                </securityContext>
            </header>
            <body>
                <bodyContent xsi:type="java:com.webex.service.binding.user.AuthenticateUser">
                </bodyContent>
            </body>
        </serv:message>
        '''.format( siteName, webExId, password )

    response = sendRequest( request )

    return {
            'siteName': siteName,
            'webExId': webExId,
            'sessionTicket': response.find( '{*}body/{*}bodyContent/{*}sessionTicket' ).text
            }

def CreateMeeting( sessionSecurityContext,
                   meetingPassword,
                   confName,
                   meetingType,
                   agenda,
                   startDate,
                   debug = False ):

    request = '''<?xml version="1.0" encoding="UTF-8"?>
        <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <header>
                <securityContext>
                    <siteName>{siteName}</siteName>
                    <webExID>{webExId}</webExID>
                    <sessionTicket>{sessionTicket}</sessionTicket>  
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
                        <joinTeleconfBeforeHost>true</joinTeleconfBeforeHost>
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
        </serv:message>
        '''.format( siteName = sessionSecurityContext['siteName'],
                    webExId = sessionSecurityContext['webExId'],
                    sessionTicket = sessionSecurityContext['sessionTicket'],
                    meetingPassword = meetingPassword,
                    confName = confName,
                    meetingType = meetingType,
                    agenda = agenda,
                    startDate = startDate )

    response = sendRequest( request, debug = False )

    return response

def LstsummaryMeeting( sessionSecurityContext,
    maximumNum,
    orderBy,
    orderAD,
    hostWebExId,
    startDateStart,
    debug = False ):

    request = '''<?xml version="1.0" encoding="UTF-8"?>
        <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <header>
                <securityContext>
                    <siteName>{siteName}</siteName>
                    <webExID>{webExId}</webExID>
                    <sessionTicket>{sessionTicket}</sessionTicket>  
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
        </serv:message>
        '''.format( siteName = sessionSecurityContext['siteName'],
            webExId = sessionSecurityContext['webExId'],
            sessionTicket = sessionSecurityContext['sessionTicket'],
            maximumNum = maximumNum,
            orderBy = orderBy,
            orderAD = orderAD,
            hostWebExId = hostWebExId,
            startDateStart = startDateStart )

    response = sendRequest( request, debug = False )

    return response

def GetMeeting( sessionSecurityContext, meetingKey, debug = False ):

    request = '''<?xml version="1.0" encoding="ISO-8859-1"?>
        <serv:message
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:serv="http://www.webex.com/schemas/2002/06/service">
            <header>
                <securityContext>
                    <siteName>{siteName}</siteName>
                    <webExID>{webExId}</webExID>
                    <sessionTicket>{sessionTicket}</sessionTicket>
                </securityContext>
            </header>
            <body>
                <bodyContent xsi:type="java:com.webex.service.binding.meeting.GetMeeting">
                    <meetingKey>{meetingKey}</meetingKey>
                </bodyContent>
            </body>
        </serv:message>
        '''.format( siteName = sessionSecurityContext['siteName'],
            webExId = sessionSecurityContext['webExId'],
            sessionTicket = sessionSecurityContext['sessionTicket'],
            meetingKey = meetingKey )

    response = sendRequest( request, debug = False )

    return response

def DelMeeting( sessionSecurityContext, meetingKey, debug = False ):

    request = '''<?xml version="1.0" encoding="ISO-8859-1"?>
        <serv:message
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:serv="http://www.webex.com/schemas/2002/06/service">
            <header>
                <securityContext>
                    <siteName>{siteName}</siteName>
                    <webExID>{webExId}</webExID>
                    <sessionTicket>{sessionTicket}</sessionTicket>
                </securityContext>
            </header>
            <body>
            <bodyContent xsi:type="java:com.webex.service.binding.meeting.DelMeeting">
                <meetingKey>{meetingKey}</meetingKey>
            </bodyContent>
            </body>
        </serv:message>
        '''.format( siteName = sessionSecurityContext['siteName'],
            webExId = sessionSecurityContext['webExId'],
            sessionTicket = sessionSecurityContext['sessionTicket'],
            meetingKey = meetingKey )

    response = sendRequest( request, debug = False )

    return response

if __name__ == "__main__":

    # AuthenticateUser and get sesssionTicket
    try:
        sessionSecurityContext = AuthenticateUser( SITENAME, WEBEXID, PASSWORD)

    except SendRequestError as err:
        print(err)
        raise SystemExit

    print( )
    print( 'Session Ticket:', '\n' )
    print( sessionSecurityContext[ 'sessionTicket' ] )
    print( )

    input( 'Press Enter to continue...' )

    # CreateMeeting with some sample settings, with StartDate of 'now'

    timestamp = datetime.datetime.now() + datetime.timedelta(seconds=60) #now + 60 sec
    strDate =  timestamp.strftime('%m/%d/%Y %H:%M:%S')

    try:
        response = CreateMeeting( sessionSecurityContext,
            meetingPassword = 'C!sco123',
            confName = 'Test Meeting',
            meetingType = '105',
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
            hostWebExId = WEBEXID,
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
    print( 'Next Meeting Delete: SUCCESS:', '\n')
