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
"""

str_desc = """

 _____ _    ______ _____ _____  _    _ _____
/  __ \ |   | ___ \_   _/  ___|| |  | /  ___|
| /  \/ |__ | |_/ / | | \ `--. | |  | \ `--.
| |   | '_ \|    /  | |  `--. \| |/\| |`--. \\
| \__/\ | | | |\ \ _| |_/\__/ /\  /\  /\__/ /
 \____/_| |_\_| \_|\___/\____/  \/  \/\____/
                           ______
                          |______|

'ChRIS_WS' is a simple server that parses raw socket input for the
/GET /xxx HTTP/ string, dispatches this to a ChRIS_SM instance,
parses the resultant stdout, and transmits this back to the caller.

Parts of the server infrastructure were adapted from:
http://thomasfischer.biz/python-simple-json-tcp-server-and-client/
"""

from    webob           import Response
from    urlparse        import urlparse, parse_qs

import  crun
import  SocketServer
import  json
import  argparse
import  os
import  sys
import  datetime


class TCPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True

class TCPServerHandler(SocketServer.BaseRequestHandler):

    def URL_clientParamsPOST(self, al_inputRaw):
        """ Returns the string of client parameters embedded in the URL.

            This method handles POST calls from client.

            Args:
                al_inputRaw (list): The raw socket data as list split on '\n'

            Returns:
                a string of client parameters.
        """
        return "?" + al_inputRaw[7]

    def URL_clientParamsGET(self, al_inputRaw):
        """ Returns the string of client parameters embedded in the URL.

            This method handles GET calls from client.

            Args:
                al_inputRaw (list): The raw socket data as list split on '\n'

            Returns:
                a string of client parameters.
        """
        str_GET         = al_inputRaw[0]
        l_URLargSpec    = str_GET.split('/')
        str_URLargs     = l_URLargSpec[1].split()[0]
        return str_URLargs

    def URL_serverProcess(self, astr_URLargs, astr_sessionFile):
        """Call the server side entry point with the URLargs and sessionFile.

        Args:
            astr_URLargs (string):      The string of data from client.
            astr_sessionFile (string):  The sessionFile to use.

        Returns:
            string response from server process
        """
        shell = crun.crun()
        shell.waitForChild(True)
        shell.echoStdOut(True)
        shell.echoStdErr(True)
        shell.echo(False)

        print("astr_URLargs     = %s" % astr_URLargs)
        print("astr_sessionFIle = %s" % astr_sessionFile)
        shell('ChRIS_SM.py --APIcall \"%s\" --stateFile %s' % (astr_URLargs, astr_sessionFile))
        #return {'message' : 'ok'}
        return eval(shell.stdout())

    def HTTPresponse_sendClient(self, str_payload, **kwargs):
        """Send a properly formed HTTP response back to the client.
        """

        str_contentType = "text/html"
        for key, val in kwargs.iteritems():
            if key == "ContentType":   str_contentType = val

        res  = Response(str_payload)
        res.content_type = str_contentType

        str_HTTPpre = "HTTP 1.1 "
        str_res     = "%s %s" % (str_HTTPpre, str(res))

        #print(str_res)
        return str_res

    def handle(self):
        str_raw         = self.request.recv(1024).strip()
        now             = datetime.datetime.today()
        str_timeStamp   = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        print("%s incoming data stream\n%s\n" % (str_timeStamp, str_raw) )
        l_raw       = str_raw.split('\n')
        print(l_raw)
        FORMtype    = l_raw[0].split('/')[0]
        str_URLargs = eval('self.URL_clientParams%s(l_raw)' % FORMtype)

        # process the data:
        d_component     = parse_qs(urlparse(str_URLargs).query)
        print(d_component)
        str_sessionFile = d_component['sessionFile'][0]
        print('sessionFile = %s\n' % str_sessionFile)
        str_reply       = self.URL_serverProcess(str_URLargs, str_sessionFile)
        print(str_reply)
        try:
            self.request.sendall(self.HTTPresponse_sendClient(json.dumps(str_reply),
                                                              ContentType = 'application/json'))
        except Exception, e:
            print "Exception while attempting to transmit receive message: ", e

def synopsis(ab_shortOnly = False):
    scriptName = os.path.basename(sys.argv[0])
    shortSynopsis =  '''
    SYNOPSIS

            %s                                     \\
                            --port <port>


    ''' % scriptName

    description =  '''
    DESCRIPTION

        `%s' is a thin server that connects a web browser
        to the ChRIS_SM.py machine.

        It essentially parses the raw URL inputs, then calls
        the ChRIS_SM.py, and returns JSON data back to the caller.

    ARGS

       --port <port> (defaults to '5555')
       The port for the server to listen on.

    EXAMPLES


    ''' % (scriptName)
    if ab_shortOnly:
        return shortSynopsis
    else:
        return shortSynopsis + description


if __name__ == "__main__":
    """Start the server on arbitrary port.
    """

    parser  = argparse.ArgumentParser(description = synopsis(True))
    parser.add_argument(
        '-p', '--port',
        help    =   "The <port> on which to listen.",
        dest    =   'port',
        action  =   'store',
        default =   5555
    )

    args = parser.parse_args()

    print(str_desc)
    print('Starting Simple ChRIS Web Service on port %s.' % args.port)
    print('To exit/kill this server, hit <ctrl>-c.\n')
    print("Send GET/POST requests to the service port.")
    server = TCPServer(('127.0.0.1', args.port), TCPServerHandler)
    server.serve_forever()