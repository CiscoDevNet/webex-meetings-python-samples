# webex-meetings-api-samples

## Overview

This project contains sample scripts demonstrating usage of the Webex Meetings API, using Python.

https://developer.cisco.com/webex-meetings/

The concepts and techniques shown can be extended to enable automated management of Webex Meetings features.

Also included is a Postman collection covering the requests used in the sample.

Samples built/tested using [Visual Studio Code](https://code.visualstudio.com/).

## Available samples

* `sampleFlow.py` - demonstrates the following work flow:

    * AuthenticateUser
    * GetUser
    * CreateMeeting
    * LstsummaryMeeting
    * GetMeeting
    * DelMeeting 

    Can use webExId/password or webExId/accessToken for authorization

* `oauth2.py` - demonstrates a web application that can perform a Webex Meetings OAuth2 login (using [Authlib](https://github.com/lepture/authlib)), then performs a GetUser request.  Can use either [Webex Meetings OAuth](https://developer.cisco.com/docs/webex-meetings/#!integration) or [Webex Teams OAuth](https://developer.webex.com/docs/integrations) providers.

* `Postman collection - Webex Meetings XML API.json` - import this [Postman collection](https://learning.getpostman.com/docs/postman/collections/intro_to_collections/) which contains select scripted API request samples

## Webex environments

* **Full site** - For full admin access and complete features, a production Webex instance is best.  Some samples require site admin credentials

* **Trial site** - The next best thing is to request a [free Webex trial](https://www.webex.com/pricing/free-trial.html) which should provide you admin access and lots of features to try

* **DevNet Webex Sandbox** - For instant/free access, you can create an end-user account in the [DevNet Webex Sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/b0547ab9-20cd-4a2d-a817-5c3b76258c83?diagramType=Topology).  Note, this instance is non-SSO/CI, and uses username/password authentication

## Getting started

* Install Python 3:

    On Windows, choose the option to add to PATH environment variable

* From a terminal, clone this repo and change into the directory:

    ```bash
    git clone https://github.com/CiscoDevNet/webex-meetings-python-samples
    cd webex-meetings-python-samples
    ```

* (Optional but recommended) Create a Python virtual environment named `venv`:

    (you may need to use `python3` on Linux/Mac):

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

* Dependency Installation (you may need to use `pip3` on Linux/Mac)

    ```bash
    pip install -r requirements.txt
    ```

* Open the project in Visual Studio Code:

    ```bash
    code .
    ```

* In VS Code:

    1. Rename `.env.example` to `.env`

        Edit `.env` to specify your Webex credentials

    1. Click on the Debug tab, then the Launch configurations drop-down in the upper left.

        Select the sample you wish to run, e.g. 'Python: Launch sampleFlow.py`

    1. See comments in the individual samples for additional sample-specific setup/launch details

    1. Click the green **Start Debugging** button

