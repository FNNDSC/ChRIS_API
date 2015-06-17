#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""

 _____ _    ______ _____ _____   _   _ _ _
/  __ \ |   | ___ \_   _/  ___| | | | | | |
| /  \/ |__ | |_/ / | | \ `--.  | | | | | |_ _ __ ___  _ __
| |   | '_ \|    /  | |  `--. \ | | | | | __| '__/ _ \| '_ \
| \__/\ | | | |\ \ _| |_/\__/ / | |_| | | |_| | | (_) | | | |
 \____/_| |_\_| \_|\___/\____/   \___/|_|\__|_|  \___/|_| |_|



font generated by:
http://patorjk.com/software/taag/#p=display&f=Doom&t=ChRIS%20Ultron

ChRIS_SM

'ChRIS_SM' is the 'ChRIS Simulated Machine' or 'ChRIS Simple Machine'
or ... :-) -- basically it is a simplified infrastructure for
developing / testing the API between the front end view and various
back-end services.

Essentially, 'ChRIS_SM' simulates the API behaviour on a synthetic
instance of ChRIS consisting of a single user (with password) and
a few feeds containing different data, views, results, notes, etc.


"""

from __future__ import print_function

import crun
import hashlib
import sys
import os
import argparse
import json

class ChRIS_client(object):
    """Simple class that handles comms between a back end ChRIS_SM

    """

    callCounter     = 0

    def __init__(self, **kwargs):
        """Constructor
        """
        self._str_executable    = ""
        self._str_stateFile     = ""

        self._str_token         = ""
        self._str_seed          = ""

        self._b_formatAllJSON   = False

        self._shell             = crun.crun()
        self._shell.waitForChild(True)
        self._shell.echoStdOut(False)
        self._shell.echoStdErr(False)
        self._shell.echo(False)

        for key, val in kwargs.iteritems():
            if key == "stateMachine":   self._str_executable    = val
            if key == "stateFile":      self._str_stateFile     = val
            if key == "formatAllJSON":  self._b_formatAllJSON   = val

    def __call__(self, *args, **kwargs):
        """Entry point mimicking the external call to the web service
        """
        str_jwrap       = ""
        b_jwrapStart    = False
        b_jwrapEnd      = False
        for key, val in kwargs.iteritems():
            if key == "jwrap" and val == "start":   b_jwrapStart    = True
            if key == "jwrap" and val == "end":     b_jwrapEnd      = True

        ChRIS_client.callCounter += 1

        if self._b_formatAllJSON:
            if b_jwrapStart:
                print("{\"call_%03d\": " % ChRIS_client.callCounter, end="")
            else:
                print(",\"call_%03d\": " % ChRIS_client.callCounter, end="")

        self._shell("%s --APIcall %s --stateFile %s" % (self._str_executable, args[0], self._str_stateFile))
        # print(self.stdout())
        # print(json.dumps(self.stdout()))
        # print(json.dumps(self.stdout(), sort_keys = True,
        #       indent=4, separators=(',', ': ')))
        job = eval(self.stdout())
        # print("vvvv")
        print(json.dumps(job), end="")
        # print("^^^^")
        if self._b_formatAllJSON and b_jwrapEnd:
            print("}")

    def stdout(self):
        return self._shell.stdout()

    def generateToken(self, jsonRetString):
        """Determines the token to use in the next API call

        Args:
            jsonRetString:  The JSON payload returned from the call to the web service

        Returns:
            str_token:  The token to use for the next API call.

        :param jsonRetString:
        :return:
        """
        jdata   = json.loads(jsonRetString)
        for key,val in jdata.iteritems():
            if key == 'token':  self._str_token = val
            if key == 'seed':   self._str_token = val
        str_hashInput   = "%s%s" % (self._str_token, self._str_seed)
        return m.md5(str_hash).hexdigest()

def synopsis(ab_shortOnly = False):
    scriptName = os.path.basename(sys.argv[0])
    shortSynopsis =  '''
    SYNOPSIS

            %s --stateFile <stateFile> [--formatAllJSON]


    ''' % scriptName

    description =  '''
    DESCRIPTION

        `%s' shows client side connection to the ChRIS_SM API service.

    ARGS

       --stateFile <stateFile> (required)
       The file that tracks calls pertinent to a specific session.
       API calls are logged to <stateFile> and replayed back when
       ChRIS_SM is instantiated. In this manner the machine state
       can be rebuilt. The current <apiCall> is appended to the
       <stateFile>.

       --formatAllJSON
       If specified, format the entire set of output responses as a "meta"
       JSON string. Useful for downstream parsing with "|python -m json.tool"

    EXAMPLES


    ''' % (scriptName)
    if ab_shortOnly:
        return shortSynopsis
    else:
        return shortSynopsis + description


if __name__ == "__main__":
    """Simulated session interacting with the ChRIS_SM

    This module simulates an external client communicating with the
    back end.

    """

    if len(sys.argv) == 1:
        print(synopsis())
        sys.exit(1)

    parser      = argparse.ArgumentParser(description = synopsis(True))
    parser.add_argument(
        '-s', '--stateFile',
        help    =   "The <stateFile> keeps track of ChRIS state.",
        dest    =   'str_stateFileName',
        action  =   'store',
        default =   "<void>"
    )
    parser.add_argument(
        '-f', '--formatAllJSON',
        help    =   "If specified, wrap *all* output in a JSON object, useful for downsteam parsing.",
        dest    =   'formatAllJSON',
        action  =   'store_true',
        default =   False
    )

    args        = parser.parse_args()
    m           = hashlib
    API         = ChRIS_client(stateMachine = './ChRIS_SM.py',  stateFile       = args.str_stateFileName,
                                                                formatAllJSON   = args.formatAllJSON)

    # First login...
    API("\"http://chris_service?returnstore=d&object=chris&method=login&parameters=user='chris',passwd='chris1234'&clearSessionFile=1\"",jwrap="start")

    # Now do something...

    # Get a list of feeds for the homepage
    API("\"http://chris_service?object=chris.homePage&method=feeds_organize&parameters=schema='default',returnAsDict=True&auth=user='chris',hash='dabcdef1234'\"")

    # Get details about specific feeds
    API("\"http://chris_service?object=chris.homePage&method=feed_getFromObjectName&parameters='Feed-3',returnAsDict=True&auth=user='chris',hash='dabcdef1234'\"")

    API("\"http://chris_service?object=chris.homePage&method=feed_getFromObjectName&parameters='Feed-2',returnAsDict=True&auth=user='chris',hash='dabcdef1234'\"",jwrap="end")

