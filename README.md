# webex-meetings-api-samples

## Overview

This project contains sample scripts demonstrating usage of the Webex Meetings API, using Python

https://developer.cisco.com/webex-meetings/

The concepts and techniques shown can be extended to enable automated management of Webex Meetings features

Also included is a Postman collection covering the requests used in the sample.

## Getting started

* Install Python 2.7 or 3.7
  On Windows, choose the option to add to PATH environment variable

* Script Dependencies:

    * lxml
    * requests

* Dependency Installation (you may need to use `pip3` on Linux or Mac)

    ```
    $ pip install lxml
    ```
  
* Edit creds.py to specify your Webex site name, and user credentials


## Available samples

* `sampleFlow.py` - demonstrates the following work flow:

    * AuthenticateUser
    * CreateMeeting
    * LstsummaryMeeting
    * GetMeeting
    * DelMeeting 