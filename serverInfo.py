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

This module maintains information and methods relevant to the hosting server.

"""

import sys
import os
import argparse
import json

class serverInfo(object):
    """
    A simple object that contains information and methods relevant to the hosting server:

        * IP
        * port
        * SSL
        * etc
    """

    def __init__(self, **kwargs):
        """
        Initialize the class.
        :param kwargs: hostURL=<hostIP[:port]>
        :return:
        """

        self.scheme         = ""
        self.authority      = ""
        self.hostname       = ''
        self.port           = ""
        self.APIversion     = 'v1'

        self.URI            = ""
        self.URI_set(**kwargs)

    def internals_set(self, **kwargs):
        """
        Set the internal class variables based on the pattern of passed kwargs
        :param kwargs:
        :return:
        """
        for key,val in kwargs.iteritems():
            if key == 'scheme':     self.scheme     = val
            if key == 'authority':  self.authority  = val
            if key == 'hostname':   self.hostname   = val
            if key == 'port':       self.port       = val

        if not len(self.scheme):
            self.scheme = "http"

        if len(self.authority):
            l_hostport  = self.authority.split(":")
            self.hostname   = l_hostport[0]
            if len(l_hostport) >= 2:
                self.port   = l_hostport[1]
            else: self.port = 80

        if len(self.hostname) and not len(self.authority):
            if len(self.port):
                self.authority = "%s:%s" % (self.hostname, self.port)
            else:
                self.authority = self.hostname

        self.URI        = "%s://%s" % (self.scheme, self.authority)

    def __iter__(self):
        """
        An iterator over object internals
        :return: an iterator used to create dictionaries
        """

        yield('scheme',     self.scheme)
        yield('authority',  self.authority)
        yield('hostname',   self.hostname)
        yield('port',       self.port)
        yield('URI',        self.URI)

    def __str__(self):
        """
        A string representation of the object
        :return: A string representation of the object
        """

        d_str   = dict(self)
        return json.dumps(d_str)


    def URI_set(self, **kwargs):
        """
        Compose the URL of the server.
        :return: the URL of the server
        """
        self.internals_set(**kwargs)
        return self.URI


def synopsis(ab_shortOnly = False):
    scriptName = os.path.basename(sys.argv[0])
    shortSynopsis =  '''
    SYNOPSIS

            %s [--host <hostIP | hostName>] [--port <port>] [--authority <authority>]


    ''' % scriptName

    description =  '''
    DESCRIPTION

        `%s' sets and maintains server-side information.

    ARGS

        --authority <authority>
        The authority.

        --host <hostIP | hostName> [--port <port>]
        An explicit authority by specifying the host and port separately.


    ''' % (scriptName)
    if ab_shortOnly:
        return shortSynopsis
    else:
        return shortSynopsis + description

if __name__ == "__main__":
    """
    Simple calling/instantiation of module/object
    """

    if len(sys.argv) == 1:
        print(synopsis())
        sys.exit(1)

    parser      = argparse.ArgumentParser(description = synopsis(True))
    parser.add_argument(
        '-a', '--authority',
        help    =   "The <authority> field.",
        dest    =   'authority',
        action  =   'store',
        default =   ""
    )
    parser.add_argument(
        '-n', '--hostname',
        help    =   "The <host> field.",
        dest    =   'hostname',
        action  =   'store',
        default =   ""
    )
    parser.add_argument(
        '-p', '--port',
        help    =   "The <port> field.",
        dest    =   'port',
        action  =   'store',
        default =   ""
    )

    args        = parser.parse_args()

    server      = serverInfo(
        authority   = args.authority,
        hostname    = args.hostname,
        port        = args.port
    )

    print(server)
