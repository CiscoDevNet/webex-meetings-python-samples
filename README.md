# webex-meetings-api-samples

## Overview

This project contains sample scripts demonstrating usage of the Webex Meetings API, using Python

https://developer.cisco.com/webex-meetings/

The concepts and techniques shown can be extended to enable automated management of Webex Meetings features

Also included is a Postman collection covering the requests used in the sample.

## Getting started

* Install Python 3:

    On Windows, choose the option to add to PATH environment variable

* Clone this repo:

    ```bash
    git clone https://github.com/CiscoDevNet/webex-meetings-python-samples
    cd webex-meetings-python-samples
    ```

* Dependency Installation (you may need to use `pip3` on Linux or Mac)

    ```bash
    pip install -r requirements.txt
    ```
  
* Edit creds.py to specify your Webex credentials

* See the comments in the individual samples for specific setup/launch details

## Available samples

* `sampleFlow.py` - demonstrates the following work flow:

    * AuthenticateUser
    * CreateMeeting
    * LstsummaryMeeting
    * GetMeeting
    * DelMeeting 

* `oauth2.py` - demonstrates a web application that can perform a Webex Meetings OAuth2 login (using [Authlib](https://github.com/lepture/authlib)), then perform a GetUser request

* `Postman collection - Webex Meetings XML API.json` - import this [Postman collection](https://learning.getpostman.com/docs/postman/collections/intro_to_collections/)] which contains select scripted API request samples
